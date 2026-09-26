import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { validatePlan, PlanCoverage, normalizeRequirements, interviewContext, TARGET_LEVELS } from "../prep/app/interview-plan.js";
import { generateInterviewPlan } from "../prep/app/plan-request.js";
import { generateReport } from "../prep/app/report.js";
import { buildInterviewerInstructions } from "../prep/app/interviewer.js";
import { interviewProgress } from "../prep/app/assessment.js";
import { assessmentHtml, assessmentText } from "../prep/app/assessment-view.js";
import { computeMetrics } from "../prep/app/metrics.js";
import { GeminiLive } from "../prep/app/live.js";

function criterion(extra = {}) {
  return { label: "Database diagnosis", category: "problem_solving", priority: "essential",
    source_quote: "Must diagnose database performance", cv_evidence: "Improved SQL queries", cv_match: "direct",
    assessment_method: "interview", question: "How would you investigate a slow query?",
    followups: ["How would you check the improvement?"], next_assessment: "",
    criteria: { weak: "Names indexes without diagnosing the query.", adequate: "Uses a query plan to identify a bottleneck.", strong: "Justifies a change using the plan, weighs write costs and verifies with comparable measurements." }, ...extra };
}
const documents = { jd: "Must diagnose database performance. Prefer customer communication.", cv: "Improved SQL queries." };
const rawPlan = () => ({ role: "Backend engineer", level: "Mid-level", uncertainties: [], deferred_requirements: [], requirements: [criterion(), criterion({ label: "Customer communication", category: "communication", priority: "preferred", source_quote: "Prefer customer communication", cv_evidence: "", cv_match: "unknown", question: "How would you explain an incident to a customer?" })] });
const plan = () => validatePlan(rawPlan(), documents);
const progress = (elapsedSeconds = 250) => interviewProgress({ plannedSeconds: 600, elapsedSeconds });
const conversation = [
  { who: "interviewer", text: "How did you investigate the problem?" },
  { who: "candidate", text: "I checked the query plan and measured the slow join." },
  { who: "interviewer", text: "How did you verify the change?" },
  { who: "candidate", text: "I compared the same workload before and after the change." },
];

test("JD and CV references are verified; priorities cannot be manufactured from missing text", () => {
  const raw = rawPlan();
  raw.requirements.push(criterion({ label: "Invented leadership", source_quote: "Must manage ten people", cv_evidence: "Managed a team" }));
  const result = validatePlan(raw, documents);
  assert.equal(result.requirements[0].priority, "essential");
  assert.equal(result.requirements[0].weight, 2);
  assert.equal(result.requirements[1].weight, 1);
  assert.equal(result.requirements[2].priority, "inferred");
  assert.equal(result.requirements[2].source_quote, "");
  assert.equal(result.requirements[2].cv_match, "unknown");
  assert.equal(result.requirements[2].cv_evidence, "");
  assert.deepEqual(result.requirements.map(r => r.id), ["r1", "r2", "r3"]);
});

test("absent and vague JDs stay visibly uncertain, without lowering criteria to match the CV", () => {
  for (const jd of ["", "Join our exciting team"]) {
    const result = validatePlan(rawPlan(), { cv: "Student", jd });
    assert.ok(result.requirements.every(r => r.priority === "inferred" && r.cv_match === "unknown"));
    assert.equal(result.requirements[0].criteria.strong, criterion().criteria.strong);
    if (!jd) assert.match(result.uncertainties.join(" "), /No JD supplied/);
  }
});

test("no-JD role practice requires a confirmed role and level; general practice needs neither", () => {
  assert.throws(() => interviewContext({}), /enter the role/);
  assert.throws(() => interviewContext({ targetRole: "Accountant" }), /Choose the level/);
  for (const targetLevel of TARGET_LEVELS) {
    const context = interviewContext({ targetRole: "Accountant", targetLevel });
    assert.equal(context.mode, "role_baseline");
    assert.equal(context.targetLevel, targetLevel);
  }
  assert.equal(interviewContext({ practiceFocus: "general_cv" }).mode, "general_cv");
  assert.equal(interviewContext({ jd: "Target employer JD", targetRole: "Stale role from old form" }).targetRole, "");
});

