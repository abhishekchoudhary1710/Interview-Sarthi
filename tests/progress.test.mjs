// Progress across the month: progress.js numbers, report focus fields, month analysis and re-answers (29 Sep 2026).
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  DELIVERY, MIN_MINUTES, SKILL_GROUPS, buildProgress, carryFocus, comparability, dayKey, reportChanges, summarize, trackKey, writerTier,
} from "../prep/app/progress.js";
import { RUBRIC_VERSION, generateReport, normalizeProgressFields } from "../prep/app/report.js";
import { buildInterviewerInstructions } from "../prep/app/interviewer.js";
import { computeMetrics } from "../prep/app/metrics.js";
import { analyse, analysisId, dueAnalyses, facts, monthReportText, validateAnalysis } from "../prep/app/insights.js";
import { buildRedrillInstructions, compareAnswers, redrillItem, redrillNotes, redrillProgress, redrillSource } from "../prep/app/redrill.js";

const TZ = "Asia/Kolkata";
const day = (n, h = 10) => new Date(Date.UTC(2026, 9, n, h - 5, 30)).toISOString();   // October n, h:00 IST

const transcript = [
  { who: "interviewer", text: "Tell me about yourself.", start: 0, end: 3 },
  { who: "candidate", text: "I am a backend developer, um, working on payments.", start: 4, end: 20 },
  { who: "interviewer", text: "Walk me through the payment retry project.", start: 21, end: 25 },
  { who: "candidate", text: "We built a retry queue and basically we cut failures by half.", start: 26, end: 70 },
  { who: "interviewer", text: "What did you personally do?", start: 71, end: 73, interrupted: false },
  { who: "candidate", text: "I designed the backoff and wrote the monitoring.", start: 74, end: 110 },
];
const plan = { mode: "job_description", role: "Backend engineer", level: "Mid-level", requirements: [] };
function record(o = {}) {
  const rows = o.rows || [
    { id: "r1", category: "role_knowledge", weight: 2, score: 6, status: "assessed" },
    { id: "r2", category: "role_knowledge", weight: 1, score: 9, status: "assessed" },
    { id: "r3", category: "communication", weight: 1, score: 7, status: "limited" },
    { id: "r4", category: "collaboration", weight: 1, score: null, status: "not_assessed" },
  ];
  return {
    id: o.id || "iv-1", at: o.at || day(1), elapsed: o.elapsed ?? 600, language: "English", model: o.model || "gemini-3.6-flash",
    rubric: RUBRIC_VERSION, demo: !!o.demo,
    report: { overall_score: "score" in o ? o.score : 70, requirements: rows, plan: { ...plan, ...(o.plan || {}) },
      questions: [{ question: "Walk me through the payment retry project.", score: 6, answer_turns: [4], answer_gist: "retry queue", what_was_missing: "own role", better_answer: "..." }],
      practice_next: ["a", "b", "c", "d"], next_focus: o.focus === undefined ? { group: "ownership", issue: "Says we instead of I", drill: "Name one decision you made" } : o.focus,
      focus_check: o.check || null },
    metrics: computeMetrics(transcript, []), transcript,
  };
}
const S = (o) => summarize(record(o));

test("a summary keeps numbers, skill groups by weight, delivery, focus and who wrote it; never the transcript", () => {
  const s = S();
  assert.equal(s.score, 70);
  assert.deepEqual(s.groups.role_knowledge, { score: 7, n: 2, limited: false });          // (6*2 + 9) / 3
  assert.deepEqual(s.groups.communication, { score: 7, n: 1, limited: true });
  assert.equal(s.groups.collaboration, undefined, "not assessed stays missing, never zero");
  assert.deepEqual(s.planned, { role_knowledge: 2, communication: 1, collaboration: 1 });
  assert.deepEqual(s.coverage, { scored: 3, total: 4 });
  assert.equal(s.minutes, 10);
  assert.equal(s.writer, "main");
  assert.equal(s.rubric, RUBRIC_VERSION);
  assert.equal(s.track, trackKey({ mode: "job_description", role: "backend ENGINEER", level: "mid-level " }));
  assert.equal(s.focus.issue, "Says we instead of I");
  assert.equal(s.practice_next.length, 3);
  assert.equal(s.delivery.answers, 3);
  assert.equal(s.delivery.metrics_v, 2);
  assert.ok(s.delivery.talk_share > 0.8);
  assert.ok(!JSON.stringify(s).includes("retry queue and basically"), "no answer text in a summary");
  assert.equal(writerTier("gemini-3.1-flash-lite"), "lite");
  assert.equal(writerTier("openai/gpt-oss-120b"), "backup");
  // a plan-less report (the six broad areas) maps onto the same groups
  const broad = summarize({ ...record(), report: { overall_score: 50, competencies: [{ id: "problem_solving", score: 5, status: "assessed" }] } });
  assert.deepEqual(broad.groups.problem_solving, { score: 5, n: 1, limited: false });
  assert.equal(SKILL_GROUPS.length, 8);
});

