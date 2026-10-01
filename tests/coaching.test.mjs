// What a pass holder's interviewer is told about their earlier practice (prep/app/coaching.js).
// Run: node --test tests/coaching.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { coachingBrief, COACHING } from "../prep/app/coaching.js";
import { trackKey } from "../prep/app/progress.js";

const now = new Date("2026-10-01T10:00:00Z");
const ago = (days) => new Date(now.getTime() - days * 86400_000).toISOString();
const ROLE = trackKey({ mode: "role_baseline", role: "Accountant", level: "Entry-level / fresher" });
const OTHER = trackKey({ mode: "role_baseline", role: "Data analyst", level: "Individual contributor" });
const interview = (o) => ({ kind: "interview", at: ago(1), minutes: 12, demo: false, track: ROLE, score: 60, groups: {}, questions: [], ...o });

test("nothing to say without real earlier interviews on this track", () => {
  assert.equal(coachingBrief([], { track: ROLE, now }), "");
  assert.equal(coachingBrief([interview({ demo: true }), interview({ minutes: 1 }), interview({ track: OTHER }), interview({ at: ago(90) })], { track: ROLE, now }), "");
});

test("scores, the weakest two areas and recent questions come from this track only, oldest score first", () => {
  const items = [
    interview({ at: ago(5), score: 52, groups: { communication: { score: 5 }, ownership: { score: 4 }, problem_solving: { score: 8 } },
      questions: [{ q: "Tell me about yourself." }, { q: "How do you reconcile accounts?" }] }),
    interview({ at: ago(2), score: 61, groups: { communication: { score: 6 }, ownership: { score: 5 }, problem_solving: { score: 8 } },
      questions: [{ q: "Tell me about yourself." }, { q: "Walk me through a month-end close." }] }),
    interview({ at: ago(1), track: OTHER, score: 90, questions: [{ q: "Explain a SQL join." }] }),
  ];
  const brief = coachingBrief(items, { track: ROLE, now });
  assert.match(brief, /oldest first: 52 -> 61/);
  assert.match(brief, /Weakest areas so far: Ownership \(4\.5\/10\), Communication \(5\.5\/10\)/);
  assert.doesNotMatch(brief, /Problem solving/, "an area already at 8/10 is not called weak");
  assert.match(brief, /Keep the usual opening introduction[^\n]*\n- Walk me through a month-end close\.\n- How do you reconcile accounts\?/, "newest interview first, each question once");
  assert.doesNotMatch(brief, /- Tell me about yourself/, "the opening introduction is never listed as already asked");
  assert.doesNotMatch(brief, /SQL join|90/, "another role's interview stays out");
});

test("difficulty follows the trend: deeper follow-ups when scores rise, gentler questions when they are low", () => {
  const rising = coachingBrief([interview({ at: ago(3), score: 58 }), interview({ at: ago(1), score: 74 })], { track: ROLE, now });
  assert.match(rising, /ask one deeper follow-up/);
  const low = coachingBrief([interview({ score: 38 })], { track: ROLE, now });
  assert.match(low, /keep questions accessible/);
});

test("a pasted JD (track unknown) uses every recent interview, but not role knowledge learnt for another job", () => {
  const items = [interview({ track: OTHER, groups: { role_knowledge: { score: 2 }, collaboration: { score: 5 } } })];
  const brief = coachingBrief(items, { track: null, now });
  assert.match(brief, /Collaboration \(5\.0\/10\)/);
  assert.doesNotMatch(brief, /Role knowledge/);
});

test("recurring patterns from a recent month analysis are added; improvements and strengths are not", () => {
  const analysis = { kind: "analysis", at: ago(3), enough: true, patterns: [
    { type: "improved", title: "Gives numbers now" }, { type: "recurring_weakness", title: "Says we instead of I" },
    { type: "strength", title: "Clear structure" }, { type: "inconsistent", title: "Examples come and go" },
  ] };
  const brief = coachingBrief([interview({}), analysis], { track: ROLE, now });
  assert.match(brief, /Patterns seen across interviews: Says we instead of I; Examples come and go\./);
  assert.doesNotMatch(brief, /Gives numbers now|Clear structure/);
  assert.doesNotMatch(coachingBrief([interview({}), { ...analysis, at: ago(45) }], { track: ROLE, now }), /Patterns/, "an old analysis is left out");
});

test("the brief stays short however long the history", () => {
  const long = "Q".repeat(400);
  const items = Array.from({ length: 12 }, (_, i) => interview({ at: ago(i + 1), questions: Array.from({ length: 8 }, (_, k) => ({ q: `${long} ${i}-${k}` })) }));
  const brief = coachingBrief(items, { track: ROLE, now });
  assert.ok(brief.length <= COACHING.MAX_CHARS);
  assert.ok((brief.match(/^- /gm) || []).length <= COACHING.QUESTIONS);
});