test("no-JD plans cannot invent employer requirements or override the chosen career-change target", () => {
  const context = interviewContext({ targetRole: "Accountant", targetLevel: "Entry-level / fresher" });
  assert.throws(() => validatePlan({ ...rawPlan(), role: "Senior developer", level: "Manager" }, { cv: "Former sales associate", context }), /changed the chosen role/);
  const result = validatePlan({ ...rawPlan(), role: context.targetRole, level: context.targetLevel }, { cv: "Former sales associate", context });
  assert.equal(result.role, "Accountant");
  assert.equal(result.level, "Entry-level / fresher");
  assert.ok(result.requirements.every(r => r.priority === "inferred" && r.weight === 1 && !r.source_quote));
  const report = normalizeRequirements({}, result, []);
  assert.equal(report.overall_score, null);
  assert.match(report.assessment_scope, /No employer-specific suitability/);
  assert.deepEqual(report.unresolved_essentials, []);
});

test("general CV practice cannot inherit an invented occupation or seniority", () => {
  const context = interviewContext({ practiceFocus: "general_cv" });
  assert.throws(() => validatePlan(rawPlan(), { cv: "Student with a volunteer project", context }), /changed the chosen role/);
  const result = validatePlan({ ...rawPlan(), role: context.targetRole, level: context.targetLevel }, { cv: "Student with a volunteer project", context });
  assert.equal(result.role, "General CV practice");
  assert.equal(result.level, "No target seniority");
  assert.match(result.uncertainties.join(" "), /not a score for a specific job/);
});

test("malformed and overlong plans cannot start an interview without scoring criteria", () => {
  for (const raw of [null, {}, { requirements: [] }, { requirements: [null] }, { requirements: [criterion({ criteria: {} })] }, { requirements: Array(13).fill(criterion()) }]) {
    assert.throws(() => validatePlan(raw, documents));
  }
});

test("coverage changes with answer evidence and never forces a fixed question order", () => {
  const coverage = new PlanCoverage(plan());
  assert.equal(coverage.snapshot(progress()).question_opportunities[0].id, "r1");
  coverage.update([{ requirement_id: "r1", status: "covered", answer_quote: "checked the query plan" }], conversation);
  const next = coverage.snapshot(progress());
  assert.equal(next.question_opportunities[0].id, "r2");
  assert.equal(next.requirements[0].status, "covered");
  assert.deepEqual(next.requirements[0].evidence_turns, [2]);
  assert.match(next.guidance, /not a mandatory sequence/);
  assert.ok(coverage.snapshot(progress(20)).question_opportunities.length > 0); // no fixed-time lock after a completed intro
  assert.deepEqual(coverage.snapshot(progress(550)).question_opportunities, []);
});

test("invented quotes, interviewer words, cut-off answers and unknown criteria do not count as coverage", () => {
  const coverage = new PlanCoverage(plan());
  coverage.update([
    { requirement_id: "r1", status: "covered", answer_quote: "I implemented a cache" },
    { requirement_id: "r1", status: "covered", answer_quote: "How did you investigate" },
    { requirement_id: "invented", status: "covered", answer_quote: "checked the query plan" },
    { requirement_id: "r1", status: "covered", answer_quote: "" },
  ], conversation);
  coverage.update([{ requirement_id: "r1", status: "covered", answer_quote: "checked the query plan" }], conversation.map(t => ({ ...t, interrupted: true })));
  assert.ok(coverage.snapshot(progress()).requirements.every(r => r.status === "pending"));
});

test("repeated tool calls do not create extra evidence or an endless follow-up loop", () => {
  const coverage = new PlanCoverage(plan());
  const first = { requirement_id: "r1", status: "needs_followup", answer_quote: "checked the query plan" };
  coverage.update([first, first], conversation);
  assert.equal(coverage.snapshot(progress()).requirements[0].evidence_turns.length, 1);
  coverage.update([{ ...first, answer_quote: "compared the same workload" }], conversation);
  assert.ok(!coverage.snapshot(progress()).question_opportunities.some(r => r.id === "r1"));
  assert.equal(coverage.snapshot(progress()).requirements[0].status, "needs_followup");
});

test("weighted scores use pre-interview priorities and keep unresolved essentials visible", () => {
  const result = normalizeRequirements({ requirements: [
    { id: "r1", status: "assessed", score: 4, weight: 0, priority: "preferred", evidence_turns: [2] },
    { id: "r2", status: "assessed", score: 10, weight: 100, evidence_turns: [4] },
    { id: "invented", status: "assessed", score: 10, evidence_turns: [2] },
  ] }, plan(), conversation);
  assert.equal(result.overall_score, 60);
  assert.equal(result.requirements.length, 2);
  assert.equal(result.requirements[0].weight, 2);
  assert.match(result.unresolved_essentials[0], /Below expected level/);
});

