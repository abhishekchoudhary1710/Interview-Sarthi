/* Prep Sarthi: the app page. Four screens: CV, key, interview, report.
 *
 * All state lives in this browser. The CV text and the key go to Google only
 * when the interview starts; a hash of the key goes to the licence server for
 * the free-minutes counter. Timing is hard: when the planned time or the free
 * minutes run out, the interview ends that second and the report is written.
 *
 * The interview screen is a call, not a chat: the Sarthi wheel turns while the
 * interviewer speaks, only their current line is shown, and the full transcript
 * waits for the report. The chosen voice decides whether the page calls the
 * interviewer she or he: see interviewerPersona.
 */

import { AudioIO } from "./audio.js";
import { GeminiLive } from "./live.js?v=20260925-demo";
import { buildInterviewerInstructions, interviewerPersona } from "./interviewer.js?v=20260923-jd-plan";
import { readDocFile, tidy, guessName } from "./cv.js";
import { computeMetrics } from "./metrics.js";
import { generateReport } from "./report.js?v=20260925-demo";
import { interviewProgress } from "./assessment.js";
import { assessmentHtml, assessmentText } from "./assessment-view.js?v=20260923-jd-plan";
import { generateInterviewPlan } from "./plan-request.js?v=20260925-demo";
import { PlanCoverage, interviewContext } from "./interview-plan.js";
import { keyHash, entitlement, entitlementBySession, tick, rememberInvite, rememberSource, requestDemo, demoTransport, demoUsed } from "./billing.js?v=20260925-demo";
import { initPasses, openPasses, renderInvite } from "./pass.js?v=20260925-demo";
import { Wheel } from "../wheel.js";
import { VoiceGate, MIC_HELP } from "./miccheck.js";

const $ = (id) => document.getElementById(id);
// Technical output is available only when support explicitly requests this URL.
// Keep it hidden in the HTML too, so it never flashes during normal page loading.
const diagnosticsEnabled = new URLSearchParams(location.search).get("diagnostics") === "1";
$("diagnostics").hidden = !diagnosticsEnabled;
const store = {
  get(k, d = "") { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (_) { /* private mode */ } },
  del(k) { try { localStorage.removeItem(k); } catch (_) { /* ignore */ } },
};
const track = (name, params) => { try { if (window.gtag) window.gtag("event", name, params || {}); } catch (_) { /* analytics off */ } };
const nowS = () => performance.now() / 1000;
const TICK_SECONDS = 30;
const VOICE_RMS = 0.005;
const BAR_SHAPE = [0.55, 1, 0.75, 0.95, 0.5];
const MIC_MUTED_RMS = 0.00002;   // exact digital silence: a mute key or a dead input
const LOW_FREE_SECONDS = 5 * 60;      // when the pass offer appears during a free interview

const S = { cv: "", jd: "", practiceFocus: "role", targetRole: "", targetLevel: "", name: "", language: "English", minutes: 12, voice: "Kore", key: "", hash: "", ent: null, plan: "w" };
let lastScreen = "s-cv";
let assessmentPlan = null, planCoverage = null, planController = null;
let audio = null, live = null, timer = null, startedAt = 0, plannedSeconds = 0, ending = false;
let voiceLog = [], bookedSeconds = 0, trialLeftAtStart = 0, tickPending = null;
let speaking = false, lastVoiceAt = 0, heardSinceShe = false, linkState = "idle";
let phase = "idle";               // idle | miccheck | preparing | call
let gate = new VoiceGate(), micHelpTimer = null, micStats = { chunks: 0, voiced: 0, maxRms: 0 };
let sheStoppedAt = 0, quietMax = 0, micWarned = false;
let youClearTimer = null;
let offerShown = false;
let booted = false;
const bubbles = new Map();
const logLines = [];
const DEMO_SECONDS = 7 * 60;   // the licence server's DEMO.SECONDS; its answer caps the call too
let demo = null;               // the free demo in progress: { demo, token, seconds } from /mock/demo/start
const wheel = new Wheel($("wheel"));
const waitWheel = new Wheel($("wheel-wait"));

// ------------------------------------------------------------------ helpers