test("Hindi words are not fillers: toh, wo and haan no longer count", () => {
  const m = computeMetrics([{ who: "interviewer", text: "Q", start: 0, end: 1 }, { who: "candidate", text: "Haan toh wo project mein um basically maine API banaya", start: 2, end: 10 }], []);
  assert.equal(m.answers[0].fillers, 2);   // um, basically
  assert.equal(m.v, 2);
});

test("only full interviews move a trend, and the page is told why one was left out", () => {
  assert.deepEqual(comparability(S()), { ok: true, reason: null });
  assert.equal(comparability(S({ elapsed: (MIN_MINUTES - 1) * 60 })).reason, "too_short");
  assert.equal(comparability(S({ score: null })).reason, "no_score");
  assert.equal(comparability(S({ rows: [{ category: "communication", score: 7 }, { category: "leadership", score: null }, { category: "ownership", score: null }] })).reason, "low_coverage");
});

test("report badges: change since last time and since the first interview of the pass, per skill too", () => {
  const a = S({ id: "a", at: day(1), score: 50, rows: [{ category: "communication", score: 5 }] });
  const short = S({ id: "b", at: day(2), score: 90, elapsed: 60 });
  const c = S({ id: "c", at: day(3), score: 60, rows: [{ category: "communication", score: 6 }] });
  const now = S({ id: "d", at: day(4), score: 72, rows: [{ category: "communication", score: 8 }, { category: "leadership", score: 6 }] });
  const ch = reportChanges(now, [a, short, c, now]);
  assert.equal(ch.comparable, true);
  assert.equal(ch.score.since_last, 12);
  assert.equal(ch.score.since_first, 22);
  assert.equal(ch.score.last_id, "c", "the too-short interview is skipped");
  assert.equal(ch.score.interviews, 3);
  assert.deepEqual(ch.groups.find((g) => g.id === "communication"), { id: "communication", label: "Communication", score: 8, since_last: 2, since_first: 3, first_time: false });
  assert.equal(ch.groups.find((g) => g.id === "leadership").first_time, true);
  // first of a new pass: nothing earlier inside the period
  assert.equal(reportChanges(now, [a, c], { start: day(4, 0), end: day(30) }).score, null);
  assert.equal(reportChanges(short, [a]).comparable, false);
});