test("missing essential evidence stays unresolved even when assessed preferred skills score highly", () => {
  const result = normalizeRequirements({ requirements: [{ id: "r2", status: "assessed", score: 9, evidence_turns: [4] }] }, plan(), conversation);
  assert.equal(result.overall_score, 90);
  assert.match(result.coverage, /1 of 2/);
  assert.match(result.assessment_scope, /Partial assessment/);
  assert.match(result.unresolved_essentials[0], /Not assessed/);
});

test("work-sample abilities cannot be certified by a high spoken-answer score", () => {
  const raw = rawPlan();
  raw.requirements[0].assessment_method = "work_sample";
  raw.requirements[0].next_assessment = "Execute and verify a query against a provided dataset.";
  const result = normalizeRequirements({ requirements: [{ id: "r1", status: "assessed", score: 9, evidence_turns: [2] }] }, validatePlan(raw, documents), conversation);
  assert.equal(result.requirements[0].status, "limited");
  assert.equal(result.requirements[0].outcome, "Partially demonstrated");
  assert.match(result.unresolved_essentials[0], /practical assessment required/);
  assert.match(assessmentText(result), /Execute and verify/);
  assert.match(assessmentHtml(result, conversation), /Practical assessment still needed/);
});

function modelResponse(raw) { return { ok: true, json: async () => ({ candidates: [{ content: { parts: [{ text: JSON.stringify(raw) }] } }] }) }; }

test("planner sends role-specific source documents, duration and evidence criteria before the call", async ctx => {
  const cases = [
    { role: "Backend engineer", ...documents, label: "Database diagnosis", quote: criterion().source_quote },
    { role: "Sales associate", jd: "Must understand customer needs", cv: "Discussed customer requirements during a retail internship", label: "Customer discovery", quote: "Must understand customer needs" },
    { role: "Graduate accountant", jd: "Must reconcile financial records", cv: "Completed a coursework reconciliation exercise", label: "Reconciliation reasoning", quote: "Must reconcile financial records" },
  ];
  for (const example of cases) {
    let request;
    const raw = { ...rawPlan(), role: example.role, requirements: [criterion({ label: example.label, source_quote: example.quote, cv_evidence: example.cv })] };
    ctx.mock.method(globalThis, "fetch", async (_url, options) => { request = JSON.parse(options.body); return modelResponse(raw); });
    const result = await generateInterviewPlan({ apiKey: "test", ...example, minutes: 18, language: "Hinglish" });
    assert.equal(result.role, example.role);
    assert.equal(result.requirements[0].label, example.label);
    const source = JSON.parse(request.contents[0].parts[0].text);
    assert.equal(source.selectedMinutes, 18);
    assert.equal(source.jd, example.jd);
    assert.equal(source.cv, example.cv);
    assert.equal(source.language, "Hinglish");
    assert.match(request.systemInstruction.parts[0].text, /Missing CV information means unknown/);
    assert.match(request.systemInstruction.parts[0].text, /Names|name tools|naming tools|name|listing|Weak answers/i);
    ctx.mock.restoreAll();
  }
});

test("no-JD planner receives the confirmed target or explicitly selected general mode", async ctx => {
  let request;
  ctx.mock.method(globalThis, "fetch", async (_url, options) => { request = JSON.parse(options.body); const context = JSON.parse(request.contents[0].parts[0].text).context; return modelResponse({ ...rawPlan(), role: context.targetRole, level: context.targetLevel }); });
  const options = { apiKey: "test", cv: "Sales experience, changing careers", minutes: 8, targetRole: "Accountant", targetLevel: "Entry-level / fresher" };
  const targeted = await generateInterviewPlan(options);
  assert.equal(JSON.parse(request.contents[0].parts[0].text).context.targetRole, "Accountant");
  assert.equal(targeted.role, "Accountant");
  assert.match(request.systemInstruction.parts[0].text, /career changer must be interviewed for the chosen new role/);
  const general = await generateInterviewPlan({ ...options, practiceFocus: "general_cv" });
  assert.equal(general.mode, "general_cv");
  assert.equal(general.role, "General CV practice");
  assert.match(request.systemInstruction.parts[0].text, /missing skills from an imagined job must not become weaknesses/);
});