function show(id) {
  if (id !== "s-pass" && id !== "s-invite") lastScreen = id;
  for (const s of document.querySelectorAll(".screen")) s.classList.toggle("on", s.id === id);
  window.scrollTo({ top: 0 });
}
function notice(id, text, cls = "") { const el = $(id); el.textContent = text || ""; el.className = "notice " + cls; }
function log(name, data) {
  if (!diagnosticsEnabled) return;
  const t = startedAt ? (nowS() - startedAt).toFixed(1) : "0.0";
  const line = `${t.padStart(6)}  ${name}${data && Object.keys(data).length ? " " + JSON.stringify(data) : ""}`;
  logLines.push(line);
  const el = $("log"); el.textContent += line + "\n"; el.scrollTop = el.scrollHeight;
}
function fmt(seconds) {
  const s = Math.max(0, Math.round(seconds));
  return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
}
function fmtLong(seconds) {
  const m = Math.round(seconds / 60);
  if (m < 90) return `${m} min`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h} h ${m % 60} min`;
  return `${Math.floor(h / 24)} d ${h % 24} h`;
}
function renderEntitlement() {
  const e = S.ent, el = $("entitle");
  // Nothing known yet: a dash while the server is being asked, and the honest
  // default for a first-time visitor once it is clear nobody is signed in.
  if (!e) { el.textContent = booted ? (store.get("ps_from") === "applysarthi" ? "30 min free" : "20 min free") : "\u2026"; el.className = "chip"; return; }
  if (e.kind === "demo") { el.textContent = "Free demo · 7 min"; el.className = "chip ok"; return; }
  if (e.kind === "pass") { el.textContent = `Pass · ${fmtLong(e.secondsLeft)} left`; el.className = "chip ok"; }
  else if (e.kind === "trial") { el.textContent = `Free · ${fmtLong(e.secondsLeft)} left`; el.className = "chip"; }
  // Signed in, but no Gemini key in this browser yet: no free-minute count to show.
  else if (e.hasTrial === false) { el.textContent = "Get a pass"; el.className = "chip"; }
  else { el.textContent = passCtx.passesOn ? "Get a pass" : "Free minutes used"; el.className = "chip warn"; }
}

/* What the pass screen and the invite card need from this page. */
const passCtx = {
  state: S, passesOn: false, show, track, log,
  setEntitlement(ent) {
    S.ent = ent; renderEntitlement();
    // The server says this once, on the call that created the trial: tell the person where the minutes came from.
    if (ent && ent.welcome) showApplyWelcome(`ApplySarthi bonus added: ${ent.welcome.minutes} extra free minutes, so you have ${Math.round(ent.secondsLeft / 60)} in total.`);
  },
  refresh: () => entitlement(S.hash),
  // An interview keeps running while someone looks at passes; coming back must
  // return to it, never reset it.
  running: () => ["call", "miccheck", "preparing"].includes(phase),
  resume() {
    $("pass-back").textContent = "Back";
    if (["call", "miccheck", "preparing"].includes(phase)) { show("s-live"); return; }
    if (S.key && S.ent && lastScreen === "s-live") preLive();
    else show(lastScreen === "s-live" || lastScreen === "s-report" ? (S.key ? lastScreen : "s-cv") : lastScreen);
  },
  practise() {
    $("pass-back").textContent = "Back";
    if (["call", "miccheck", "preparing"].includes(phase)) { show("s-live"); return; }
    if (S.key && S.ent) preLive(); else if (S.cv || $("cv").value) showKeyStep(); else show("s-cv");
  },
};
function currentLanguage() {
  const v = $("language").value;
  return v === "other" ? ($("language-other").value.trim() || "auto") : v;
}
/* Who the interviewer is right now: the voice the candidate picked decides the
 * name in the brief and the pronouns on the screen. */
function who() { return interviewerPersona(S.voice); }
function escapeHtml(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

// ---------------------------------------------------------------- 1. CV

async function restore() {
  $("cv").value = store.get("ps_cv"); $("jd").value = store.get("ps_jd"); $("name").value = store.get("ps_name");
  $("practice-focus").value = store.get("ps_practice_focus", "role");
  $("target-role").value = store.get("ps_target_role");
  $("target-level").value = store.get("ps_target_level");
  updateNoJdOptions();
  const lang = store.get("ps_language", "English");
  if ([...$("language").options].some((o) => o.value === lang)) $("language").value = lang;
  else { $("language").value = "other"; $("language-other").value = lang; $("language-other").style.display = "block"; }
  const voice = store.get("ps_voice");
  if (voice && [...$("voice").options].some((o) => o.value === voice)) $("voice").value = voice;
  $("key").value = store.get("ps_gemini_key");
  // A returning visitor can reach the interview screen without passing through
  // Continue (the Practise button after buying), so S has to match the form now.
  readForm();
  renderEntitlement();
  // A returning visitor must see what they actually own, not the free-minutes
  // placeholder: ask the server before they touch anything.
  const saved = store.get("ps_gemini_key");
  if (saved) {
    S.key = saved;
    S.hash = await keyHash(saved);
    S.ent = await entitlement(S.hash);
    log("entitlement", { kind: S.ent.kind, secondsLeft: S.ent.secondsLeft, source: S.ent.source, at: "load" });
  } else {
    const byAccount = await entitlementBySession();
    if (byAccount) { S.ent = byAccount; log("entitlement", { kind: byAccount.kind, source: "session", at: "load" }); }
  }
  booted = true;
  renderEntitlement();
}

$("language").onchange = () => { $("language-other").style.display = $("language").value === "other" ? "block" : "none"; };
/* The CV and the JD each take a PDF or a text file from the small button on
 * their label row, or from a file dragged onto the box itself. The file is read
 * here in the browser and its text put into the box, so what the interview
 * reads is always what is on the screen, and still editable. */
function wirePicker({ pick, input, area, noticeId, label, minChars, onText }) {
  const load = async (file) => {
    if (!file) return;
    notice(noticeId, "Reading " + file.name + "…");
    try {
      const text = await readDocFile(file, label);
      if (text.length < minChars) { notice(noticeId, `That file has almost no readable text (a scanned PDF?). Paste the ${label} text instead.`, "bad"); return; }
      $(area).value = text;
      $(pick).classList.add("ok"); $(pick).textContent = "Replace";
      notice(noticeId, `Read ${text.split(/\s+/).length} words from ${file.name}.`, "ok");
      if (onText) onText(text);
    } catch (err) {
      notice(noticeId, err.message, "bad");
    }
  };
  $(pick).onclick = () => $(input).click();
  $(input).onchange = () => { load($(input).files[0]); $(input).value = ""; };   // same file twice still fires
  $(area).ondragover = (e) => { e.preventDefault(); $(area).classList.add("over"); };
  $(area).ondragleave = () => $(area).classList.remove("over");
  $(area).ondrop = (e) => { e.preventDefault(); $(area).classList.remove("over"); load(e.dataTransfer && e.dataTransfer.files[0]); };
}
wirePicker({
  pick: "cvpick", input: "cvfile", area: "cv", noticeId: "cv-notice", label: "CV", minChars: 80,
  onText: (text) => { if (!$("name").value) $("name").value = guessName(text); },
});
wirePicker({ pick: "jdpick", input: "jdfile", area: "jd", noticeId: "jd-notice", label: "JD", minChars: 40, onText: updateNoJdOptions });

function updateNoJdOptions() {
  const noJd = !$("jd").value.trim();
  const general = $("practice-focus").value === "general_cv";
  $("no-jd-options").hidden = !noJd;
  $("target-details").style.display = general ? "none" : "";
  $("no-jd-help").textContent = general
    ? "Practise discussing your experience and skills. This mode does not assess suitability for a specific job."
    : "We’ll practise common skills for this role and level. The report won’t claim a match to a specific employer.";
}
$("jd").oninput = updateNoJdOptions;
$("practice-focus").onchange = updateNoJdOptions;

function readForm() {
  S.cv = tidy($("cv").value); S.jd = tidy($("jd").value); S.name = $("name").value.trim();
  S.practiceFocus = $("practice-focus").value; S.targetRole = $("target-role").value.trim(); S.targetLevel = $("target-level").value;
  S.language = currentLanguage(); S.minutes = Number($("minutes").value) || 12; S.voice = $("voice").value;
}
$("to-key").onclick = async () => {
  readForm();
  if (S.cv.length < 80) { notice("cv-notice", "Add your CV first: a file or pasted text.", "bad"); return; }
  try { interviewContext(S); }
  catch (err) { notice("jd-notice", err.message, "bad"); return; }
  notice("jd-notice", "");
  store.set("ps_practice_focus", S.practiceFocus); store.set("ps_target_role", S.targetRole); store.set("ps_target_level", S.targetLevel);
  store.set("ps_cv", S.cv); store.set("ps_jd", S.jd); store.set("ps_name", S.name); store.set("ps_language", S.language); store.set("ps_voice", S.voice);
  track("mock_cv_ready", { words: S.cv.split(/\s+/).length, jd: !!S.jd, language: S.language });
  await booting;                           // the server's config says whether the free demo is on
  // A first-time visitor gets the free demo on our key: no key, no sign-in, straight to the interview.
  // A key comes up only after a pass is bought (the owner's call, 25 Sep 2026). Someone who already
  // has a key keeps the old path untouched.
  if (!S.key && passCtx.demoOn && !(S.ent && S.ent.kind === "pass")) {
    if (!demoUsed.get()) { S.ent = { kind: "demo", secondsLeft: DEMO_SECONDS, hasTrial: false }; renderEntitlement(); preLive(); return; }
    if (passCtx.passesOn) { openPasses("You've had your free demo. A pass gives you unlimited mock interviews."); return; }
  }
  showKeyStep();
};

/* The key screen. After a purchase it is the one-minute setup that makes the pass usable. */
function showKeyStep() {
  const paid = S.ent && S.ent.kind === "pass";
  $("key-lede").textContent = paid
    ? "Your pass is active. One last step, about a minute: the interviewer runs on Google's Gemini, on your own free key. It stays in this browser and is sent only to Google."
    : "The interviewer runs on Google's Gemini, on your own free key. It stays in this browser and is sent only to Google. If you use Interview Sarthi or ApplySarthi, it is the same key.";
  show("s-key");
  if (!$("key").value) $("key").focus();
}

// --------------------------------------------------------------- 2. Key

$("back-cv").onclick = () => show("s-cv");
$("check-key").onclick = async () => {
  const key = $("key").value.trim();
  if (!key) { notice("key-notice", "Paste the key first.", "bad"); return; }
  $("check-key").disabled = true;
  notice("key-notice", "Checking with Google…");
  try {
    const res = await fetch("https://generativelanguage.googleapis.com/v1beta/models?pageSize=1&key=" + encodeURIComponent(key), { cache: "no-store" });
    if (res.status === 400 || res.status === 401) throw new Error("Google says this key is not valid. Copy it again from AI Studio.");
    if (res.status === 403) throw new Error("This key exists but is not allowed to use Gemini. Check its restrictions in AI Studio.");
    if (!res.ok && res.status !== 429) throw new Error(`Google answered ${res.status}. Try again in a minute.`);
  } catch (err) {
    notice("key-notice", err.message, "bad"); $("check-key").disabled = false; return;
  }
  S.key = key;
  if ($("remember").checked) store.set("ps_gemini_key", key); else store.del("ps_gemini_key");
  S.hash = await keyHash(key);
  S.ent = await entitlement(S.hash);
  renderEntitlement();
  log("entitlement", { kind: S.ent.kind, secondsLeft: S.ent.secondsLeft, source: S.ent.source });
  track("mock_key_ok", { entitlement: S.ent.kind });
  notice("key-notice", "Key works.", "ok");
  $("check-key").disabled = false;
  preLive();
};

// ---------------------------------------------------------- 3. Interview

function setCaption(hint, line, dim = false) {
  $("hint").textContent = hint;
  if (line !== null) $("line").textContent = line;
  $("caption").classList.toggle("dim", dim);
}

/* Only the current thought fits on a call screen: the last sentence or two. */
function lastLines(text, max = 190) {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= max) return clean;
  const parts = clean.split(/(?<=[.?!।])\s+/);
  let out = "";
  for (let i = parts.length - 1; i >= 0; i--) {
    if ((parts[i] + " " + out).length > max && out) break;
    out = (parts[i] + " " + out).trim();
  }
  return out.length > max ? "…" + out.slice(-max) : out;
}

function setLink(state, label) {
  linkState = state;
  const tag = $("livetag");
  tag.textContent = label;
  tag.className = "live" + (state === "live" ? " on" : state === "busy" ? " busy" : "");
}

// ---- microphone help: shown when the mic check fails, or the mic dies mid-call

async function showMicFix(text, { allowAnyway }) {
  $("micfix-text").textContent = text;
  $("micfix-anyway").style.display = allowAnyway ? "flex" : "none";
  const mics = await AudioIO.listMics();
  $("micselect").innerHTML = mics.map((m) => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.label)}</option>`).join("");
  if (audio && audio.micId) $("micselect").value = audio.micId;
  $("micfix").style.display = "block";
}
function hideMicFix() { $("micfix").style.display = "none"; }