test("the month: score line, skills, delivery against guide ranges, calendar, streak and readiness", () => {
  const items = [
    S({ id: "a", at: day(1), score: 48, model: "gemini-3.1-flash-lite", rows: [{ category: "communication", score: 4 }, { category: "role_knowledge", score: 5 }, { category: "problem_solving", score: 4 }] }),
    S({ id: "b", at: day(2), score: 55, rows: [{ category: "communication", score: 5 }, { category: "role_knowledge", score: 6 }] }),
    S({ id: "x", at: day(2, 20), score: 90, elapsed: 120 }),
    S({ id: "c", at: day(4), score: 66, rows: [{ category: "communication", score: 7 }, { category: "role_knowledge", score: 7 }, { category: "problem_solving", score: 7 }] }),
    S({ id: "d", at: day(5), score: 74, check: { status: "fixed", note: "used I" }, rows: [{ category: "communication", score: 8 }, { category: "role_knowledge", score: 8 }, { category: "problem_solving", score: 7 }] }),
    { id: "an", kind: "analysis", at: day(5) },
  ];
  const p = buildProgress(items, { period: { start: day(1, 6), end: day(31, 6) }, now: new Date(day(5, 22)), timeZone: TZ });
  assert.equal(p.score.enough, true);
  assert.deepEqual([p.score.first, p.score.latest, p.score.best, p.score.change_since_first, p.score.change_since_last], [48, 74, 74, 26, 8]);
  assert.equal(p.score.points.find((x) => x.id === "x").comparable, false);
  assert.equal(p.score.points.length, 5, "analyses are not interviews");
  const comm = p.groups.find((g) => g.id === "communication");
  assert.deepEqual([comm.n, comm.start, comm.recent, comm.change, comm.trend, comm.status], [4, 4.5, 6.7, 3, "up", "developing"]);
  assert.equal(p.groups.find((g) => g.id === "leadership").status, "not_tested");
  assert.ok(p.coverage.never_tested.includes("leadership"));
  assert.ok(p.coverage.planned_not_scored.includes("collaboration"), "planned in one interview, never scored");
  const wpm = p.delivery.find((d) => d.id === "wpm");
  assert.equal(wpm.approximate, true);
  assert.deepEqual(wpm.target, DELIVERY[0].target);
  assert.equal(p.totals.interviews, 5);
  assert.equal(p.totals.practice_days, 4);
  assert.equal(p.totals.streak, 2, "4 and 5 October");
  assert.equal(p.calendar.length, 31);
  assert.deepEqual(p.calendar.find((d) => d.date === "2026-10-02").interviews, ["b", "x"]);
  assert.equal(p.calendar.find((d) => d.date === "2026-10-03").interviews.length, 0, "an empty day stays empty");
  assert.equal(p.calendar.find((d) => d.date === "2026-10-10").future, true);
  assert.deepEqual([p.period.day, p.period.days, p.period.days_left], [5, 30, 26]);
  assert.equal(p.readiness.level, "getting_there");
  assert.ok(p.readiness.reasons.some((r) => r.code === "recent_average" && r.value === 65));
  assert.equal(p.focus.fixed, 1);
  assert.equal(p.focus.current.issue, "Says we instead of I");
  assert.ok(p.warnings.some((w) => w.code === "mixed_writers" && w.ids[0] === "a"));
  assert.ok(p.warnings.some((w) => w.code === "excluded" && w.ids[0] === "x"));
});

test("too little to judge is said plainly; roles can be viewed apart", () => {
  const one = buildProgress([S({ id: "a", at: day(1) })], { now: new Date(day(1, 12)), timeZone: TZ });
  assert.equal(one.score.enough, false);
  assert.match(one.score.message, /next one/);
  assert.equal(one.readiness.level, "not_enough");
  assert.equal(one.groups.find((g) => g.id === "communication").trend, "not_enough");
  assert.equal(buildProgress([], { now: new Date(day(1)) }).score.message.includes("after two"), true);
  const other = S({ id: "b", at: day(2), plan: { role: "Data analyst" } });
  const both = buildProgress([S({ id: "a", at: day(1) }), other], { now: new Date(day(2, 12)), timeZone: TZ });
  assert.equal(both.tracks.length, 2);
  assert.equal(both.score.different_roles, true);
  const only = buildProgress([S({ id: "a", at: day(1) }), other], { track: other.track, now: new Date(day(2, 12)), timeZone: TZ });
  assert.deepEqual(only.score.points.map((x) => x.id), ["b"]);
});

test("ready needs three recent interviews at 70+, no weak skill and the core skills tested", () => {
  const good = (id, n) => S({ id, at: day(n), score: 78, rows: [{ category: "communication", score: 8 }, { category: "role_knowledge", score: 7 }, { category: "problem_solving", score: 7.5 }] });
  const p = buildProgress([good("a", 1), good("b", 2), good("c", 3)], { now: new Date(day(3, 12)), timeZone: TZ });
  assert.equal(p.readiness.level, "ready");
  const gap = (id, n) => S({ id, at: day(n), score: 78, rows: [{ category: "communication", score: 8 }, { category: "role_knowledge", score: 7 }] });
  const q = buildProgress([gap("a", 1), gap("b", 2), gap("c", 3)], { now: new Date(day(3, 12)), timeZone: TZ });
  assert.equal(q.readiness.level, "getting_there");
  assert.ok(q.readiness.reasons.some((r) => r.code === "untested_core" && r.group === "problem_solving"));
});