test("invalid planner output retries, while quota failure ends without a fake generic plan", async ctx => {
  let calls = 0;
  ctx.mock.method(globalThis, "fetch", async () => ++calls === 1 ? modelResponse({}) : modelResponse(rawPlan()));
  assert.equal((await generateInterviewPlan({ apiKey: "test", ...documents })).requirements.length, 2);
  assert.equal(calls, 2);
  ctx.mock.restoreAll();
  ctx.mock.method(globalThis, "fetch", async () => ({ ok: false, status: 429 }));
  await assert.rejects(generateInterviewPlan({ apiKey: "test", ...documents }), /Could not create a complete assessment plan/);
});

test("cancelled planning does not contact a model", async ctx => {
  const controller = new AbortController(); controller.abort();
  let calls = 0;
  ctx.mock.method(globalThis, "fetch", async () => { calls++; return modelResponse(rawPlan()); });
  await assert.rejects(generateInterviewPlan({ apiKey: "test", ...documents, signal: controller.signal }), { name: "AbortError" });
  assert.equal(calls, 0);
});

test("the live clock tool accepts coverage evidence and returns dynamic opportunities after reconnect", () => {
  const coverage = new PlanCoverage(plan());
  let live;
  live = new GeminiLive({ apiKey: "test", instructions: () => "Test", getInterviewProgress: args => {
    coverage.update(args?.updates, live.transcript.turns);
    return { ...progress(), coverage: coverage.snapshot(progress()) };
  } });
  const sent = []; live._sendJson = payload => { sent.push(payload); return true; };
  live._handle({ setupComplete: {} });
  for (const t of conversation) { live.transcript.append(t.who, t.text, 1); live.transcript.close(t.who); }
  live._handle({ toolCall: { functionCalls: [{ id: "coverage", name: "get_interview_progress", args: { updates: [{ requirement_id: "r1", status: "covered", answer_quote: "checked the query plan" }] } }] } });
  assert.equal(sent.at(-1).toolResponse.functionResponses[0].response.coverage.question_opportunities[0].id, "r2");
  live._disconnect();
  assert.match(live._setupMessage().setup.systemInstruction.parts[0].text, /"status":"covered"/);
  live.close();
});

test("report uses the prepared rubric and dynamic IDs rather than re-planning after answers", async ctx => {
  let request;
  ctx.mock.method(globalThis, "fetch", async (_url, options) => { request = JSON.parse(options.body); return modelResponse({ requirements: [{ id: "r1", status: "assessed", score: 4, evidence_turns: [2], explanation: "No verification evidence." }] }); });
  const result = await generateReport({ apiKey: "test", ...documents, transcript: conversation, metrics: computeMetrics([], []), minutes: 10, assessmentPlan: plan() });
  assert.deepEqual(request.generationConfig.responseSchema.properties.requirements.items.properties.id.enum, ["r1", "r2"]);
  assert.ok(!request.generationConfig.responseSchema.required.includes("competencies"));
  assert.match(request.contents[0].parts[0].text, /Names indexes without diagnosing/);
  assert.match(request.contents[0].parts[0].text, /listing plausible tools.*not strong evidence/);
  assert.equal(result.report.overall_score, 40);
  assert.equal(result.report.requirements[1].score, null);
});

test("interviewer instructions make question choice dynamic while keeping scoring criteria stable", () => {
  const text = buildInterviewerInstructions({ cv: documents.cv, jd: documents.jd, assessmentPlan: plan() });
  assert.match(text, /Choose WHEN to probe and WHAT to ask dynamically/);
  assert.match(text, /never a script to recite or a fixed sequence/);
  assert.match(text, /FIRST question must invite a brief self-introduction/);
  assert.match(text, /Database diagnosis/);
});