$("micselect").onchange = async () => {
  if (!audio) return;
  try {
    const info = await audio.useMic($("micselect").value);
    gate = new VoiceGate();
    log("mic_switched", { label: info.label });
    $("micfix-text").textContent = `Switched to ${info.label || "the other microphone"}. Say hello.`;
  } catch (err) {
    $("micfix-text").textContent = "That microphone could not be opened: " + err.message;
  }
};
$("anyway").onclick = () => {
  if (phase !== "miccheck") return;
  log("mic_check_skipped", { verdict: gate.verdict, maxRms: +gate.maxRms.toFixed(5) });
  track("mock_mic_check", { result: "skipped", verdict: gate.verdict });
  clearTimeout(micHelpTimer); hideMicFix();
  startCall();
};

function showOffer(id, text) { $(id + "-text").textContent = text; $(id).style.display = "flex"; }
function hideOffer(id) { $(id).style.display = "none"; }

function preLive() {
  hidePreparation();
  hideDemoFull();
  phase = "idle";
  hideOffer("live-offer"); offerShown = false;
  show("s-live");
  wheel.start(); wheel.setState("idle"); wheel.setLevel(0); wheel.setMic(0);
  $("pre-live").style.display = "grid"; $("youbar").style.display = "none";
  hideMicFix(); $("youline").textContent = "";
  $("transcript").innerHTML = ""; bubbles.clear();
  $("clock").textContent = fmt(S.minutes * 60); $("clock").classList.remove("low");
  setLink("idle", "Ready");
  const p = who();
  setCaption("Your interviewer", `${p.They} speaks first. Answer out loud, like a real call.`);
  $("tip-speaker").textContent = `Use earphones if you can. From a loud speaker ${p.they} can hear ${p.themself}.`;
  $("tip-interrupt").textContent = `You can interrupt, and so can ${p.they}.`;
  if (S.ent.kind === "demo") {
    $("start").disabled = false;
    const cap = Math.min(S.minutes * 60, DEMO_SECONDS);
    $("clock").textContent = fmt(cap);
    // Free-tier Gemini may use what it hears to improve Google's services; say so before the call, once.
    notice("live-notice", `Your free demo: a ${Math.round(cap / 60)}-minute interview, then your report. It runs on Google Gemini, which may use it to improve its services.`);
  } else if (S.ent.kind === "none") {
    $("start").disabled = true;
    if (passCtx.passesOn) { openPasses("Your free minutes are used up. A pass gives you unlimited mocks, or invite a friend for 20 more free minutes."); return; }
    notice("live-notice", "Your free minutes are used up. Passes open in a few days. Until then, tap Invite at the top: you and a friend both get 20 free minutes.", "bad");
  } else {
    $("start").disabled = false;
    const cap = Math.min(S.minutes * 60, S.ent.secondsLeft);
    $("clock").textContent = fmt(cap);
    const why = S.ent.kind === "pass" ? `Your pass ends in ${fmtLong(S.ent.secondsLeft)}` : `You have ${fmtLong(S.ent.secondsLeft)} free left`;
    notice("live-notice", cap < S.minutes * 60 ? `${why}, so this interview will be ${fmtLong(cap)}.` : "");
  }
}


