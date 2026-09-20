// Protocol logic of the browser interviewer engine, fed with fake server
// messages. No network, no audio. Run: node --test tests/mock_engine.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { GeminiLive, Transcript } from "../mock/app/live.js";
import { buildInterviewerInstructions, languageNote } from "../mock/app/interviewer.js";

function engine(extra = {}) {
  const seen = { transcript: [], events: [], audio: 0, interrupted: 0, status: [] };
  const live = new GeminiLive({
    apiKey: "test",
    instructions: () => "SYS",
    onTranscript: (u, done) => seen.transcript.push([u.who, u.text, done]),
    onEvent: (n, d) => seen.events.push([n, d]),
    onAudio: () => seen.audio++,
    onInterrupted: () => seen.interrupted++,
    onStatus: (s) => seen.status.push(s),
    ...extra,
  });
  const sent = [];
  live._sendJson = (p) => sent.push(p);
  return { live, seen, sent };
}

test("setupComplete marks live and nudges the interviewer to speak first", () => {
  const { live, seen, sent } = engine();
  live._handle({ setupComplete: {} });
  assert.equal(live.connected, true);
  assert.deepEqual(seen.status, ["live"]);
  assert.equal(sent.length, 1);
  assert.match(sent[0].clientContent.turns[0].parts[0].text, /just joined/);
  assert.equal(sent[0].clientContent.turnComplete, true);
});

test("candidate speech, interviewer speech and audio flow into the transcript", () => {
  const { live, seen } = engine();
  live._handle({ setupComplete: {} });
  live._handle({ serverContent: { inputTranscription: { text: "I worked on " } } });
  live._handle({ serverContent: { inputTranscription: { text: "payments." } } });
  live._handle({ serverContent: { outputTranscription: { text: "Okay. " }, modelTurn: { parts: [{ inlineData: { mimeType: "audio/pcm;rate=24000", data: "AAAA" } }] } } });
  live._handle({ serverContent: { outputTranscription: { text: "Which gateway?" } } });
  live._handle({ serverContent: { turnComplete: true } });
  assert.equal(seen.audio, 1);
  const turns = live.transcript.turns;
  assert.deepEqual(turns.map((u) => [u.who, u.text]), [["candidate", "I worked on payments."], ["interviewer", "Okay. Which gateway?"]]);
  // The candidate's line is final the moment the interviewer starts; the
  // interviewer's line is final at turnComplete.
  const finals = seen.transcript.filter(([, , done]) => done);
  assert.deepEqual(finals, [["candidate", "I worked on payments.", true], ["interviewer", "Okay. Which gateway?", true]]);
});

test("interrupted closes the interviewer utterance and clears the speaker", () => {
  const { live, seen } = engine();
  live._handle({ setupComplete: {} });
  live._handle({ serverContent: { outputTranscription: { text: "Tell me about a time when" } } });
  live._handle({ serverContent: { interrupted: true } });
  assert.equal(seen.interrupted, 1);
  const u = live.transcript.turns[0];
  assert.equal(u.interrupted, true);
  assert.match(live.transcript.asContext(), /\[cut off\]/);
});

test("reconnect nudge asks to continue, not to greet, and carries the transcript", () => {
  const { live, sent } = engine();
  live._handle({ setupComplete: {} });
  live._handle({ serverContent: { outputTranscription: { text: "Hi, tell me about yourself." }, turnComplete: true } });
  live.connected = false;                     // socket dropped
  live._handle({ setupComplete: {} });        // fresh session
  assert.equal(live.sessions, 2);
  assert.match(sent.at(-1).clientContent.turns[0].parts[0].text, /reconnected/);
  const setup = live._setupMessage().setup;
  assert.match(setup.systemInstruction.parts[0].text, /^SYS[\s\S]*INTERVIEW SO FAR[\s\S]*tell me about yourself/);
  assert.deepEqual(setup.generationConfig.responseModalities, ["AUDIO"]);
  assert.ok("inputAudioTranscription" in setup && "outputAudioTranscription" in setup);
});

test("usage totals accumulate across messages", () => {
  const { live } = engine();
  live._handle({ usageMetadata: { promptTokenCount: 10, responseTokenCount: 5, totalTokenCount: 15 } });
  live._handle({ usageMetadata: { promptTokenCount: 1, responseTokenCount: 1, totalTokenCount: 2 } });
  assert.deepEqual(live.usage, { promptTokenCount: 11, responseTokenCount: 6, totalTokenCount: 17 });
});

