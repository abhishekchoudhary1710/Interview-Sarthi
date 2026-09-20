/* Prep Sarthi: the pass screen and the invite card.
 *
 * Buying: pick 7 or 30 days, sign in with Google (so the pass follows the
 * person, not the browser), pay through Cashfree, come back, and the page asks
 * the server until the pass is confirmed. Nothing renews by itself.
 *
 * Inviting: every key has a link. The share text never carries the score
 * unless the person ticks it themselves, and the tick is only offered for a
 * score worth showing.
 */

import { LOCAL, config, inviteLink, orderStatus, session, signIn, startFreeDays, startOrder } from "./billing.js";

const $ = (id) => document.getElementById(id);
const PENDING = "ps_pending_order";
const SCORE_WORTH_SHARING = 70;
const PLAN_COPY = { w: { days: "7 days", line: "For the interview this week" }, m: { days: "30 days", line: "For placement season, about Rs 8 a day" } };

let ctx = null;          // { state, setEntitlement, show, track, log, resume }
let cfg = null;
let googleReady = false;

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) return resolve();
    const s = document.createElement("script");
    s.src = src; s.async = true; s.onload = resolve; s.onerror = () => reject(new Error("could not load " + src));
    document.head.appendChild(s);
  });
}
function say(text, cls = "") { const el = $("pass-notice"); el.textContent = text || ""; el.className = "notice " + cls; }
function when(isoTime) { return new Date(isoTime).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }); }
function escapeHtml(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

export async function initPasses(context) {
  ctx = context;
  try { cfg = await config(); } catch (_) { cfg = null; }
  const testLogin = LOCAL && cfg && !cfg.google_client_id;
  ctx.passesOn = !!(cfg && (cfg.google_client_id || testLogin));
  if (cfg && cfg.plans) {
    for (const [id, p] of Object.entries(cfg.plans)) {
      const el = document.querySelector(`.plan[data-plan="${id}"]`);
      if (el) { el.querySelector(".price").textContent = "Rs " + p.amount; el.querySelector("b").textContent = (PLAN_COPY[id] || {}).days || p.label; }
    }
  }
  $("entitle").onclick = () => openPasses();
  $("open-invite").onclick = () => openInvite();
  $("pass-back").onclick = () => ctx.resume();
  $("invite-back").onclick = () => ctx.resume();
  for (const el of document.querySelectorAll(".plan")) el.onclick = () => choosePlan(el.dataset.plan);
  $("pay").onclick = pay;
  $("signout").onclick = () => { session.clear(); ctx.state.ent = { ...ctx.state.ent, account: null }; paint(); };
  $("start-days").onclick = startDays;
  if (testLogin) {
    $("testlogin").style.display = "block";
    $("testlogin-go").onclick = () => onGoogle("test:" + ($("testlogin-email").value.trim() || "tester@example.com"));
  }
  await resumePendingOrder();
}

// ------------------------------------------------------------------ passes

function choosePlan(id) {
  ctx.state.plan = id;
  for (const el of document.querySelectorAll(".plan")) el.classList.toggle("on", el.dataset.plan === id);
  const p = cfg && cfg.plans && cfg.plans[id];
  $("pay").textContent = p ? `Pay Rs ${p.amount} →` : "Pay →";
}

export async function openPasses(message) {
  ctx.show("s-pass");
  say(message || "");
  if (!ctx.passesOn) {
    $("pass-body").style.display = "none";
    say("Passes open in a few days. Until then, invite a friend: you both get 20 free minutes.", "");
    return;
  }
  $("pass-body").style.display = "block";
  choosePlan(ctx.state.plan || "w");
  paint();
  ctx.track("mock_pass_view", { signed_in: !!(ctx.state.ent && ctx.state.ent.account) });
  if (cfg.google_client_id && !googleReady) {
    try {
      await loadScript("https://accounts.google.com/gsi/client");
      window.google.accounts.id.initialize({ client_id: cfg.google_client_id, callback: (r) => onGoogle(r.credential), ux_mode: "popup" });
      window.google.accounts.id.renderButton($("gbutton"), { theme: "filled_black", size: "large", shape: "pill", text: "continue_with", width: 300 });
      googleReady = true;
    } catch (err) { say("Google sign-in could not load. Check your connection and try again.", "bad"); }
  }
}

function paint() {
  const ent = ctx.state.ent || {};
  const account = ent.account;
  $("pass-signin").style.display = account ? "none" : "block";
  $("pass-pay").style.display = account ? "block" : "none";
  if (account) $("pass-who").textContent = `Signed in as ${account.email}`;
  const live = ent.kind === "pass";
  $("pass-live").style.display = live ? "block" : "none";
  if (live) $("pass-live-text").textContent = `Your pass is live until ${when(ent.expiresAt)}. Buying again adds the days on top.`;
  const banked = (ent.invite && ent.invite.banked_days) || 0;
  $("freedays").style.display = banked > 0 ? "block" : "none";
  if (banked > 0) {
    $("freedays-text").textContent = `You have ${banked} free day${banked > 1 ? "s" : ""} from friends who bought a pass.`;
    $("start-days").textContent = account ? `Start my ${banked} free day${banked > 1 ? "s" : ""}` : "Sign in above to start them";
    $("start-days").disabled = !account;
  }
}

async function onGoogle(credential) {
  if (!ctx.state.hash) { say("Add your Gemini key first, then come back to sign in.", "bad"); return; }
  say("Signing you in…");
  try {
    ctx.setEntitlement(await signIn(credential, ctx.state.hash));
    say("");
    ctx.track("mock_sign_in", {});
    paint();
  } catch (err) { say(err.message, "bad"); }
}

async function pay() {
  const phone = $("phone").value.replace(/\D/g, "");
  if (phone.length < 10) { say("Enter your 10-digit mobile number. Cashfree needs it for the receipt.", "bad"); return; }
  $("pay").disabled = true;
  say("Opening secure checkout…");
  try {
    const order = await startOrder(ctx.state.plan || "w", phone);
    try { localStorage.setItem(PENDING, JSON.stringify({ order_id: order.order_id, hash: ctx.state.hash, at: Date.now() })); } catch (_) { /* private mode */ }
    ctx.track("begin_checkout", { product: "prep-sarthi", plan: ctx.state.plan || "w", value: order.amount, currency: "INR" });
    await loadScript("https://sdk.cashfree.com/js/v3/cashfree.js");
    window.Cashfree({ mode: order.mode }).checkout({ paymentSessionId: order.payment_session_id, redirectTarget: "_self" });
  } catch (err) {
    say(err.status === 401 ? "Your sign-in expired. Sign in again." : err.message, "bad");
    if (err.status === 401) { session.clear(); ctx.state.ent = { ...ctx.state.ent, account: null }; paint(); }
    $("pay").disabled = false;
  }
}

/* Back from Cashfree (or the tab was closed mid-payment): ask until it is settled. */
async function resumePendingOrder() {
  let pending = null;
  try { pending = JSON.parse(localStorage.getItem(PENDING) || "null"); } catch (_) { /* corrupt */ }
  const fromUrl = new URLSearchParams(location.search).get("order_id");
  if (fromUrl && (!pending || pending.order_id !== fromUrl)) pending = pending && pending.hash ? { ...pending, order_id: fromUrl } : null;
  if (!pending || !session.get() || Date.now() - (pending.at || 0) > 3600_000) return;
  if (fromUrl) history.replaceState(null, "", location.pathname);
  ctx.state.hash = ctx.state.hash || pending.hash;
  ctx.show("s-pass");
  $("pass-body").style.display = "none";
  say("Confirming your payment… keep this page open.");
  for (let i = 0; i < 40; i++) {
    let r;
    try { r = await orderStatus(pending.order_id, pending.hash); } catch (err) { r = { status: "pending" }; }
    if (r.status === "paid") {
      try { localStorage.removeItem(PENDING); } catch (_) { /* ignore */ }
      ctx.setEntitlement(r.entitlement);
      ctx.track("purchase", { product: "prep-sarthi", plan: r.plan });
      $("pass-body").style.display = "block"; paint();
      say(`Paid. Your ${r.plan} is live until ${when(r.entitlement.expiresAt)}. Unlimited mocks until then.`, "ok");
      $("pass-back").textContent = "Start practising →";
      return;
    }
    if (r.status === "failed") {
      try { localStorage.removeItem(PENDING); } catch (_) { /* ignore */ }
      $("pass-body").style.display = "block"; choosePlan(ctx.state.plan || "w"); paint();
      say("That payment did not go through, and nothing was charged. You can try again.", "bad");
      return;
    }
    await new Promise((ok) => setTimeout(ok, 2500));
  }
  $("pass-body").style.display = "block"; paint();
  say("The payment is still being confirmed. If money left your account, your pass will appear here within a few minutes. Otherwise write to support@interviewsarthi.com.", "");
}

async function startDays() {
  try {
    await startFreeDays();
    ctx.setEntitlement(await ctx.refresh());
    paint();
    say("Your free days have started. Unlimited mocks until they end.", "ok");
    ctx.track("mock_free_days_started", {});
  } catch (err) { say(err.message, "bad"); }
}

// ------------------------------------------------------------------ invites

export function openInvite() {
  if (!ctx.state.ent || !ctx.state.ent.invite || !ctx.state.ent.invite.code) {
    ctx.show("s-key");
    const el = $("key-notice"); el.textContent = "Add your Gemini key first. Your invite link is tied to it."; el.className = "notice";
    return;
  }
  ctx.show("s-invite");
  renderInvite($("invite-full"), null);
  ctx.track("mock_invite_view", { from: "nav" });
}

/** Draw the invite card into `host`. `score` is only ever used if the person ticks the box. */
export function renderInvite(host, score) {
  const inv = ctx.state.ent && ctx.state.ent.invite;
  if (!inv || !inv.code) { host.innerHTML = ""; return; }   // never show a link without a code
  const link = inviteLink(inv.code);
  const rules = inv.rules || { minutes: 20, max_friends: 5, inviter_days: 3, friend_days: 1 };
  const brag = Number(score) >= SCORE_WORTH_SHARING;
  host.innerHTML = `
    <div class="card invite">
      <span class="label">Invite a friend</span>
      <h2>You both get ${rules.minutes} free minutes.</h2>
      <p class="muted">When a friend does their first mock through your link, ${rules.minutes} free minutes land for both of you, for your first ${rules.max_friends} friends. If they buy a pass, you get ${rules.inviter_days} free days and they get ${rules.friend_days} extra day.</p>
      <input type="text" class="invite-link" readonly value="${escapeHtml(link)}">
      ${brag ? `<label class="check"><input type="checkbox" class="with-score"> Include my score (${Number(score)}) in the message</label>` : ""}
      <div class="actions">
        <a class="pill share-wa" target="_blank" rel="noopener">Share on WhatsApp</a>
        <button class="pill ghost share-copy">Copy link</button>
        ${navigator.share ? `<button class="pill ghost share-more">More…</button>` : ""}
      </div>
      <p class="muted invite-stats">${inv.friends_tried} friend${inv.friends_tried === 1 ? "" : "s"} tried it · ${inv.friends_bought} bought a pass · you earned ${inv.minutes_earned} free minutes${inv.banked_days ? ` and ${inv.banked_days} free days` : ""}</p>
    </div>`;
  const text = () => {
    const withScore = brag && host.querySelector(".with-score") && host.querySelector(".with-score").checked;
    return (withScore
      ? `I scored ${Number(score)}/100 in a mock interview with an AI that had read my CV. Try yours, it's free: `
      : `I just did a mock interview with an AI that had actually read my CV. It asks follow-ups like a real interviewer. Try yours, it's free: `) + link;
  };
  const wa = host.querySelector(".share-wa");
  const setWa = () => { wa.href = "https://wa.me/?text=" + encodeURIComponent(text()); };
  setWa();
  wa.onclick = () => ctx.track("mock_invite_share", { via: "whatsapp" });
  const box = host.querySelector(".with-score"); if (box) box.onchange = setWa;
  host.querySelector(".invite-link").onclick = (e) => e.target.select();
  host.querySelector(".share-copy").onclick = async (e) => {
    try { await navigator.clipboard.writeText(text()); e.target.textContent = "Copied"; } catch (_) { host.querySelector(".invite-link").select(); e.target.textContent = "Select and copy"; }
    ctx.track("mock_invite_share", { via: "copy" });
  };
  const more = host.querySelector(".share-more");
  if (more) more.onclick = () => { navigator.share({ text: text() }).catch(() => {}); ctx.track("mock_invite_share", { via: "native" }); };
}