/* Both of our keys are running all the interviews they can (6 each, measured). The owner's call: offer the
   visitor their own key right now, or a minute's wait. Either way the demo is not used up. */
let demoWaitTimer = null;
function showDemoFull() {
  hideDemoFull();
  $("demo-full").style.display = "block";
  $("start").disabled = true;
  track("mock_demo_full", {});
}
function hideDemoFull() {
  clearInterval(demoWaitTimer); demoWaitTimer = null;
  $("demo-full").style.display = "none"; $("demo-full-note").textContent = "";
  $("demo-full-key").disabled = false; $("demo-full-wait").disabled = false;
}
$("demo-full-key").onclick = () => { track("mock_demo_full_choice", { choice: "key" }); hideDemoFull(); showKeyStep(); };
$("demo-full-wait").onclick = () => {
  track("mock_demo_full_choice", { choice: "wait" });
  $("demo-full-key").disabled = true; $("demo-full-wait").disabled = true;
  let left = 60;
  const say = () => { $("demo-full-note").textContent = `Trying again in ${left} seconds…`; };
  say();
  demoWaitTimer = setInterval(() => {
    left -= 1;
    if (left > 0) { say(); return; }
    hideDemoFull(); $("start").disabled = false;
    notice("live-notice", "Ready. Press Start the interview.", "ok");
  }, 1000);
};

/* The live engine retains the full transcript for the report. The call shows
 * current captions only; support can explicitly enable the diagnostic view. */
function onTranscript(u, done) {
  if (diagnosticsEnabled) {
    let el = bubbles.get(u);
    if (!el) {
      el = document.createElement("div");
      el.className = "bubble " + u.who;
      el.innerHTML = `<small>${u.who === "interviewer" ? "Interviewer" : (escapeHtml(S.name) || "You")}</small><span></span>`;
      $("transcript").appendChild(el); bubbles.set(u, el);
    }
    el.querySelector("span").textContent = u.text + (u.interrupted ? " …" : "");
  }
  if (u.who === "interviewer") {
    // Google sends your words in one batch when your turn ends, so they land
    // just as the interviewer starts to reply. Leave them up for a few seconds:
    // it reads as "this is what they heard", then it fades.
    if (!youClearTimer && $("youline").textContent) youClearTimer = setTimeout(() => { $("youline").textContent = ""; youClearTimer = null; }, 6000);
    setCaption("Interviewer", lastLines(u.text) + (u.interrupted ? " …" : ""), false);
  } else {
    clearTimeout(youClearTimer); youClearTimer = null;
    $("youline").innerHTML = `<b>${who().They} heard</b>` + escapeHtml(lastLines(u.text, 120));
  }
}

function refreshWheel() {
  if (phase !== "call" || !live) return;
  if (linkState === "busy" && !speaking) { wheel.setState("reconnecting"); return; }
  if (speaking) { wheel.setState("speaking"); return; }
  if (micWarned) { wheel.setState("listening"); return; }
  const quietFor = nowS() - lastVoiceAt;
  if (heardSinceShe && quietFor > 0.9) { wheel.setState("thinking"); setCaption("Thinking", null, true); }
  else { wheel.setState("listening"); setCaption(heardSinceShe ? "Listening" : "Your turn", null, heardSinceShe); }
}

function wireAudio() {
  const bars = [...$("bars").children];
  audio.onPlaying = (playing) => {
    speaking = playing;
    if (live) live.setPlaying(playing);
    if (playing) heardSinceShe = false;
    else { sheStoppedAt = nowS(); quietMax = 0; }
    refreshWheel();
  };
  audio.onLevel = (level) => wheel.setLevel(level * 5);
  audio.onChunk = (pcm, rms) => {
    const t = nowS();
    const voiced = rms >= VOICE_RMS;
    micStats.chunks++; if (voiced) micStats.voiced++; if (rms > micStats.maxRms) micStats.maxRms = rms;
    const lvl = Math.min(1, rms * 9);
    wheel.setMic(lvl);
    bars.forEach((b, i) => { b.style.transform = `scaleY(${Math.max(0.12, Math.min(1, lvl * BAR_SHAPE[i] * 1.6)).toFixed(2)})`; });
    if (phase === "miccheck") { if (gate.feed(rms, t)) micCheckPassed(); return; }
    if (phase !== "call") return;
    voiceLog.push([t, voiced]);
    if (rms > quietMax) quietMax = rms;
    if (voiced && !speaking) {
      lastVoiceAt = t; heardSinceShe = true;
      if (micWarned) { micWarned = false; hideMicFix(); log("mic_back", {}); }
    }
    if (live) live.sendAudio(pcm, rms);
    refreshWheel();
  };
}