// Execute the actual app's preparation/cancellation functions with fake UI,
// audio and transport. No credentials, payment, microphone or network access.
function preparationHarness(generate, extra = {}) {
  const source = readFileSync(new URL("../prep/app/app.js", import.meta.url), "utf8");
  const nodes = new Map();
  const context = vm.createContext({
    hidePreparation() {}, showPreparation() {},
    phase: "miccheck", planController: null, assessmentPlan: null, planCoverage: null,
    // The free demo (billing.js): off unless a test turns it on.
    demo: null, requestDemo: async () => ({ ok: false, reason: "unavailable" }), demoTransport: (id) => ({ demoId: id }),
    // The Groq backup for pass holders (billing.js backupTransport): none unless a test supplies one.
    passBackup: () => undefined,
    demoUsed: { set() { context.demoMarked = true; } }, passCtx: { passesOn: false }, openPasses(text) { context.passes = text; },
    showDemoFull() { context.fullChoice = true; },
    S: { key: "test", cv: documents.cv, jd: documents.jd, minutes: 12, ent: { kind: "trial", secondsLeft: 1200 } },
    AbortController, generateInterviewPlan: generate, PlanCoverage,
    entitlement: async () => ({ kind: "trial", secondsLeft: 1200 }),
    $: id => { if (!nodes.has(id)) nodes.set(id, { style: {} }); return nodes.get(id); },
    setLink() {}, setCaption() {}, micHelpTimer: null, clearTimeout() {},
    audio: { stop: async () => {} }, preLive() { context.phase = "idle"; },
    notice(_id, message) { context.error = message; },
    nowS: () => 100, log() {}, track() {}, wheel: { setState() {} },
    buildInterviewerInstructions, currentProgress: () => ({}), onTranscript() {},
    GeminiLive: class { constructor(o) { context.liveOptions = o; } start() { context.started = true; } },
    setInterval() { context.timerStarted = true; return 1; }, onSecond() {},
    ...extra,
  });
  vm.runInContext(source.slice(source.indexOf("async function cancelMicCheck()"), source.indexOf("function currentProgress(")), context);
  return context;
}

test("preparation does not start the clock or socket until the plan is ready", async () => {
  let resolve;
  const ctx = preparationHarness(() => new Promise(r => { resolve = r; }));
  const pending = ctx.startCall();
  assert.equal(ctx.phase, "preparing");
  assert.equal(ctx.started, undefined);
  assert.equal(ctx.timerStarted, undefined);
  resolve(plan()); await pending;
  assert.equal(ctx.started, true);
  assert.equal(ctx.timerStarted, true);
  assert.equal(ctx.plannedSeconds, 720);
});

test("cancelling preparation prevents a late model response from starting the interview", async () => {
  let resolve;
  const ctx = preparationHarness(() => new Promise(r => { resolve = r; }));
  const pending = ctx.startCall();
  await ctx.cancelMicCheck();
  resolve(plan()); await pending;
  assert.equal(ctx.phase, "idle");
  assert.equal(ctx.started, undefined);
});

test("planning failure leaves practice time untouched and offers retry", async () => {
  const ctx = preparationHarness(async () => { throw new Error("Temporary failure"); });
  await ctx.startCall();
  assert.equal(ctx.started, undefined);
  assert.equal(ctx.phase, "idle");
  assert.match(ctx.error, /timer did not start/);
});

test("an entitlement that expires during preparation cannot start a call", async () => {
  const ctx = preparationHarness(async () => plan());
  ctx.entitlement = async () => ({ kind: "none", secondsLeft: 0 });
  await ctx.startCall();
  assert.equal(ctx.started, undefined);
  assert.equal(ctx.timerStarted, undefined);
  assert.match(ctx.error, /expired/);
});

test("duplicate microphone events cannot launch concurrent planners", async () => {
  let resolve, calls = 0;
  const ctx = preparationHarness(() => { calls++; return new Promise(r => { resolve = r; }); });
  const first = ctx.startCall();
  await ctx.startCall();
  assert.equal(calls, 1);
  resolve(plan()); await first;
  assert.equal(ctx.started, true);
});

test("no-JD controls follow pasted/removed JD and general-practice selection", () => {
  const source = readFileSync(new URL("../prep/app/app.js", import.meta.url), "utf8");
  const nodes = Object.fromEntries(["jd", "practice-focus", "no-jd-options", "target-details", "no-jd-help"].map(id => [id, { value: "", style: {} }]));
  nodes["practice-focus"].value = "role";
  const ctx = vm.createContext({ $: id => nodes[id] });
  vm.runInContext(source.slice(source.indexOf("function updateNoJdOptions()"), source.indexOf('$("jd").oninput')), ctx);
  ctx.updateNoJdOptions();
  assert.equal(nodes["no-jd-options"].hidden, false);
  assert.equal(nodes["target-details"].style.display, "");
  nodes.jd.value = "An employer job description";
  ctx.updateNoJdOptions();
  assert.equal(nodes["no-jd-options"].hidden, true);
  nodes.jd.value = " "; nodes["practice-focus"].value = "general_cv";
  ctx.updateNoJdOptions();
  assert.equal(nodes["no-jd-options"].hidden, false);
  assert.equal(nodes["target-details"].style.display, "none");
  assert.match(nodes["no-jd-help"].textContent, /does not assess suitability/);
});