test("stall watchdog fires only when connected, past grace, voiced recently and server silent", () => {
  const { live, seen } = engine();
  let closed = 0;
  live.ws = { close: () => closed++ };
  live._handle({ setupComplete: {} });
  const t = performance.now() / 1000;
  live._connectedAt = t - 60; live._lastVoiced = t - 2; live._lastServer = t - 30;
  live._checkStall();
  assert.equal(closed, 1);
  assert.ok(seen.events.some(([n]) => n === "stall_detected"));
  // Not while the server answered recently.
  live.connected = true; closed = 0; live._lastServer = t - 5;
  live._checkStall();
  assert.equal(closed, 0);
});

test("Transcript.asContext caps size by dropping the oldest lines", () => {
  const tr = new Transcript();
  for (let i = 0; i < 400; i++) { tr.append("candidate", "x".repeat(200), i); tr.close("candidate"); }
  assert.ok(tr.asContext().length <= 40300);
});

test("interviewer brief states the persona, the CV and the language", () => {
  const text = buildInterviewerInstructions({ candidateName: "Riya", cv: "Built a payments service, cut latency 40%.", jd: "Backend engineer", language: "Hinglish", minutes: 12 });
  assert.match(text, /You are the interviewer/);
  assert.match(text, /cut latency 40%/);
  assert.match(text, /Backend engineer/);
  assert.match(text, /Hinglish/);
  assert.match(text, /about 12 minutes/);
  assert.match(languageNote("Tamil"), /in Tamil/);
  assert.match(languageNote(""), /Begin in English/);
});

import { computeMetrics, describeMetrics } from "../mock/app/metrics.js";
import { tidy, guessName } from "../mock/app/cv.js";

test("metrics: response delay, pace, fillers and pauses from timing plus the mic log", () => {
  const turns = [
    { who: "interviewer", text: "Tell me about the payments project.", start: 0, end: 4, interrupted: false },
    { who: "candidate", text: "Um so basically I built the, um, gateway integration with Cashfree and cut failures by half.", start: 6, end: 16, interrupted: false },
    { who: "interviewer", text: "How did you measure that?", start: 17, end: 19, interrupted: true },
  ];
  const voice = [];
  for (let t = 0; t <= 20; t += 0.5) voice.push([t, (t >= 6 && t < 9) || (t >= 12 && t <= 16)]);
  const m = computeMetrics(turns, voice);
  assert.equal(m.answerCount, 1);
  assert.equal(m.answers[0].responseDelay, 2);       // interviewer ended at 4, voice at 6
  assert.equal(m.answers[0].fillers, 3);             // um, basically, um
  assert.equal(m.answers[0].longestPause, 3.5);      // last voice at 8.5, next at 12
  assert.ok(m.answers[0].wpm > 50 && m.answers[0].wpm < 200);
  assert.equal(m.interruptions, 1);
  assert.ok(describeMetrics(m).some((l) => /Filler words: 3/.test(l)));
});

test("cv helpers tidy text and guess a first name", () => {
  assert.equal(tidy("Riya  Sharma \n\n\n\nSkills:   Java\r\n"), "Riya Sharma\n\nSkills: Java");
  assert.equal(guessName("Riya Sharma\nBackend Engineer\n"), "Riya");
  assert.equal(guessName("CURRICULUM VITAE\n"), "");
});

import { VoiceGate, MIC_HELP } from "../mock/app/miccheck.js";

test("mic check: a muted mic never passes and is called silent", () => {
  const g = new VoiceGate();
  for (let i = 0; i < 80; i++) assert.equal(g.feed(0, i * 0.1), false);
  assert.equal(g.passed, false);
  assert.equal(g.verdict, "silent");
  assert.match(MIC_HELP[g.verdict], /muted/);
});

test("mic check: room hiss alone does not pass, a voice does, and only once", () => {
  const g = new VoiceGate();
  for (let i = 0; i < 30; i++) assert.equal(g.feed(0.004, i * 0.1), false);   // hiss
  assert.equal(g.verdict, "quiet");
  assert.equal(g.feed(0.09, 3.0), false);
  assert.equal(g.feed(0.12, 3.1), false);
  assert.equal(g.feed(0.08, 3.2), true);      // third loud chunk inside the window
  assert.equal(g.feed(0.2, 3.3), false);      // passes once
  assert.equal(g.verdict, "ok");
});

test("mic check: isolated clicks far apart do not count as a voice", () => {
  const g = new VoiceGate();
  assert.equal(g.feed(0.3, 0), false);
  assert.equal(g.feed(0.3, 2), false);
  assert.equal(g.feed(0.3, 4), false);
  assert.equal(g.passed, false);
});

test("mic check: nothing delivered at all is reported as no audio", () => {
  assert.equal(new VoiceGate().verdict, "no-audio");
});