test("the focus carried into the next interview: recent only, and a role-knowledge focus only for the same role", () => {
  const a = S({ id: "a", at: day(1), focus: { group: "role_knowledge", issue: "Vague on SQL joins", drill: "x" } });
  assert.equal(carryFocus([a], a.track, new Date(day(2))).issue, "Vague on SQL joins");
  assert.equal(carryFocus([a], "job_description|data analyst|mid-level", new Date(day(2))), null);
  assert.equal(carryFocus([a], a.track, new Date(day(20))), null, "older than two weeks");
  const b = S({ id: "b", at: day(3), focus: { group: "ownership", issue: "Says we", drill: "" } });
  assert.equal(carryFocus([a, b], "other|role|x", new Date(day(4))).from_id, "b");
  assert.equal(S({ focus: { group: "hobbies", issue: "x" } }).focus, null);
  assert.equal(dayKey("2026-10-01T20:00:00Z", TZ), "2026-10-02");
});

test("report fields for progress are checked against the transcript", () => {
  const raw = { questions: [{ question: "Q", answer_turns: [2, 3, 99] }], next_focus: { group: "ownership", issue: "Says we", drill: "d" },
    focus_check: { status: "fixed", evidence_turns: [1], note: "fixed" } };
  const out = normalizeProgressFields(raw, transcript, true);
  assert.deepEqual(out.questions[0].answer_turns, [2]);
  assert.deepEqual(out.focus_check, { status: "not_tested", evidence_turns: [], note: "" }, "a claim with no candidate turn is a guess");
  assert.equal(normalizeProgressFields({ ...raw, focus_check: { status: "still_open", evidence_turns: [4], note: "again" } }, transcript, true).focus_check.status, "still_open");
  assert.equal(normalizeProgressFields(raw, transcript, false).focus_check, null, "no focus was set");
  assert.equal(normalizeProgressFields({ ...raw, next_focus: { group: "x", issue: "y" } }, transcript, false).next_focus, null);
});

test("the report asks whether last time's focus was fixed only when there was one", async () => {
  const bodies = [];
  const transport = async (_model, body) => {
    bodies.push(JSON.parse(body));
    return new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify({
      overall_score: 60, competencies: [], verdict: "v", strengths: [], weaknesses: [], questions: [], delivery: { pace: "", fillers: "", confidence: "", structure: "" },
      practice_next: [], next_focus: { group: "communication", issue: "Rambles", drill: "Answer in three parts" },
      focus_check: { status: "improved", evidence_turns: [4], note: "shorter" } }) }] } }] }), { status: 200 });
  };
  const args = { transcript, metrics: computeMetrics(transcript, []), minutes: 10, language: "English", transport };
  const plain = await generateReport(args);
  assert.equal(plain.report.focus_check, null);
  assert.equal(plain.report.next_focus.issue, "Rambles");
  assert.ok(!bodies[0].generationConfig.responseSchema.properties.focus_check);
  assert.ok(bodies[0].generationConfig.responseSchema.required.includes("next_focus"));
  const withFocus = await generateReport({ ...args, previousFocus: { group: "ownership", issue: "Says we instead of I", drill: "d" } });
  assert.equal(withFocus.report.focus_check.status, "improved");
  assert.ok(bodies[1].generationConfig.responseSchema.required.includes("focus_check"));
  assert.match(bodies[1].contents[0].parts[0].text, /Says we instead of I/);
});

test("the interviewer is told about the focus privately, and only when there is one", () => {
  const base = { candidateName: "Riya", cv: "cv", language: "English" };
  assert.ok(!buildInterviewerInstructions(base).includes("PRACTICE FOCUS"));
  const t = buildInterviewerInstructions({ ...base, focus: { issue: "Says we instead of I" } });
  assert.match(t, /PRACTICE FOCUS[^\n]*never mention it[^\n]*Says we instead of I/);
});

// ---- month analysis (insights.js)

const full = (o) => { const r = record(o); return { id: r.id, kind: "interview", at: r.at, summary: summarize(r), body: { ...r } }; };

