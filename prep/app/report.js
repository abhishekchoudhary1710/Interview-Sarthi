/* Prep Sarthi: the report card, one text call on the candidate's key.
 *
 * Mirrors the desktop app's gemini_text.py: generateContent, first model that
 * answers wins, 404/429/5xx move to the next. JSON output is requested so the
 * page renders fields, not prose.
 */

import { describeMetrics } from "./metrics.js";

export const REPORT_MODELS = ["gemini-3.6-flash", "gemini-3.1-flash-lite"];
const URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}";

const SCHEMA = {
  type: "OBJECT",
  properties: {
    overall_score: { type: "INTEGER", description: "0-100, how hireable this performance was" },
    verdict: { type: "STRING", description: "one sentence, honest, specific" },
    strengths: { type: "ARRAY", items: { type: "STRING" } },
    weaknesses: { type: "ARRAY", items: { type: "STRING" } },
    questions: {
      type: "ARRAY",
      items: {
        type: "OBJECT",
        properties: {
          question: { type: "STRING" },
          answer_gist: { type: "STRING", description: "what the candidate actually said, in one line" },
          score: { type: "INTEGER", description: "0-10" },
          what_was_missing: { type: "STRING" },
          better_answer: { type: "STRING", description: "a stronger answer in the candidate's own voice, 40-90 words, using only facts from the CV or the transcript" },
        },
        required: ["question", "answer_gist", "score", "what_was_missing", "better_answer"],
      },
    },
    delivery: {
      type: "OBJECT",
      properties: {
        pace: { type: "STRING" }, fillers: { type: "STRING" }, confidence: { type: "STRING" }, structure: { type: "STRING" },
      },
      required: ["pace", "fillers", "confidence", "structure"],
    },
    practice_next: { type: "ARRAY", items: { type: "STRING" }, description: "exactly three concrete drills for the next mock" },
  },
  required: ["overall_score", "verdict", "strengths", "weaknesses", "questions", "delivery", "practice_next"],
};

function systemPrompt(language) {
  return `You are a blunt, kind senior interviewer writing the debrief after a mock interview. Judge only what the transcript shows. Be specific: quote the candidate's own words when pointing out a problem. Never invent facts about the candidate. Evaluate each answer against the question actually asked and the candidate's experience: an introduction needs a clear relevant background, a project walkthrough needs purpose and personal contribution, a technical answer needs sound reasoning, and a behavioural answer needs actions and outcomes. Reward specific evidence where relevant, but do not require numbers or technical depth in an introduction. Do not penalize skills or stages that were never assessed, candidate questions at the close, or answers cut off by the session time limit. If the session only covered background or one project, explicitly describe the assessment as limited instead of claiming technical readiness was established. Write in ${language && language.toLowerCase() !== "auto" ? language : "the language the candidate mostly spoke"}; keep technical terms in English.`;
}

export async function generateReport({ apiKey, cv, jd, language, transcript, metrics, minutes }) {
  const lines = transcript.map((u) => `${u.who === "interviewer" ? "INTERVIEWER" : "CANDIDATE"}: ${u.text}${u.interrupted ? " [cut off]" : ""}`);
  const user = [
    `Mock interview length: ${minutes} minutes. ${jd ? "The role:\n" + jd + "\n" : ""}`,
    `CANDIDATE CV:\n${cv || "(none)"}`,
    `DELIVERY METRICS (measured from the microphone):\n${describeMetrics(metrics).join("\n")}`,
    `TRANSCRIPT:\n${lines.join("\n")}`,
    "Produce the debrief as JSON matching the schema. One entry in `questions` per real interviewer question that got an answer (skip greetings and small talk).",
  ].join("\n\n");
  const body = JSON.stringify({
    systemInstruction: { parts: [{ text: systemPrompt(language) }] },
    contents: [{ role: "user", parts: [{ text: user }] }],
    generationConfig: { temperature: 0.3, maxOutputTokens: 4000, responseMimeType: "application/json", responseSchema: SCHEMA },
  });
  let last = "no model answered";
  for (const model of REPORT_MODELS) {
    let res;
    try {
      res = await fetch(URL.replace("{model}", model).replace("{key}", encodeURIComponent(apiKey)), {
        method: "POST", headers: { "content-type": "application/json" }, body,
      });
    } catch (err) { throw new Error(`Gemini unreachable (${err.message})`); }
    if (!res.ok) {
      let detail = "";
      try { detail = (await res.json()).error.message; } catch (_) { /* no body */ }
      last = `Gemini HTTP ${res.status}${detail ? ": " + detail : ""}`;
      if ([404, 429, 500, 503].includes(res.status)) continue;
      throw new Error(last);
    }
    const payload = await res.json();
    const text = ((((payload.candidates || [])[0] || {}).content || {}).parts || []).map((p) => p.text || "").join("").trim();
    if (!text) { last = "Gemini returned no report"; continue; }
    try { return { model, report: JSON.parse(text) }; }
    catch { last = "Gemini returned malformed JSON"; continue; }
  }
  throw new Error(last);
}
