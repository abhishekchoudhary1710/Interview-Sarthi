// Protocol logic of the browser interviewer engine, fed with fake server
// messages. No network, no audio. Run: node --test tests/mock_engine.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { GeminiLive, Transcript } from "../prep/app/live.js";
import { buildInterviewerInstructions, interviewerPersona, languageNote, NOTES } from "../prep/app/interviewer.js";

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
  assert.equal(sent[0].clientContent.turns[0].parts[0].text, NOTES.opening);
  assert.match(NOTES.opening, /Ask only for a brief self-introduction, then stop and wait/);
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
  assert.equal(sent.at(-1).clientContent.turns[0].parts[0].text, NOTES.reconnect);
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

test("a short answer followed by silence recovers even when metadata still arrives", () => {
  let t = 100;
  const { live, seen } = engine({ now: () => t });
  let closed = 0;
  live.ws = { close: () => closed++ };
  live._handle({ setupComplete: {} });
  live.sendAudio(new Int16Array(1600), 0.1);
  t += 16;
  live._handle({ usageMetadata: {} });
  live._checkStall();
  assert.equal(closed, 1);
  assert.ok(seen.events.some(([n]) => n === "stall_detected"));
  live.close();
});

const audioReply = { serverContent: { modelTurn: { parts: [{ inlineData: { mimeType: "audio/pcm;rate=24000", data: "AAAA" } }] } } };

test("long candidate answers and queued interviewer audio do not cause false reconnects", () => {
  let t = 100;
  const { live, seen } = engine({ now: () => t });
  live._handle({ setupComplete: {} });
  live._handle(audioReply);
  live._handle({ serverContent: { turnComplete: true } });
  for (let i = 0; i < 120; i++) {
    t++;
    live.sendAudio(new Int16Array(1600), 0.1);
    live._checkStall();
  }
  assert.equal(live.connected, true);
  live._handle(audioReply);
  live.setPlaying(true);
  t += 30;
  live._checkStall();
  assert.equal(live.connected, true);
  live.setPlaying(false);
  live._checkStall();
  assert.equal(live.connected, false);
  assert.ok(seen.events.some(([n]) => n === "stall_detected"));
  live.close();
});

test("practice clock excludes startup and reconnection, then stays frozen on close", () => {
  let t = 100;
  const { live } = engine({ now: () => t });
  live._handle({ setupComplete: {} });
  t += 8;
  assert.equal(live.activeSeconds, 0);
  live._handle(audioReply);
  t += 30;
  live._disconnect();
  t += 20;
  assert.equal(live.activeSeconds, 30);
  live._handle({ setupComplete: {} });
  t += 4;
  assert.equal(live.activeSeconds, 30);
  live._handle(audioReply);
  t += 10;
  live.close();
  t += 100;
  assert.equal(live.activeSeconds, 40);
});

test("native session resumption uses the handle without injecting another user turn", () => {
  let t = 100;
  const { live, sent } = engine({ now: () => t });
  live._handle({ setupComplete: {} });
  live._handle(audioReply);
  live._handle({ serverContent: { outputTranscription: { text: "Tell me about yourself." }, turnComplete: true } });
  live._handle({ sessionResumptionUpdate: { resumable: true, newHandle: "private-handle" } });
  const setup = live._setupMessage().setup;
  assert.deepEqual(setup.sessionResumption, { handle: "private-handle" });
  assert.equal(setup.systemInstruction.parts[0].text, "SYS");
  assert.deepEqual(setup.contextWindowCompression, { slidingWindow: {} });
  live._disconnect();
  live._resuming = true;
  const before = sent.length;
  t += 10;
  live._handle({ setupComplete: {} });
  assert.equal(sent.length, before);
  t += 5;
  assert.equal(live.activeSeconds, 5);
  live._handle({ sessionResumptionUpdate: { resumable: false } });
  assert.deepEqual(live._setupMessage().setup.sessionResumption, {});
  assert.match(live._setupMessage().setup.systemInstruction.parts[0].text, /INTERVIEW SO FAR/);
  live.close();
});