test("patterns must point at real candidate answers; recurring needs two interviews, improved needs two in order", () => {
  const items = [full({ id: "a", at: day(1) }), full({ id: "b", at: day(3) })];
  const out = validateAnalysis({
    summary: "s", next_priorities: ["1", "2", "3", "4"],
    patterns: [
      { type: "recurring_weakness", group: "ownership", title: "Says we", detail: "d", drill: "x", evidence: [{ interview_id: "a", turn: 4 }, { interview_id: "b", turn: 4 }] },
      { type: "recurring_weakness", group: "ownership", title: "one only", detail: "d", drill: "x", evidence: [{ interview_id: "a", turn: 4 }, { interview_id: "a", turn: 6 }] },
      { type: "improved", group: "communication", title: "better", detail: "d", drill: "x", evidence: [{ interview_id: "a", turn: 2 }, { interview_id: "b", turn: 2 }] },
      { type: "strength", group: "communication", title: "interviewer turn", detail: "d", drill: "x", evidence: [{ interview_id: "a", turn: 1 }] },
      { type: "strength", group: "communication", title: "unknown interview", detail: "d", drill: "x", evidence: [{ interview_id: "zz", turn: 2 }] },
      { type: "strength", group: "made_up", title: "bad group", detail: "d", drill: "x", evidence: [{ interview_id: "a", turn: 2 }] },
    ],
    strong_answers: [{ interview_id: "b", turn: 6, why: "clear" }, { interview_id: "b", turn: 5, why: "interviewer" }],
  }, items);
  assert.deepEqual(out.patterns.map((p) => p.title), ["Says we", "better"]);
  assert.equal(out.patterns[0].interviews, 2);
  assert.equal(out.patterns[0].group_label, "Ownership");
  assert.deepEqual(out.strong_answers.map((a) => a.turn), [6]);
  assert.equal(out.next_priorities.length, 3);
});

test("analysis needs two interviews; with them it reads answers by turn, never the CV", async () => {
  let calls = 0, sent = null;
  const transport = async (_m, body) => { calls++; sent = JSON.parse(body); return new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify({ summary: "ok", patterns: [], strong_answers: [], next_priorities: ["a", "b", "c"] }) }] } }] })); };
  const one = await analyse({ items: [full({ id: "a" })], transport });
  assert.equal(one.enough, false);
  assert.equal(calls, 0);
  const cvRecord = full({ id: "b", at: day(2) });
  cvRecord.body.cv = "SECRET CV TEXT";
  const two = await analyse({ items: [full({ id: "a" }), cvRecord], transport, scope: "latest" });
  assert.equal(two.enough, true);
  assert.deepEqual(two.based_on, ["a", "b"]);
  const text = sent.contents[0].parts[0].text;
  assert.match(text, /\[turn 4\] We built a retry queue/);
  assert.ok(!text.includes("SECRET CV TEXT"));
  assert.equal(two.facts.interviews, 2);
});

test("which analyses are due: latest after new interviews, each finished week, the end-of-pass review", () => {
  const period = { start: day(1, 6), end: day(31, 6), current: true };
  const ivs = [S({ id: "a", at: day(2) }), S({ id: "b", at: day(3) }), S({ id: "c", at: day(9) })].map((s) => ({ ...s, kind: "interview" }));
  const now = new Date(day(10));
  const due = dueAnalyses({ summaries: ivs, analyses: [], periods: [period], now });
  assert.deepEqual(due.map((j) => j.scope + (j.week || "")), ["latest", "week1"]);
  const latestId = analysisId(period, "latest");
  const fresh = [{ id: latestId, at: day(9, 23), based_on: ["a", "b"] }, { id: analysisId(period, "week", 1), at: day(8) }];
  assert.deepEqual(dueAnalyses({ summaries: ivs, analyses: fresh, periods: [period], now }).map((j) => j.scope), [], "one new interview and a recent analysis: wait");
  const old = [{ id: latestId, at: day(9, 1), based_on: ["a", "b"] }, { id: analysisId(period, "week", 1), at: day(8) }];
  assert.deepEqual(dueAnalyses({ summaries: ivs, analyses: old, periods: [period], now: new Date(day(10, 14)) }).map((j) => j.scope), ["latest"]);
  const end = dueAnalyses({ summaries: ivs, analyses: fresh, periods: [period], now: new Date(day(30)) });
  assert.ok(end.some((j) => j.scope === "period"));
  assert.ok(!end.some((j) => j.scope === "week" && j.week === 1), "week 1 is saved already");
  assert.equal(dueAnalyses({ summaries: ivs.slice(0, 1), analyses: [], periods: [], now }).length, 0);
});

