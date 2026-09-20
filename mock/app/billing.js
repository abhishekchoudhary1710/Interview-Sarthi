/* Prep Sarthi: free minutes and passes, through the licence server.
 *
 * The trial is keyed by a one-way hash of the Gemini key (the key itself
 * never leaves the browser). The server is the only clock for passes. Until
 * the worker endpoints are deployed, or when it is unreachable, the page falls
 * back to a local counter so a mock is never blocked by a server hiccup; the
 * server wins whenever it answers.
 */

// Local preview (python -m http.server) talks to the sandbox worker, whose CORS
// allows 127.0.0.1:8765; the live site talks to production.
const LOCAL = typeof location !== "undefined" && /^(127\.0\.0\.1|localhost)$/.test(location.hostname);
export const LICENSE_API = LOCAL
  ? "https://interview-sarthi-license-test.interview-sarthi-license.workers.dev"
  : "https://license.interviewsarthi.com";
export const TRIAL_SECONDS = 20 * 60;

export async function keyHash(apiKey) {
  const bytes = new TextEncoder().encode("prep-sarthi:" + apiKey.trim());
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

const local = {
  key: (hash) => "ps_trial_" + hash.slice(0, 16),
  used(hash) { try { return Number(localStorage.getItem(this.key(hash)) || 0); } catch { return 0; } },
  add(hash, seconds) { try { localStorage.setItem(this.key(hash), String(this.used(hash) + seconds)); } catch (_) { /* private mode */ } },
};

async function post(path, body) {
  const res = await fetch(LICENSE_API + path, {
    method: "POST", headers: { "content-type": "application/json" }, cache: "no-store", body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`license server ${res.status}`);
  return res.json();
}

/**
 * What this key may do right now.
 * @returns {{kind:"pass"|"trial"|"none", secondsLeft:number, expiresAt?:string, source:"server"|"local"}}
 */
export async function entitlement(hash, account) {
  try {
    const r = await post("/mock/status", { hash, account: account || null });
    if (r.pass && r.pass.valid) return { kind: "pass", secondsLeft: Math.max(0, r.pass.seconds_left), expiresAt: r.pass.expires_at, source: "server" };
    const left = Math.max(0, Number(r.trial.seconds_left));
    local.add(hash, Math.max(0, (TRIAL_SECONDS - left) - local.used(hash)));  // keep the local mirror honest
    return { kind: left > 0 ? "trial" : "none", secondsLeft: left, source: "server" };
  } catch (_) {
    const left = Math.max(0, TRIAL_SECONDS - local.used(hash));
    return { kind: left > 0 ? "trial" : "none", secondsLeft: left, source: "local" };
  }
}

/* Book a slice of the trial, like the desktop app's book_free_tick. */
export async function tick(hash, seconds) {
  local.add(hash, seconds);
  try {
    const r = await post("/mock/trial/tick", { hash, seconds });
    return { secondsLeft: Math.max(0, Number(r.seconds_left)), source: "server" };
  } catch (_) {
    return { secondsLeft: Math.max(0, TRIAL_SECONDS - local.used(hash)), source: "local" };
  }
}