test("GoAway refresh waits for speech to finish, with a deadline before server shutdown", (ctx) => {
  ctx.mock.timers.enable({ apis: ["setTimeout"] });
  let t = 100;
  const { live, seen } = engine({ now: () => t });
  live._handle({ setupComplete: {} });
  live._handle(audioReply);
  live.setPlaying(true);
  live._handle({ goAway: { timeLeft: "30s" } });
  live._checkStall();
  assert.equal(live.connected, true);
  ctx.mock.timers.tick(28000);
  assert.equal(live.connected, false);
  assert.ok(seen.events.some(([n, d]) => n === "reconnect" && d.reason === "connection_deadline"));
  live.close();
});

test("GoAway refreshes between turns before the deadline", () => {
  const { live, seen } = engine({ now: () => 100 });
  live._handle({ setupComplete: {} });
  live._handle(audioReply);
  live._handle({ serverContent: { turnComplete: true } });
  live._handle({ goAway: { timeLeft: "30s" } });
  live._checkStall();
  assert.equal(live.connected, false);
  assert.ok(seen.events.some(([n, d]) => n === "reconnect" && d.reason === "scheduled_refresh"));
  live.close();
});

test("stopping microphone input flushes it once, and PCM slices send only their own bytes", () => {
  let t = 100;
  const { live, sent } = engine({ now: () => t });
  live._handle({ setupComplete: {} });
  const full = new Int16Array([111, 222, 333]);
  live.sendAudio(full.subarray(1, 2), 0);
  assert.equal(Buffer.from(sent.at(-1).realtimeInput.audio.data, "base64").length, 2);
  t += 2;
  live._checkStall(); live._checkStall();
  assert.equal(sent.filter(p => p.realtimeInput?.audioStreamEnd).length, 1);
  live.sendAudio(full, 0);
  t += 2;
  live._checkStall();
  assert.equal(sent.filter(p => p.realtimeInput?.audioStreamEnd).length, 2);
  live.close();
});

class FakeSocket {
  static OPEN = 1;
  static instances = [];
  constructor() { this.readyState = 1; this.bufferedAmount = 0; this.sent = []; FakeSocket.instances.push(this); }
  send(data) { this.sent.push(JSON.parse(data)); }
  close() { this.readyState = 3; this.onclose?.({ code: 1000, reason: "" }); }
  open() { this.onopen?.(); }
  message(message) { this.onmessage?.({ data: JSON.stringify(message) }); }
}

function transport(ctx) {
  const original = globalThis.WebSocket;
  globalThis.WebSocket = FakeSocket;
  FakeSocket.instances = [];
  ctx.mock.timers.enable({ apis: ["setTimeout", "setInterval"] });
  let t = 100;
  const notices = [];
  const live = new GeminiLive({ apiKey: "test", instructions: () => "SYS", now: () => t, onNotice: m => notices.push(m) });
  ctx.after(() => { live.close(); globalThis.WebSocket = original; });
  return { live, notices, advance: seconds => { t += seconds; ctx.mock.timers.tick(seconds * 1000); } };
}

test("setup that never completes times out, retries, and ignores a retired socket", (ctx) => {
  const { live, advance } = transport(ctx);
  live.start();
  const old = live.ws;
  old.open();
  advance(12);
  assert.equal(live.ws, null);
  advance(1);
  const next = live.ws;
  assert.notEqual(next, old);
  next.open(); next.message({ setupComplete: {} });
  old.onclose({ code: 1006, reason: "late close" });
  old.message({ serverContent: { inputTranscription: { text: "stale" } } });
  assert.equal(live.connected, true);
  assert.equal(live.transcript.turns.length, 0);
});

test("closing during backoff cancels the queued reconnect", (ctx) => {
  const { live, advance } = transport(ctx);
  live.start();
  live.ws.close();
  live.close();
  advance(60);
  assert.equal(FakeSocket.instances.length, 1);
});