test("the downloadable month review says what the numbers say, and when there is too little", () => {
  const items = [S({ id: "a", at: day(1), score: 50 }), S({ id: "b", at: day(4), score: 64 })];
  const p = buildProgress(items, { period: { start: day(1, 6), end: day(31, 6) }, now: new Date(day(5)), timeZone: TZ });
  const text = monthReportText(p, { enough: true, facts: facts(items), summary: "Better structure.", next_priorities: ["x", "y", "z"],
    patterns: [{ title: "Says we", group_label: "Ownership", interviews: 2, detail: "In two answers", drill: "Use I" }] });
  assert.match(text, /first 50, latest 64/);
  assert.match(text, /Says we \(Ownership, 2 interviews\)/);
  assert.match(text, /not a prediction of any hiring decision/);
  assert.match(monthReportText(buildProgress([], { now: new Date(day(1)) }), null), /No full interview yet/);
});

// ---- answer one question again (redrill.js)

test("re-answering: the old answer comes from its own turns, the call stays on one question, the old score never moves", async () => {
  const rec = record();
  const src = redrillSource(rec, 0);
  assert.equal(src.before.text, "We built a retry queue and basically we cut failures by half.");
  assert.equal(src.before.score, 6);
  assert.equal(redrillSource(rec, 5), null);
  const brief = buildRedrillInstructions({ candidateName: "Riya", language: "English", voice: "Puck", source: src });
  assert.match(brief, /Walk me through the payment retry project/);
  assert.match(brief, /never ask a different question/i);
  assert.match(brief, /Arjun Nair/);
  assert.match(redrillNotes().opening, /ask the question/);
  assert.equal(redrillProgress({ plannedSeconds: 180, elapsedSeconds: 170 }).canWrapUp, true);
  assert.equal(redrillProgress({ plannedSeconds: 180, elapsedSeconds: 30 }).focus, "one_question");

  const call = [{ who: "interviewer", text: "Walk me through it?" }, { who: "candidate", text: "I designed the retry backoff myself and cut failures from 8% to 4%." }];
  const transport = async () => new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify({
    score_after: 8, answer_turns: [2, 1], improved: ["Says I designed"], still_missing: [], verdict: "Clearer ownership." }) }] } }] }));
  const out = await compareAnswers({ source: src, transcript: call, language: "English", transport });
  assert.deepEqual([out.result.score_before, out.result.score_after, out.result.change], [6, 8, 2]);
  assert.deepEqual(out.result.answer_turns, [2]);
  const item = redrillItem({ id: "rd-1", at: day(2), source: src, transcript: call, model: out.model, result: out.result, elapsed: 95 });
  assert.equal(item.kind, "redrill");
  assert.equal(item.summary.interview_id, "iv-1");
  assert.equal(item.body.after.text, call[1].text);
  assert.equal(item.body.source.before.better, "...", "the AI's suggested answer is kept apart from what they said");
});

test("the free demo before buying is day 0 of the first pass; a renewal starts where the last pass ended", () => {
  const demo = S({ id: "demo", at: day(1), score: 40, demo: true });
  const first = S({ id: "a", at: day(3), score: 55 });
  const p = buildProgress([demo, first], { period: { start: day(2), end: day(32), from: null }, now: new Date(day(4)), timeZone: TZ });
  assert.deepEqual(p.score.points.map((x) => x.id), ["demo", "a"]);
  assert.equal(p.score.change_since_first, 15);
  assert.equal(p.calendar[0].date, "2026-10-01", "the calendar starts on the demo day");
  const renewal = buildProgress([demo, first, S({ id: "b", at: day(33) })], { period: { start: day(40), end: day(70), from: day(32) }, now: new Date(day(41)), timeZone: TZ });
  assert.deepEqual(renewal.score.points.map((x) => x.id), ["b"]);
  assert.equal(buildProgress([demo, first], { period: { start: day(2), end: day(32) }, now: new Date(day(4)), timeZone: TZ }).totals.interviews, 1, "no from: the period starts at its start");
  assert.equal(reportChanges(first, [demo], { start: day(2), end: day(32), from: null }).score.since_first, 15);
});
