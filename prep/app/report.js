/* Prep Sarthi: the report card, one text call on the candidate's key.
 *
 * Mirrors the desktop app's gemini_text.py: generateContent, first model that
 * answers wins, 404/429/5xx move to the next. JSON output is requested so the
 * page renders fields, not prose.
 */

import { describeMetrics } from "./metrics.js";
import { COMPETENCIES, ASSESSMENT_BRIEF, normalizeAssessment } from "./assessment.js";

export const REPORT_MODELS = ["gemini-3.6-flash", "gemini-3.1-flash-lite"];
const URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}";

const SCHEMA = {
  type: "OBJECT",
  properties: {
    overall_score: { type: "INTEGER", nullable: true, description: "Provisional practice score; the app recomputes the average of evidenced competency scores." },
    competencies: { type: "ARRAY", items: {
      type: "OBJECT", properties: {
        id: { type: "STRING", enum: COMPETENCIES.map(c => c.id) },
        status: { type: "STRING", enum: ["assessed", "limited", "not_assessed"] },
        score: { type: "NUMBER", nullable: true, description: "0-10 for relevant observed evidence, null when not assessed" },
        evidence_turns: { type: "ARRAY", items: { type: "INTEGER" }, description: "1-based candidate turn numbers from the original transcript that support this assessment" },
        explanation: { type: "STRING", description: "Brief evidence-based reason for this score, or why evidence is missing" },
      }, required: ["id", "status", "score", "evidence_turns", "explanation"],
    } },
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
  required: ["overall_score", "competencies", "verdict", "strengths", "weaknesses", "questions", "delivery", "practice_next"],
};

function systemPrompt(language) {
  return `You are a blunt, kind senior interviewer writing the debrief after a mock interview. Judge only what the transcript shows. Be specific: quote the candidate's own words when pointing out a problem. Never invent facts about the candidate. Evaluate each answer against the question actually asked and the candidate's experience: an introduction needs a clear relevant background, a project walkthrough needs purpose and personal contribution, a technical answer needs sound reasoning, and a behavioural answer needs actions and outcomes. Reward specific evidence where relevant, but do not require numbers or technical depth in an introduction. Do not penalize skills or stages that were never assessed, candidate questions at the close, or answers cut off by the session time limit. If the session only covered background or one project, explicitly describe the assessment as limited instead of claiming technical readiness was established. Write in ${language && language.toLowerCase() !== "auto" ? language : "the language the candidate mostly spoke"}; keep technical terms in English.`;
}

export async function generateReport({ apiKey, cv, jd, language, transcript, metrics, minutes }) {
  const lines = transcript.map((u, i) => `[${i + 1}] ${u.who === "interviewer" ? "INTERVIEWER" : "CANDIDATE"}: ${u.text}${u.interrupted ? " [cut off]" : ""}`);
  const user = [
    `Mock interview length: ${minutes} minutes. ${jd ? "The role:\n" + jd + "\n" : ""}`,
    `CANDIDATE CV:\n${cv || "(none)"}`,
    `DELIVERY METRICS (measured from the microphone):\n${describeMetrics(metrics).join("\n")}`,
    `TRANSCRIPT:\n${lines.join("\n")}`,
    `ASSESSMENT AREAS:\n${ASSESSMENT_BRIEF}\nReturn exactly one competencies entry per area. Mark assessed only with a relevant substantive answer, limited for thin but relevant evidence, and not_assessed with score=null and no evidence_turns when it was not meaningfully tested. A CV claim alone, a greeting, an unanswered question or interviewer speech is not answer evidence. Link only candidate turn numbers that actually demonstrate the area; do not reuse an introduction as evidence of technical ability. Score the evidence using common anchors: 0-2 fundamentally incorrect or no relevant substance in an attempted answer; 3-4 partial understanding with major gaps; 5-6 adequate approach with missing detail; 7-8 clear, sound reasoning with a specific example; 9-10 strong depth, justified decisions and appropriate verification or reflection. Apply these to the role and question, without demanding numeric achievements. Do not infer confidence, competence or personality from accent, language choice or speaking speed. The overall score is an equal-weight mean of scored areas only, not a hiring prediction. State coverage limits in the verdict. Recommend unassessed important JD skills for a later round, including a work sample or coding task when a voice interview cannot test them.`,
    "Produce the debrief as JSON matching the schema. One entry in `questions` per real interviewer question that got an answer (skip greetings and small talk).",
  ].join("\n\n");
  const body = JSON.stringify({
    systemInstruction: { parts: [{ text: systemPrompt(language) }] },
    contents: [{ role: "user", parts: [{ text: user }] }],
    generationConfig: { temperature: 0.3, maxOutputTokens: 7000, responseMimeType: "application/json", responseSchema: SCHEMA },
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
    try { return { model, report: normalizeAssessment(JSON.parse(text), transcript) }; }
    catch { last = "Gemini returned malformed JSON"; continue; }
  }
  throw new Error(last);
}