test("an expired resumption handle falls back to the saved transcript", (ctx) => {
  const { live, advance } = transport(ctx);
  live.transcript.append("candidate", "I built the API.", 90);
  live._resumeHandle = "expired";
  live.start();
  live.ws.open();
  assert.equal(live.ws.sent[0].setup.sessionResumption.handle, "expired");
  live.ws.onclose({ code: 1008, reason: "Session resumption handle expired" });
  advance(1);
  live.ws.open();
  assert.deepEqual(live.ws.sent[0].setup.sessionResumption, {});
  assert.match(live.ws.sent[0].setup.systemInstruction.parts[0].text, /I built the API/);
  live.ws.message({ setupComplete: {} });
  assert.equal(live.connected, true);
});

test("a greeting that never arrives triggers recovery without consuming practice time", (ctx) => {
  const { live, advance } = transport(ctx);
  live.start(); live.ws.open(); live.ws.message({ setupComplete: {} });
  advance(15);
  assert.equal(live.connected, false);
  assert.equal(live.activeSeconds, 0);
});

test("a delayed Blob from a retired socket cannot update the new session", async () => {
  const { live } = engine();
  const old = {}, replacement = {};
  live.ws = old;
  let release;
  const blob = new Blob();
  blob.text = () => new Promise(resolve => { release = resolve; });
  const pending = live._onRaw(blob, old);
  live.ws = replacement;
  release(JSON.stringify({ setupComplete: {} }));
  await pending;
  assert.equal(live.connected, false);
  live.close();
});

test("transient initial failures retry but quota failures stop immediately", (ctx) => {
  const { live, advance, notices } = transport(ctx);
  live.start();
  live.ws.onclose({ code: 1011, reason: "temporary internal error" });
  assert.equal(live.stopped, false);
  advance(1);
  live.ws.onclose({ code: 1008, reason: "RESOURCE_EXHAUSTED quota" });
  assert.equal(live.stopped, true);
  assert.match(notices.at(-1), /usage limit/);
  advance(60);
  assert.equal(FakeSocket.instances.length, 2);
});

test("repeated startup failures terminate instead of retrying forever", (ctx) => {
  const { live, advance } = transport(ctx);
  live.start();
  for (let i = 0; i < 6; i++) {
    live.ws.onclose({ code: 1011, reason: "temporary internal error" });
    if (!live.stopped) advance(8);
  }
  assert.equal(live.stopped, true);
  assert.equal(FakeSocket.instances.length, 6);
});