test("the free demo plans through the licence server and calls with a one-time token, for 7 minutes", async () => {
  let planArgs;
  const ctx = preparationHarness(async (a) => { planArgs = a; return plan(); }, {
    requestDemo: async () => ({ ok: true, demo: "d".repeat(24), token: "auth_tokens/abc", seconds: 420 }),
  });
  ctx.S.key = ""; ctx.S.ent = { kind: "demo", secondsLeft: 420 };
  await ctx.startCall();
  assert.deepEqual(planArgs.transport, { demoId: "d".repeat(24) });
  assert.equal(ctx.liveOptions.authToken, "auth_tokens/abc");
  assert.equal(ctx.plannedSeconds, 420);
  assert.equal(ctx.demoMarked, undefined);     // only a finished report uses the demo up; a busy Google must not
  assert.equal(ctx.started, true);
});

test("a refused demo never prepares or calls, and says so without mentioning a key", async () => {
  let planned = false;
  const ctx = preparationHarness(async () => { planned = true; return plan(); }, {
    requestDemo: async () => ({ ok: false, reason: "day_full" }),
  });
  ctx.S.key = ""; ctx.S.ent = { kind: "demo", secondsLeft: 420 };
  await ctx.startCall();
  assert.equal(planned, false);
  assert.equal(ctx.started, undefined);
  assert.match(ctx.error, /free demos are all used up/);
  assert.doesNotMatch(ctx.error, /key/i);
});

test("when both demo keys are full, the visitor is offered a choice and nothing is prepared or used up", async () => {
  let planned = false;
  const ctx = preparationHarness(async () => { planned = true; return plan(); }, {
    requestDemo: async () => ({ ok: false, reason: "full", retry_after: 60 }),
  });
  ctx.S.key = ""; ctx.S.ent = { kind: "demo", secondsLeft: 420 };
  await ctx.startCall();
  assert.equal(ctx.fullChoice, true);
  assert.equal(planned, false);
  assert.equal(ctx.started, undefined);
  assert.equal(ctx.demoMarked, undefined);
});

// Owner, 26 Sep 2026: Gemini stays first; the licence server's Groq backup writes the plan or report only when
// both Gemini models have failed on a pass holder's own key.
test("the backup writes the plan only after both Gemini models fail, and never when Gemini answers", async ctx => {
  const bodies = [];
  const backup = async (body) => { bodies.push(JSON.parse(body)); return modelResponse(rawPlan()); };
  ctx.mock.method(globalThis, "fetch", async () => ({ ok: false, status: 503 }));
  assert.equal((await generateInterviewPlan({ apiKey: "test", ...documents, backup })).requirements.length, 2);
  assert.equal(bodies.length, 1);
  assert.ok(bodies[0].generationConfig.responseSchema, "the backup gets the exact plan format");
  ctx.mock.restoreAll();
  ctx.mock.method(globalThis, "fetch", async () => modelResponse(rawPlan()));
  await generateInterviewPlan({ apiKey: "test", ...documents, backup });
  assert.equal(bodies.length, 1, "Gemini answered, so the backup was not asked");
});

test("the backup writes the report when Gemini fails or hangs on both models, and a failed backup keeps Gemini's error", async ctx => {
  const report = { requirements: [{ id: "r1", status: "assessed", score: 6, evidence_turns: [2], explanation: "Checked the plan." }] };
  ctx.mock.method(globalThis, "fetch", async () => { throw Object.assign(new Error("The operation was aborted due to timeout"), { name: "TimeoutError" }); });
  const backed = await generateReport({ apiKey: "test", ...documents, transcript: conversation, metrics: computeMetrics([], []), minutes: 10,
    assessmentPlan: plan(), backup: async () => { const r = modelResponse(report); r.json = async () => ({ ...(await modelResponse(report).json()), served_by: "openai/gpt-oss-120b" }); return r; } });
  assert.equal(backed.model, "openai/gpt-oss-120b");
  assert.equal(backed.report.requirements[0].score, 6);
  await assert.rejects(generateReport({ apiKey: "test", ...documents, transcript: conversation, metrics: computeMetrics([], []), minutes: 10,
    assessmentPlan: plan(), backup: async () => ({ ok: false, status: 429 }) }), /Gemini unreachable/);
});
