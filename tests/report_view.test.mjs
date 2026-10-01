// The report dashboard (prep/app/report-view.js). Run: node --test tests/report_view.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { reportHtml, band } from "../prep/app/report-view.js";

const q = (question, score) => ({ question, answer_gist: `gist of ${question}`, score, what_was_missing: "a result", better_answer: "a stronger answer" });
const record = (report = {}, extra = {}) => ({ at: "2026-10-01T09:00:00Z", elapsed: 421, language: "English", transcript: [{ who: "interviewer", text: "Q" }, { who: "candidate", text: "I added retries." }],
  metrics: { answers: [{ words: 20, seconds: 10, wpm: 120, responseDelay: 1.5, fillers: 1 }, { words: 30, seconds: 12, wpm: 150, responseDelay: 3.5, fillers: 0 }],
    avgWpm: 136, avgResponseDelay: 2.5, fillersTotal: 1, fillersPerMinute: 0.5, longestPause: 2, candidateTalkSeconds: 60, interviewerTalkSeconds: 40, interruptions: 1 },
  report: { overall_score: 64, verdict: "Specific, but no results.", questions: [q("Tell me about yourself.", 7), q("How did you verify it?", 4)],
    competencies: [{ id: "communication", label: "Communication", status: "assessed", score: 7, evidence_turns: [2], explanation: "Clear." },
      { id: "judgment_learning", label: "Judgment and learning", status: "not_assessed", score: null, evidence_turns: [], explanation: "Not tested." }],
    strengths: ["Specific"], weaknesses: ["No results"], practice_next: ["One", "Two", "Three"],
    next_focus: { group: "ownership", issue: "Stops before the result.", drill: "End with the number." }, delivery: { pace: "Steady." }, ...report }, ...extra });

test("the whole report is shown: every question with what was missing and a stronger answer, nothing locked", () => {
  const html = reportHtml(record({}, { locked: true, demo: true }));
  assert.ok(!/locked|Unlock/i.test(html), "a demo report is no longer locked");
  assert.equal((html.match(/class="q rd-q" data-qi=/g) || []).length, 2, "question rows keep .q[data-qi] for the retake buttons");
  assert.equal((html.match(/A stronger answer/g) || []).length, 2);
  assert.match(html, /data-qi="1" open/, "the weakest answer starts open");
  assert.match(html, /Weakest/);
});

test("the score leads with its band in words and icon, and the six headline numbers", () => {
  const html = reportHtml(record());
  assert.match(html, /rd-hero rd-mid/);
  assert.match(html, /Getting there/);
  for (const label of ["Answers scored", "Speaking pace", "Pause before answering", "Filler words", "You spoke", "Interview length"]) assert.ok(html.includes(label), label);
  assert.match(html, /60<em>%<\/em>/, "talk share is the candidate's part of all talking time");
  assert.deepEqual([band(80).label, band(55).label, band(30).label, band(null).label], ["Strong", "Getting there", "Needs work", "Not enough evidence"]);
});

test("skills show their score on a bar, untested ones say so, and the evidence opens in place", () => {
  const html = reportHtml(record());
  assert.match(html, /Communication[\s\S]*width:70%[\s\S]*<b class="rd-val">7<\/b>/);
  assert.match(html, /Judgment and learning[\s\S]*Not assessed/);
  assert.match(html, /<blockquote>I added retries\.<\/blockquote>/);
});

test("delivery charts plot each answer, with the numbers also in a table", () => {
  const html = reportHtml(record());
  assert.match(html, /Pause before each answer/);
  assert.match(html, /aria-label="Answer 2: 3\.5 seconds"/);
  assert.match(html, /<table>[\s\S]*150 wpm/);
});

test("text from the report is escaped, never markup", () => {
  const html = reportHtml(record({ verdict: '<img src=x onerror="alert(1)">', questions: [q("<script>x</script>", 5)] }));
  assert.ok(!html.includes("<script>x</script>") && !html.includes("<img src=x"));
  assert.match(html, /&lt;script&gt;/);
});