$("start").onclick = async () => {
  try { interviewContext(S); }
  catch (err) { show("s-cv"); notice("jd-notice", err.message, "bad"); return; }
  $("start").disabled = true;
  notice("live-notice", "");
  audio = new AudioIO();
  audio.onMicMuted = (muted) => {
    log("mic_track_muted", { muted });
    if (muted && phase !== "idle") showMicFix("Your system reports the microphone as muted. Unmute it, then say hello.", { allowAnyway: phase === "miccheck" });
  };
  try { await audio.start(); }
  catch (err) {
    notice("live-notice", "Microphone not available: " + err.message + ". Allow the mic for this site and try again.", "bad");
    log("mic_error", { error: String(err) });
    await audio.stop(); $("start").disabled = false; audio = null; return;
  }
  log("mic", { label: audio.micLabel, deviceRate: audio.sampleRate });
  $("pre-live").style.display = "none"; $("youbar").style.display = "flex"; $("end").disabled = false;
  micStats = { chunks: 0, voiced: 0, maxRms: 0 };
  wireAudio();

  // The interview, and the free minutes, only start once a voice really arrives.
  phase = "miccheck";
  gate = new VoiceGate();
  setLink("idle", "Mic check");
  setCaption("Mic check", "Say hello, so I know I can hear you.", false);
  $("left").textContent = "Your time has not started";
  showPreparation();
  wheel.setState("listening");
  clearTimeout(micHelpTimer);
  micHelpTimer = setTimeout(() => {
    if (phase !== "miccheck") return;
    const verdict = gate.verdict;
    log("mic_check_help", { verdict, maxRms: +gate.maxRms.toFixed(5), chunks: gate.chunks });
    track("mock_mic_check", { result: "help", verdict });
    setCaption("Mic check", "I can't hear you yet.", false);
    showMicFix(MIC_HELP[verdict] || MIC_HELP.silent, { allowAnyway: true });
  }, 6000);
};

function micCheckPassed() {
  clearTimeout(micHelpTimer); hideMicFix();
  log("mic_check_ok", { maxRms: +gate.maxRms.toFixed(4), chunks: gate.chunks });
  track("mock_mic_check", { result: "ok" });
  startCall();
}

let preparationTimer = null;
function hidePreparation() {
  clearInterval(preparationTimer); preparationTimer = null;
  $("preparation").hidden = true;
  $("preparation").closest(".call").classList.remove("preparing");
  $("caption").hidden = false;
}
function showPreparation() {
  hidePreparation();
  const waitingSince = Date.now();
  $("preparation").hidden = false;
  $("preparation").closest(".call").classList.add("preparing");
  $("caption").hidden = true;
  $("youbar").style.display = "none";
  $("prep-status").textContent = S.jd.trim()
    ? "Reviewing your CV and job description to prepare relevant assessment areas."
    : S.practiceFocus === "general_cv"
      ? "Reviewing your CV to prepare questions about your experience and skills."
      : "Reviewing your CV and chosen role to prepare relevant assessment areas.";
  $("prep-elapsed").textContent = "Waiting: 0 seconds";
  $("prep-slow").hidden = true;
  preparationTimer = setInterval(() => {
    const seconds = Math.floor((Date.now() - waitingSince) / 1000);
    $("prep-elapsed").textContent = `Waiting: ${seconds} seconds`;
    if (seconds >= 20) $("prep-slow").hidden = false;
  }, 1000);
}
$("cancel-preparation").onclick = () => cancelMicCheck();

async function cancelMicCheck() {
  planController?.abort(); planController = null;
  hidePreparation();
  clearTimeout(micHelpTimer);
  phase = "idle";
  if (audio) { await audio.stop(); audio = null; }
  preLive();
}

/* No demo for this visitor right now. Nothing here mentions keys: that step comes after a purchase. */
async function demoRefused(reason) {
  await cancelMicCheck();
  track("mock_demo_refused", { reason });
  if (reason === "full") { showDemoFull(); return; }
  if (reason === "busy") { notice("live-notice", "Lots of people are practising right now. Press Start again in about 20 seconds.", "bad"); return; }
  if (reason === "used") demoUsed.set();
  const text = reason === "used" ? "You've had your free demo. A pass gives you unlimited mock interviews."
    : reason === "unavailable" ? "The free demo isn't available just now. Try again in a few minutes, or start with a pass."
    : "Today's free demos are all used up. Come back tomorrow, or start with a pass.";
  if (passCtx.passesOn) openPasses(text); else notice("live-notice", text, "bad");
}

async function startCall() {
  if (phase === "preparing" || phase === "call") return;
  phase = "preparing";
  const controller = new AbortController();
  planController = controller;
  assessmentPlan = null; planCoverage = null;
  setLink("busy", "Preparing");
  setCaption("Preparing your interview", "Reviewing your CV and the role. Your interview timer has not started.", true);
  $("left").textContent = "Your time has not started";
  showPreparation();
  try {
    if (S.ent.kind === "demo") {
      // Asked for only now, at Start: a visitor who never presses it never uses one up.
      demo = await requestDemo();
      if (controller.signal.aborted || planController !== controller) return;
      if (!demo.ok) { const why = demo.reason; demo = null; planController = null; await demoRefused(why); return; }
      // Not marked used here: if Google is too busy to prepare it, pressing Start again resumes the same demo.
      track("mock_demo_start", {});
    }
    const plan = await generateInterviewPlan({ apiKey: S.key, cv: S.cv, jd: S.jd,
      minutes: S.minutes, language: S.language, practiceFocus: S.practiceFocus, targetRole: S.targetRole, targetLevel: S.targetLevel, signal: controller.signal,
      transport: demo ? demoTransport(demo.demo) : undefined });
    if (controller.signal.aborted || planController !== controller) return;
    $("prep-status").textContent = "Your interview plan is ready. Checking your available practice time…";
    // Refresh after preparation: a pass can expire while the plan is being made. A demo has no key to look up.
    const fresh = demo ? S.ent : await entitlement(S.hash);
    if (controller.signal.aborted || planController !== controller) return;
    S.ent = fresh;
    if (S.ent.secondsLeft <= 0) throw new Error("Your practice time has expired. Get a pass or more free minutes before starting.");
    assessmentPlan = plan; planCoverage = new PlanCoverage(plan);
  } catch (err) {
    if (controller.signal.aborted || planController !== controller) return;
    await cancelMicCheck();
    notice("live-notice", `Interview preparation failed: ${err.message} Your interview timer did not start. Please retry.`, "bad");
    return;
  }
  planController = null;
  hidePreparation();
  $("youbar").style.display = "flex";
  phase = "call";
  startedAt = nowS(); voiceLog = []; ending = false; bookedSeconds = 0; tickPending = null;
  speaking = false; heardSinceShe = false; lastVoiceAt = 0; sheStoppedAt = 0; quietMax = 0; micWarned = false;
  trialLeftAtStart = S.ent.secondsLeft;
  plannedSeconds = Math.min(S.minutes * 60, S.ent.secondsLeft, demo ? demo.seconds : Infinity);   // free minutes, passes and the demo all stop on the second
  log("call_start", { planned: plannedSeconds });
  setLink("busy", "Connecting");
  setCaption("I can hear you", "Calling your interviewer…", true);
  $("left").textContent = "You're on";
  wheel.setState("reconnecting");

  const brief = { candidateName: S.name, cv: S.cv, jd: S.jd, language: S.language, voice: S.voice, minutes: plannedSeconds / 60, assessmentPlan };
  live = new GeminiLive({
    apiKey: S.key,
    authToken: demo ? demo.token : "",
    voice: S.voice,
    instructions: () => buildInterviewerInstructions(brief),
    getInterviewProgress: currentProgress,
    onAudio: (pcm) => audio && audio.play(pcm),
    onInterrupted: () => audio && audio.clear(),
    onTranscript,
    onStatus: (s) => {
      if (s === "live") {
        setLink("live", "Live");
        notice("live-notice", "");
        setCaption("Connected", "Your interviewer is here. You can continue.");
      }
      else if (s === "connecting" || s === "reconnecting") {
        setLink("busy", s === "connecting" ? "Connecting" : "Reconnecting");
        if (s === "reconnecting") setCaption("One moment", "Reconnecting. Your practice timer is paused and your answers are kept.", true);
      } else if (s === "failed") endInterview("failed");
      refreshWheel();
    },
    onNotice: (m) => { notice("live-notice", m); log("notice", { m }); },
    onEvent: log,
  });
  live.start();
  track("mock_start", { minutes: Math.round(plannedSeconds / 60), language: S.language, entitlement: S.ent.kind });
  timer = setInterval(onSecond, 1000);
}

