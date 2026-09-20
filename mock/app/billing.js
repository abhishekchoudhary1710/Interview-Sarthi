/* Prep Sarthi: free minutes, passes and invites, through the licence server.
 *
 * Free minutes are keyed by a one-way hash of the Gemini key (the key itself
 * never leaves the browser). Passes belong to a Google account; after sign-in
 * the server gives this browser a 30-day session. The server is the only
 * clock: the page asks how many seconds are left and counts down from there.
 *
 * When the server cannot be reached, free minutes fall back to a local counter
 * so a mock is never blocked by a hiccup; the server wins whenever it answers.
 */

// Local preview (python -m http.server) talks to the sandbox worker, whose CORS
// allows 127.0.0.1:8765; the live site talks to production.
export const LOCAL = typeof location !== "undefined" && /^(127\.0\.0\.1|localhost)$/.test(location.hostname);
export const LICENSE_API = LOCAL
  ? "https://interview-sarthi-license-test.interview-sarthi-license.workers.dev"
  : "https://license.interviewsarthi.com";
export const TRIAL_SECONDS = 20 * 60;

const mem = {
  get(k) { try { return localStorage.getItem(k) || ""; } catch { return ""; } },
  set(k, v) { try { v ? localStorage.setItem(k, v) : localStorage.removeItem(k); } catch (_) { /* private mode */ } },
};

export async function keyHash(apiKey) {
  const bytes = new TextEncoder().encode("prep-sarthi:" + apiKey.trim());
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

// ---- who invited this visitor: the first code seen wins, and it is only sent
// until the server has met this key.
export function rememberInvite() {
  try {
    const ref = new URLSearchParams(location.search).get("ref");
    if (ref && /^[A-Za-z0-9]{7}$/.test(ref) && !mem.get("ps_ref")) mem.set("ps_ref", ref.toUpperCase());
  } catch (_) { /* no URL */ }
  return mem.get("ps_ref");
}

export const session = {
  get: () => mem.get("ps_session"),
  set: (v) => mem.set("ps_session", v),
  clear: () => mem.set("ps_session", ""),
};

const localTrial = {
  key: (hash) => "ps_trial_" + hash.slice(0, 16),
  used(hash) { return Number(mem.get(this.key(hash)) || 0); },
  add(hash, seconds) { mem.set(this.key(hash), String(this.used(hash) + seconds)); },
  set(hash, seconds) { mem.set(this.key(hash), String(Math.max(0, seconds))); },
};

async function post(path, body) {
  const res = await fetch(LICENSE_API + path, {
    method: "POST", headers: { "content-type": "application/json" }, cache: "no-store", body: JSON.stringify(body),
  });
  let data = {};
  try { data = await res.json(); } catch (_) { /* empty body */ }
  if (!res.ok) { const err = new Error(data.error || `license server ${res.status}`); err.status = res.status; throw err; }
  return data;
}

function shape(r, hash) {
  // `trial` is absent when the person is signed in but this browser holds no
  // Gemini key yet: then only the pass is known.
  const hasTrial = !!(r.trial && typeof r.trial.seconds_left === "number");
  const trialLeft = hasTrial ? Math.max(0, Number(r.trial.seconds_left)) : 0;
  if (hasTrial && hash) localTrial.set(hash, Number(r.trial.total) - trialLeft);   // keep the local mirror honest
  const base = { invite: r.invite || null, account: r.account || null, plans: r.plans || null, trialLeft, hasTrial, source: "server" };
  if (r.pass && r.pass.valid) return { ...base, kind: "pass", secondsLeft: Math.max(0, Number(r.pass.seconds_left)), expiresAt: r.pass.expires_at };
  if (!hasTrial) return { ...base, kind: "none", secondsLeft: 0 };
  return { ...base, kind: trialLeft > 0 ? "trial" : "none", secondsLeft: trialLeft };
}

/**
 * What this key (and this account, if signed in) may do right now.
 * @returns {{kind:"pass"|"trial"|"none", secondsLeft:number, expiresAt?:string, invite, account, plans, source}}
 */
export async function entitlement(hash) {
  try {
    const r = await post("/mock/status", { hash, session: session.get() || undefined, ref: mem.get("ps_ref") || undefined });
    if (session.get() && !r.account) session.clear();            // expired or unknown session
    return shape(r, hash);
  } catch (_) {
    const left = Math.max(0, TRIAL_SECONDS - localTrial.used(hash));
    return { kind: left > 0 ? "trial" : "none", secondsLeft: left, trialLeft: left, invite: null, account: null, plans: null, source: "local" };
  }
}

/* What the signed-in person owns, when this browser has no key to hash yet.
 * Returns null when nobody is signed in. */
export async function entitlementBySession() {
  if (!session.get()) return null;
  try {
    const r = await post("/mock/status", { session: session.get() });
    if (!r.account) { session.clear(); return null; }
    return shape(r, null);
  } catch (_) { return null; }
}

/* Book a slice of the free minutes, like the desktop app's book_free_tick. */
export async function tick(hash, seconds) {
  localTrial.add(hash, seconds);
  try {
    const r = await post("/mock/trial/tick", { hash, seconds, ref: mem.get("ps_ref") || undefined });
    return { secondsLeft: Math.max(0, Number(r.seconds_left)), reward: r.reward || null, source: "server" };
  } catch (_) {
    return { secondsLeft: Math.max(0, TRIAL_SECONDS - localTrial.used(hash)), reward: null, source: "local" };
  }
}

// ---- passes

export const config = () => post("/mock/config", {});

export async function signIn(idToken, hash) {
  const r = await post("/mock/auth/google", { id_token: idToken, hash });
  session.set(r.session);
  return shape(r, hash);
}

export const startOrder = (plan, phone) => post("/mock/buy", { session: session.get(), plan, phone });

export async function orderStatus(orderId, hash) {
  const r = await post("/mock/order", { session: session.get(), order_id: orderId, hash });
  return r.status === "paid" ? { status: "paid", plan: r.plan, entitlement: shape(r, hash) } : { status: r.status };
}

export const startFreeDays = () => post("/mock/days/start", { session: session.get() });

export const inviteLink = (code) => `https://interviewsarthi.com/mock/?ref=${encodeURIComponent(code)}`;
