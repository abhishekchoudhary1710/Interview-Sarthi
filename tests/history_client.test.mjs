// history.js in the browser: consent, saving with retry, the local list, delete, export and import (29 Sep 2026).
import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";

// A browser's storage and a fake licence server, before the module is loaded.
const storage = new Map();
globalThis.localStorage = {
  getItem: (k) => (storage.has(k) ? storage.get(k) : null),
  setItem: (k, v) => storage.set(k, String(v)),
  removeItem: (k) => storage.delete(k),
};
const server = { prefs: { enabled: false }, items: new Map(), down: false, calls: [], passLive: true };
globalThis.fetch = async (url, init) => {
  const path = new URL(url).pathname, body = JSON.parse(init.body);
  server.calls.push(path);
  const reply = (status, data) => new Response(JSON.stringify(data), { status });
  if (server.down) return reply(503, { error: "server error" });
  if (body.session !== "S1") return reply(401, { error: "Sign in first." });
  if (path === "/mock/history/prefs") {
    if (typeof body.enabled === "boolean") server.prefs = { enabled: body.enabled };
    return reply(200, { ...server.prefs, retention_days: 365, pass: { live: server.passLive } });
  }
  if (path === "/mock/history/save") {
    if (!server.prefs.enabled) return reply(409, { error: "History is switched off." });
    if (!server.passLive) return reply(403, { error: "No live pass." });
    server.items.set(body.item.id, body.item);
    return reply(200, { saved: true });
  }
  if (path === "/mock/history/list") {
    let all = [...server.items.values()].sort((a, b) => (a.at < b.at ? 1 : -1));
    if (body.before) all = all.filter((i) => i.at < body.before);
    const limit = body.bodies ? 2 : 500;
    return reply(200, { items: all.slice(0, limit).map((i) => ({ id: i.id, kind: i.kind, at: i.at, summary: i.summary, ...(body.bodies ? { body: i.body } : {}) })),
      more: all.length > limit, prefs: server.prefs, periods: [{ start: "2026-10-01T00:00:00.000Z", end: "2026-10-31T00:00:00.000Z", current: true }] });
  }
  if (path === "/mock/history/get") return reply(200, { items: body.ids.map((id) => server.items.get(id)).filter(Boolean) });
  if (path === "/mock/history/delete") {
    if (body.all) { const n = server.items.size; server.items.clear(); return reply(200, { deleted: n }); }
    return reply(200, { deleted: server.items.delete(body.id) ? 1 : 0 });
  }
  return reply(404, { error: "not found" });
};

const H = await import("../prep/app/history.js");
const { session } = await import("../prep/app/billing.js?v=20260927-invite");

const transcript = [{ who: "interviewer", text: "Q?", start: 0, end: 2 }, { who: "candidate", text: "My answer here.", start: 3, end: 40 }];
const record = (id, at = "2026-10-02T10:00:00.000Z") => ({
  id, at, elapsed: 600, language: "English", model: "gemini-3.6-flash", rubric: "2026-09-29",
  report: { overall_score: 60, requirements: [{ id: "r1", category: "communication", score: 6 }], plan: { mode: "role_baseline", role: "Analyst", level: "Entry-level / fresher" }, questions: [] },
  metrics: { avgWpm: 120, answers: [{ text: "My answer here.", words: 3, seconds: 37 }], candidateTalkSeconds: 37, interviewerTalkSeconds: 2 },
  transcript,
});
const states = [];
H.HISTORY_EVENTS.addEventListener("status", (e) => states.push(`${e.detail.id}:${e.detail.state}`));

beforeEach(() => {
  storage.clear(); server.prefs = { enabled: false }; server.items.clear(); server.down = false; server.calls = []; server.passLive = true;
  states.length = 0;
});

test("signed out or with history off, nothing leaves the browser; the local list still grows", async () => {
  assert.equal((await H.saveInterview(record("iv-1"))).state, "signed_out");
  session.set("S1");
  assert.equal((await H.saveInterview(record("iv-2"))).state, "off");
  assert.equal(server.items.size, 0);
  assert.ok(!server.calls.includes("/mock/history/save"));
  assert.deepEqual(H.localSummaries().map((s) => s.id), ["iv-2", "iv-1"]);
});

test("with history on a report is saved with its transcript, never the CV, and without duplicate answer text", async () => {
  session.set("S1");
  await H.setEnabled(true);
  const r = { ...record("iv-1"), cv: "MY CV" };
  const { state, summary } = await H.saveInterview(r);
  assert.equal(state, "saved");
  assert.deepEqual(states.slice(-2), ["iv-1:saving", "iv-1:saved"]);
  const saved = server.items.get("iv-1");
  assert.equal(saved.kind, "interview");
  assert.equal(saved.summary.score, summary.score);
  assert.equal(saved.body.transcript[1].text, "My answer here.");
  assert.equal(saved.body.metrics.answers[0].text, undefined);
  assert.ok(!JSON.stringify(saved).includes("MY CV"));
  assert.equal(H.statusOf("iv-1").state, "saved");
});