function currentProgress(args = {}) {
  const progress = interviewProgress({ plannedSeconds, elapsedSeconds: live ? live.activeSeconds : 0,
    entitlementSeconds: S.ent.kind === "pass" ? trialLeftAtStart - (nowS() - startedAt) : Infinity });
  if (!planCoverage) return progress;
  const turns = live ? live.transcript.turns : [];
  planCoverage.update(args.updates, turns);
  return { ...progress, coverage: planCoverage.snapshot(progress),
    recent_answers: turns.map((u, i) => ({ turn: i + 1, who: u.who, text: u.text.slice(0, 2000) })).filter(u => u.who === "candidate").slice(-3) };
}

async function onSecond() {
  if (!live || ending) return;
  const elapsed = live.activeSeconds;
  // Pass expiry remains real clock time; only practice minutes pause.
  const passLeft = trialLeftAtStart - (nowS() - startedAt);
  const remaining = currentProgress().remainingSeconds;
  $("clock").textContent = fmt(remaining);
  $("clock").classList.toggle("low", remaining <= 60);
  if (S.ent.kind === "demo") $("left").textContent = `Free demo · ${fmt(remaining)} left`;
  else if (S.ent.kind === "trial") $("left").textContent = `Free · ${fmtLong(Math.max(0, trialLeftAtStart - elapsed))} left`;
  else if (S.ent.kind === "pass") $("left").textContent = `Pass · ${fmtLong(Math.max(0, passLeft))} left`;
  // Free time is nearly gone: this is the moment someone decides to buy.
  if (S.ent.kind === "trial" && passCtx.passesOn && !offerShown && trialLeftAtStart - elapsed <= LOW_FREE_SECONDS) {
    offerShown = true;
    showOffer("live-offer", `About ${Math.max(1, Math.round((trialLeftAtStart - elapsed) / 60))} free minutes left. A pass gives you unlimited mocks, from Rs 99 for a week.`);
    track("mock_offer_shown", { where: "interview" });
  }
  if (remaining <= 0) { endInterview("time"); return; }

  // The interviewer asked, and the microphone has delivered exact digital silence
  // ever since: that is a mute key or a dead input, not someone thinking.
  if (!micWarned && linkState === "live" && !speaking && sheStoppedAt && !heardSinceShe
      && nowS() - sheStoppedAt > 10 && quietMax < MIC_MUTED_RMS) {
    micWarned = true;
    log("mic_silent_in_call", { quietMax: +quietMax.toFixed(6) });
    track("mock_mic_silent", {});
    setCaption("Can't hear you", null, true);
    showMicFix(`Your microphone has gone completely silent. Is it muted? ${who().They} is waiting for your answer.`, { allowAnyway: false });
  }

  // Book used time against the trial, like the desktop app's 30-second slices.
  if (S.ent.kind === "trial" && !tickPending && Math.floor(elapsed) - bookedSeconds >= TICK_SECONDS) {
    const slice = Math.floor(elapsed) - bookedSeconds; bookedSeconds += slice;
    tickPending = tick(S.hash, slice);
    const r = await tickPending;
    tickPending = null;
    S.ent.secondsLeft = r.secondsLeft;
    log("trial_tick", { slice, left: r.secondsLeft, source: r.source });
    if (r.reward) {
      trialLeftAtStart += r.reward.seconds;
      notice("live-notice", `You and the friend who invited you both just earned ${Math.round(r.reward.seconds / 60)} free minutes.`, "ok");
      track("mock_invite_reward", { seconds: r.reward.seconds });
    }
    if (!ending && r.secondsLeft <= 0) endInterview("trial");
  }
}

$("end").onclick = () => {
  if (phase === "miccheck" || phase === "preparing") { cancelMicCheck(); return; }
  if (confirm("End the interview now and get your report?")) endInterview("user");
};