test("socket backpressure recovers without queuing more stale audio", (ctx) => {
  const { live } = transport(ctx);
  live.start();
  const ws = live.ws;
  ws.open(); ws.message({ setupComplete: {} });
  ws.bufferedAmount = 200000;
  const count = ws.sent.length;
  assert.equal(live.sendAudio(new Int16Array(1600), 0.1), false);
  assert.equal(ws.sent.length, count);
  assert.equal(live.connected, false);
  assert.equal(live.sendText("wrap up"), false);
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

test("fresh calls preserve introduction and project stages across CVs and session lengths", () => {
  for (const minutes of [2, 5, 12, 30]) {
    for (const cv of ["", "Student with no work experience.", "Principal engineer; led distributed systems at scale."]) {
      const brief = buildInterviewerInstructions({ cv, minutes });
      const stages = ["1. Welcome and introduction", "2. Project or experience walkthrough", "3. Role-related exploration", "4. Behavioural discussion", "5. Candidate questions and close"];
      const positions = stages.map(stage => brief.indexOf(stage));
      assert.ok(positions.every((position, i) => position >= 0 && (!i || position > positions[i - 1])));
      assert.match(brief, /FIRST question must invite a brief self-introduction/);
      assert.match(brief, /Wait for the overview before asking about their personal contribution/);
      assert.match(brief, /If they have no project, use a coursework task/);
      assert.match(brief, /If they struggle or say they do not know, simplify/);
      assert.match(brief, /For a short session, keep the introduction/);
      assert.match(brief, /If they explicitly ask to skip it, respect that/);
    }
  }
});

test("startup recovery before any speech still requests an introduction", () => {
  const { live, sent } = engine();
  live._handle({ setupComplete: {} });
  live._disconnect();
  live._handle({ setupComplete: {} });
  assert.equal(sent.at(-1).clientContent.turns[0].parts[0].text, NOTES.opening);
  live.close();
});

test("wrap-up invites candidate questions instead of another assessment topic", () => {
  const { live, sent } = engine();
  live._handle({ setupComplete: {} });
  live.sendText(NOTES.wrapUp);
  assert.match(sent.at(-1).clientContent.turns[0].parts[0].text, /ask what questions the candidate has for you and wait/);
  assert.match(NOTES.wrapUp, /Do not start another assessment topic/);
  live.close();
});

test("the interviewer's gender follows the chosen voice", () => {
  const male = interviewerPersona("Charon");
  assert.deepEqual([male.gender, male.they, male.them, male.their, male.themself], ["male", "he", "him", "his", "himself"]);
  const female = interviewerPersona("Kore");
  assert.deepEqual([female.gender, female.they, female.them, female.their, female.themself], ["female", "she", "her", "her", "herself"]);
  assert.equal(interviewerPersona("puck").they, "he");          // the select's value, whatever its case
  assert.equal(interviewerPersona("").they, "she");             // nothing chosen yet: the default voice is Kore
  assert.equal(interviewerPersona("Nonesuch").they, "she");
});

test("a male voice gets a male interviewer in the brief, and the CV screen offers both", () => {
  const male = buildInterviewerInstructions({ candidateName: "Riya", cv: "Built a payments service.", voice: "Fenrir" });
  assert.match(male, /You are Arjun Nair, a male senior hiring manager/);
  const female = buildInterviewerInstructions({ candidateName: "Riya", cv: "Built a payments service.", voice: "Leda" });
  assert.match(female, /You are Priya Nair, a female senior hiring manager/);
  // Every voice in the picker has to be one the persona knows, or the page
  // would say "she" over a male voice again.
  const html = readFileSync(new URL("../prep/app/index.html", import.meta.url), "utf8");
  const picker = html.match(/<select id="voice">([\s\S]*?)<\/select>/)[1];
  const offered = [...picker.matchAll(/value="([^"]+)"[^>]*>[^·]*· (\w+)/g)];
  assert.ok(offered.length >= 6);
  for (const [, voice, gender] of offered) assert.equal(interviewerPersona(voice).gender, gender, voice);
});

import { computeMetrics, describeMetrics } from "../prep/app/metrics.js";
import { tidy, guessName } from "../prep/app/cv.js";
import { generateReport } from "../prep/app/report.js";

test("report evaluates an introduction on its own merits and acknowledges untested skills", async (ctx) => {
  let request;
  ctx.mock.method(globalThis, "fetch", async (_url, options) => {
    request = JSON.parse(options.body);
    return { ok: true, json: async () => ({ candidates: [{ content: { parts: [{ text: '{"overall_score":70}' }] } }] }) };
  });
  await generateReport({ apiKey: "test", cv: "Student", language: "English", minutes: 2,
    transcript: [{ who: "interviewer", text: "Tell me about yourself." }, { who: "candidate", text: "I am studying commerce." }],
    metrics: computeMetrics([], []),
  });
  const prompt = request.systemInstruction.parts[0].text;
  assert.match(prompt, /do not require numbers or technical depth in an introduction/);
  assert.match(prompt, /Do not penalize skills or stages that were never assessed/);
  assert.match(prompt, /explicitly describe the assessment as limited/);
});

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

import { VoiceGate, MIC_HELP } from "../prep/app/miccheck.js";

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