test("a save that cannot reach the server waits in the outbox and goes when it can", async () => {
  session.set("S1");
  await H.setEnabled(true);
  server.down = true;
  assert.equal((await H.saveInterview(record("iv-1"))).state, "retry");
  assert.deepEqual(H.pending(), ["iv-1"]);
  server.down = false;
  assert.equal(await H.flushOutbox(), 1);
  assert.deepEqual(H.pending(), []);
  assert.ok(server.items.has("iv-1"));
});

test("history switched off elsewhere, or a pass that ended: the page is told, and nothing is retried forever", async () => {
  session.set("S1");
  await H.setEnabled(true);
  server.prefs = { enabled: false };                     // switched off on another device
  assert.equal((await H.saveInterview(record("iv-1"))).state, "off");
  assert.deepEqual(H.pending(), []);
  await H.setEnabled(true);
  server.passLive = false;
  assert.equal((await H.saveInterview(record("iv-2"))).state, "no_pass");
  assert.deepEqual(H.pending(), []);
});

test("the list merges the account with this browser; deleting removes every copy", async () => {
  session.set("S1");
  assert.equal((await H.saveInterview(record("iv-local", "2026-10-01T09:00:00.000Z"))).state, "off");
  await H.setEnabled(true);
  await H.saveInterview(record("iv-1"));
  localStorage.setItem("ps_last_report", JSON.stringify(record("iv-1")));
  const list = await H.listSummaries();
  assert.equal(list.source, "account");
  assert.deepEqual(list.items.map((s) => [s.id, !!s.local_only]), [["iv-1", false], ["iv-local", true]]);
  assert.equal(list.periods[0].current, true);
  assert.deepEqual(H.knownSummaries().map((s) => s.id).sort(), ["iv-1", "iv-local"]);
  assert.equal((await H.getInterview("iv-1")).transcript[1].text, "My answer here.");
  assert.equal(await H.deleteItem("iv-1"), 1);
  assert.equal(localStorage.getItem("ps_last_report"), null);
  assert.deepEqual((await H.listSummaries()).items.map((s) => s.id), ["iv-local"]);
  await H.deleteAll();
  assert.deepEqual((await H.listSummaries()).items, []);
  assert.equal((await H.getPrefs()).enabled, true, "the setting is not touched");
});

test("offline, the last account list is used", async () => {
  session.set("S1");
  await H.setEnabled(true);
  await H.saveInterview(record("iv-1"));
  await H.listSummaries();
  server.down = true;
  const list = await H.listSummaries();
  assert.equal(list.source, "cache");
  assert.deepEqual(list.items.map((s) => s.id), ["iv-1"]);
});

test("export pages through every saved interview and adds what only this browser has", async () => {
  session.set("S1");
  await H.setEnabled(true);
  for (const n of [1, 2, 3]) await H.saveInterview(record(`iv-${n}`, `2026-10-0${n}T10:00:00.000Z`));
  localStorage.setItem("ps_history", JSON.stringify([...JSON.parse(localStorage.getItem("ps_history")), { at: "2026-09-20T10:00:00.000Z", score: 41, elapsed: 420 }]));
  const { json, text } = await H.exportAll();
  assert.deepEqual(json.items.map((i) => i.id), ["iv-l-20260920T100000000Z", "iv-1", "iv-2", "iv-3"]);
  assert.equal(json.items[0].local_only, true);
  assert.equal(json.items[3].body.transcript[1].text, "My answer here.");
  assert.match(text, /You: My answer here\./);
  assert.match(text, /Only the score was kept/);
});

test("the one full report a browser kept from before can be added to the account, once", async () => {
  session.set("S1");
  const old = record(undefined, "2026-09-27T08:00:00.000Z");
  delete old.id;
  localStorage.setItem("ps_last_report", JSON.stringify(old));
  assert.equal(H.importable().length, 1);
  await H.setEnabled(true);
  await H.listSummaries();
  const res = await H.importLocal();
  assert.deepEqual(res, [{ id: "iv-l-20260927T080000000Z", state: "saved" }]);
  await H.listSummaries();
  assert.equal(H.importable().length, 0);
  // a locked demo report is not offered until a pass unlocks it
  localStorage.setItem("ps_last_report", JSON.stringify({ ...record("iv-demo"), locked: true }));
  assert.equal(H.importable().length, 0);
});

test("a server without the history endpoints fails the save once instead of retrying forever", async () => {
  session.set("S1");
  await H.setEnabled(true);
  const real = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify({ error: "not found" }), { status: 404 });
  try {
    assert.equal((await H.saveInterview(record("iv-1"))).state, "failed");
    assert.deepEqual(H.pending(), []);
  } finally { globalThis.fetch = real; }
});