async function endInterview(reason) {
  if (ending) return;
  ending = true;
  clearInterval(timer);
  $("end").disabled = true;
  const elapsed = Math.round(live ? live.activeSeconds : 0);
  log("interview_end", { reason, elapsed });
  log("mic_stats", { chunks: micStats.chunks, voicedChunks: micStats.voiced, maxRms: +micStats.maxRms.toFixed(5), label: audio ? audio.micLabel : "" });
  track("mock_end", { reason, seconds: elapsed });
  const turns = live ? live.transcript.turns.map((u) => ({ ...u })) : [];
  const usage = live ? { ...live.usage } : {};
  if (live) { live.close(); live = null; }
  if (audio) { await audio.stop(); audio = null; }
  phase = "idle";
  wheel.setState("idle"); wheel.setLevel(0); wheel.setMic(0);
  // Book the tail of the session.
  if (S.ent.kind === "trial") {
    if (tickPending) await tickPending;
    const slice = Math.max(0, elapsed - bookedSeconds);
    if (slice) { const r = await tick(S.hash, slice); S.ent.secondsLeft = r.secondsLeft; }
    if (S.ent.secondsLeft <= 0) S.ent.kind = "none";
    renderEntitlement();
  }
  if (reason === "failed" && turns.length === 0 && demo) {
    // Google refused the connection (a key at its limit): the same choice as a full server, never a key message.
    ending = false; preLive(); notice("live-notice", ""); showDemoFull();
    return;
  }
  if (reason === "failed" && turns.length === 0) {
    const why = $("live-notice").textContent || "Gemini refused the session.";
    ending = false; preLive();
    notice("live-notice", why + " Fix the key or try again.", "bad");
    return;
  }
  if (turns.filter((u) => u.who === "candidate").length === 0) {
    ending = false; preLive();
    const deaf = micStats.maxRms < 0.002;
    notice("live-notice", deaf
      ? "Your microphone sent only silence for the whole call, so there is nothing to score. It was muted, or the browser used the wrong one. Check it and try again."
      : "Google did not pick up any of your answers, so there is nothing to score. Check your microphone and try again. If it happens again, contact support@interviewsarthi.com.", "bad");
    return;
  }
  wheel.stop();
  await writeReport(turns, elapsed, usage);
}

// ------------------------------------------------------------- 4. Report

async function writeReport(turns, elapsed, usage) {
  show("s-report");
  $("report").innerHTML = ""; $("report-wait").style.display = "block";
  waitWheel.start(); waitWheel.setState("thinking");
  const metrics = computeMetrics(turns, voiceLog);
  let result;
  try {
    result = await generateReport({ apiKey: S.key, transport: demo ? demoTransport(demo.demo) : undefined, cv: S.cv, jd: S.jd, language: S.language, transcript: turns, metrics, minutes: Math.round(elapsed / 60), assessmentPlan });
  } catch (err) {
    waitWheel.stop(); $("report-wait").style.display = "none";
    $("report").innerHTML = `<div class="card"><h2 style="font-size:28px">The report could not be written</h2><p class="muted">${escapeHtml(err.message)}</p><p class="muted">Your transcript is safe. Download it below and try again later.</p></div>`;
    window.__lastReport = { turns, metrics, elapsed };
    return;
  }
  waitWheel.stop(); $("report-wait").style.display = "none";
  const record = { at: new Date().toISOString(), elapsed, language: S.language, model: result.model, report: result.report, metrics, transcript: turns, usage };
  window.__lastReport = record;
  saveHistory(record);
  renderReport(record);
  if (S.ent.kind === "demo") {
    // The demo is over: this is the moment to offer the pass. A second demo is not offered.
    track("mock_demo_end", { score: result.report.overall_score });
    demoUsed.set();
    demo = null;
    S.ent = { kind: "none", secondsLeft: 0, hasTrial: false }; renderEntitlement();   // spent: the chip now says "Get a pass"
    if (passCtx.passesOn) {
      showOffer("report-offer", "That was your free demo. A pass gives you unlimited mock interviews, from Rs 99 for a week.");
      track("mock_offer_shown", { where: "demo_report" });
    } else hideOffer("report-offer");
    track("mock_report", { score: result.report.overall_score, questions: (result.report.questions || []).length, model: result.model });
    return;
  }
  if (S.ent.kind !== "pass") { const fresh = await entitlement(S.hash); if (fresh.source === "server") { S.ent = fresh; renderEntitlement(); } }
  renderInvite($("invite-report"), result.report.overall_score);
  if (S.ent.kind !== "pass" && passCtx.passesOn) {
    const left = Math.round((S.ent.secondsLeft || 0) / 60);
    showOffer("report-offer", left > 0
      ? `You have ${left} free minute${left === 1 ? "" : "s"} left. A pass gives you unlimited mocks, from Rs 99 for a week.`
      : "Your free minutes are used up. A pass gives you unlimited mocks, from Rs 99 for a week.");
    track("mock_offer_shown", { where: "report" });
  } else hideOffer("report-offer");
  track("mock_report", { score: result.report.overall_score, questions: (result.report.questions || []).length, model: result.model });
}

function renderReport(r) {
  const rep = r.report, m = r.metrics;
  const li = (arr) => (arr || []).map((x) => `<li>${escapeHtml(x)}</li>`).join("");
  const tiles = [
    m.avgResponseDelay !== null ? [`${m.avgResponseDelay}s`, "Pause before answering"] : null,
    m.avgWpm ? [`${m.avgWpm}`, "Words per minute"] : null,
    [`${m.fillersTotal}`, "Filler words"],
    m.longestPause >= 2 ? [`${m.longestPause}s`, "Longest silence"] : null,
    [fmt(r.elapsed), "Interview length"],
  ].filter(Boolean).map(([b, s]) => `<div class="tile"><b>${b}</b><span>${s}</span></div>`).join("");
  const questions = (rep.questions || []).map((q, i) => {
    const score = Math.max(0, Math.min(10, Number(q.score) || 0));
    const tone = score >= 7 ? "good" : score >= 5 ? "mid" : "";
    return `<div class="q">
      <span class="label">Question ${i + 1} · ${score} / 10</span>
      <h3>${escapeHtml(q.question)}</h3>
      <div class="meter"><i class="${tone}" style="width:${score * 10}%"></i></div>
      <p class="said">You said: ${escapeHtml(q.answer_gist)}</p>
      <p style="margin:0"><b>Missing.</b> ${escapeHtml(q.what_was_missing)}</p>
      <div class="better"><span class="label">Stronger answer</span>${escapeHtml(q.better_answer)}</div>
    </div>`;
  }).join("");
  const d = rep.delivery || {};
  $("report").innerHTML = `
    <div class="card">
      <span class="label">Practice score · assessed areas</span>
      <div class="score"><b>${rep.overall_score === null ? "—" : escapeHtml(rep.overall_score)}</b><span>${rep.overall_score === null ? "Not enough evidence" : "out of 100"}</span></div>
      <p class="verdict">${escapeHtml(rep.verdict)}</p>
      <div class="tiles">${tiles}</div>
    </div>
    ${assessmentHtml(rep, r.transcript)}
    <div class="two">
      <div class="card"><span class="label">What worked</span><ul class="clean">${li(rep.strengths)}</ul></div>
      <div class="card"><span class="label">What hurt</span><ul class="clean bad">${li(rep.weaknesses)}</ul></div>
    </div>
    <div class="card"><span class="label">Question by question</span>${questions || "<p class='muted'>No scored questions.</p>"}</div>
    <div class="card delivery"><span class="label">How you sounded</span>
      <p><b>Pace</b>${escapeHtml(d.pace || "")}</p>
      <p><b>Fillers</b>${escapeHtml(d.fillers || "")}</p>
      <p><b>Confidence</b>${escapeHtml(d.confidence || "")}</p>
      <p><b>Structure</b>${escapeHtml(d.structure || "")}</p>
    </div>
    <div class="card"><span class="label">Practise next</span><ol class="next">${li(rep.practice_next)}</ol>
      <p class="muted" style="font-size:13px;margin:14px 0 0">Report written by ${escapeHtml(r.model)} on your own key.</p></div>`;
}

function saveHistory(record) {
  try {
    const list = JSON.parse(store.get("ps_history", "[]"));
    list.unshift({ at: record.at, score: record.report.overall_score, elapsed: record.elapsed, language: record.language });
    store.set("ps_history", JSON.stringify(list.slice(0, 20)));
    store.set("ps_last_report", JSON.stringify(record));
  } catch (_) { /* storage full or off */ }
}

$("again").onclick = () => { ending = false; preLive(); };
$("download").onclick = () => {
  const r = window.__lastReport;
  if (!r) return;
  const lines = [`Prep Sarthi report, ${new Date(r.at || Date.now()).toLocaleString()}`, ""];
  if (r.report) {
    lines.push(`Practice score: ${r.report.overall_score === null ? "Not enough evidence" : `${r.report.overall_score}/100`}`, r.report.verdict, "", assessmentText(r.report), "", "What worked:", ...(r.report.strengths || []).map((x) => "- " + x), "", "What hurt:", ...(r.report.weaknesses || []).map((x) => "- " + x), "");
    for (const q of r.report.questions || []) lines.push(`Q: ${q.question}`, `  Score ${q.score}/10. You said: ${q.answer_gist}`, `  Missing: ${q.what_was_missing}`, `  Stronger: ${q.better_answer}`, "");
    lines.push("Practise next:", ...(r.report.practice_next || []).map((x, i) => `${i + 1}. ${x}`), "");
  }
  lines.push("Transcript:", ...(r.transcript || r.turns || []).map((u) => `${u.who === "interviewer" ? "Interviewer" : "You"}: ${u.text}`));
  const blob = new Blob([lines.join("\n")], { type: "text/plain" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "prep-sarthi-report.txt"; a.click();
};

$("copydiag").onclick = async () => {
  const text = [`Prep Sarthi diagnostics ${new Date().toISOString()}`, navigator.userAgent, `page ${location.host}${location.pathname}`, "", ...logLines].join("\n");
  try { await navigator.clipboard.writeText(text); $("copydiag-note").textContent = "Copied. Paste it in an email or chat."; }
  catch (_) {
    const area = document.createElement("textarea"); area.value = text; area.style.cssText = "width:100%;height:160px;margin-top:10px";
    $("copydiag").parentElement.appendChild(area); area.select();
    $("copydiag-note").textContent = "Select all and copy.";
  }
};

$("live-offer-go").onclick = () => { track("mock_offer_click", { where: "interview" }); openPasses(); };
$("report-offer-go").onclick = () => { track("mock_offer_click", { where: "report" }); openPasses(); };

/* ApplySarthi's "Practise this interview" arrives as ?from=applysarthi&job=source:id. The job's public listing is
 * read from ApplySarthi and put in the JD box, so the mock interview is for that exact role. Only the public
 * job crosses over, never anything from the person's ApplySarthi account. The address is cleaned afterwards. */
const APPLY_API = "https://apply.interviewsarthi.com";
function showApplyWelcome(text) {
  let el = document.getElementById("apply-welcome");
  if (!el) {
    const lede = document.querySelector("#s-cv .lede"); if (!lede) return;
    el = document.createElement("div"); el.id = "apply-welcome"; el.className = "notice ok";
    el.style.cssText = "margin:12px 0 0;padding:10px 14px;border:1px solid currentColor;border-radius:10px;font-weight:500";
    lede.after(el);
  }
  el.textContent = text;
}
async function loadJobFromApply() {
  const q = new URLSearchParams(location.search);
  const job = q.get("job") || "", fromApply = q.get("from") === "applysarthi";
  if (q.has("job") || q.has("from")) {
    const clean = new URL(location.href); clean.searchParams.delete("job"); clean.searchParams.delete("from");
    history.replaceState(null, "", clean.pathname + clean.search + clean.hash);
  }
  if (fromApply) showApplyWelcome("Welcome from ApplySarthi. New to Prep Sarthi? You get 30 free minutes instead of 20.");
  const i = job.indexOf(":");
  if (i <= 0) return;
  try {
    const res = await fetch(`${APPLY_API}/api/jd?source=${encodeURIComponent(job.slice(0, i))}&source_id=${encodeURIComponent(job.slice(i + 1))}`, { cache: "no-store" });
    if (!res.ok) return;
    const j = await res.json();
    if (!j.text) return;
    const title = String(j.title || "").trim(), company = String(j.company || "").trim();
    const head = [title, company && `at ${company}`, j.location && `(${j.location})`].filter(Boolean).join(" ");
    $("jd").value = `${head}\n\n${j.text}`; store.set("ps_jd", $("jd").value);
    updateNoJdOptions();
    notice("jd-notice", `Loaded from ApplySarthi: ${title || "your job"}${company ? " at " + company : ""}. Your interviewer will ask about this job.`, "ok");
    track("apply_job_loaded", {});
  } catch (_) { /* the box stays as it was; the JD can still be pasted by hand */ }
}

window.addEventListener("pagehide", () => { planController?.abort(); hidePreparation(); if (live) live.close(); });
rememberInvite();
rememberSource();
const booting = restore().then(loadJobFromApply).then(() => initPasses(passCtx)).then(renderEntitlement);
