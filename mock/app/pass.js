/* Prep Sarthi: the pass screen, the account panel and the invite card.
 *
 * Buying, in the order a buyer expects it:
 *   1. see both passes and press Buy
 *   2. say who you are (Google, so the pass follows the person not the browser)
 *      and leave a number for the receipt
 *   3. pay through Cashfree
 *   4. come back to your own account, not to another pay form
 * Nothing renews by itself.
 *
 * Inviting: every key has a link. The share text never carries the score
 * unless the person ticks it themselves, and the tick is only offered for a
 * score worth showing.
 */

import { LOCAL, config, inviteLink, orderStatus, session, signIn, startFreeDays, startOrder } from "./billing.js";

const $ = (id) => document.getElementById(id);
const PENDING = "ps_pending_order";
const SCORE_WORTH_SHARING = 70;

let ctx = null;          // { state, setEntitlement, show, track, log, resume, practise }
let cfg = null;
let googleReady = false;
let step = "choose";     // choose | checkout | signin (a buyer on a new device, not buying)
const PHONE = "ps_phone";
let extendOpen = false;

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
function planOf(id) { return (cfg && cfg.plans && cfg.plans[id]) || null; }
function daysLeft(seconds) {
  const d = Math.floor(seconds / 86400), h = Math.floor((seconds % 86400) / 3600);
  if (d >= 1) return `${d} day${d > 1 ? "s" : ""}${h ? ` ${h} h` : ""} left`;
  if (h >= 1) return `${h} hour${h > 1 ? "s" : ""} left`;
  return `${Math.max(1, Math.floor(seconds / 60))} min left`;
}

export async function initPasses(context) {
  ctx = context;
  try { cfg = await config(); } catch (_) { cfg = null; }
  const testLogin = LOCAL && cfg && !cfg.google_client_id;
  ctx.passesOn = !!(cfg && (cfg.google_client_id || testLogin));
  if (cfg && cfg.plans) {
    for (const [id, p] of Object.entries(cfg.plans)) {
      const el = document.querySelector(`.plan[data-plan="${id}"]`);
      if (el) el.querySelector(".price").textContent = "Rs " + p.amount;
    }
  }
  $("entitle").onclick = () => openPasses();
  $("open-invite").onclick = () => openInvite();
  $("pass-back").onclick = () => ctx.resume();
  $("invite-back").onclick = () => ctx.resume();
  $("go-practise").onclick = () => ctx.practise();
  $("pass-running-back").onclick = () => ctx.resume();
  $("extend").onclick = () => { extendOpen = true; step = "choose"; paint(); $("buy-block").scrollIntoView({ behavior: "smooth", block: "center" }); };
  for (const el of document.querySelectorAll(".plan")) el.onclick = () => choosePlan(el.dataset.plan);
  $("buy-cta").onclick = () => { step = "checkout"; say(""); paint(); };
  $("have-pass").onclick = () => { step = "signin"; say(""); paint(); };
  $("checkout-back").onclick = () => { step = "choose"; say(""); paint(); };
  try { $("phone").value = localStorage.getItem(PHONE) || ""; } catch (_) { /* private mode */ }
  $("pay").onclick = pay;
  const signOut = () => { session.clear(); ctx.setEntitlement({ ...ctx.state.ent, account: null, kind: ctx.state.ent && ctx.state.ent.hasTrial ? (ctx.state.ent.trialLeft > 0 ? "trial" : "none") : "none", secondsLeft: (ctx.state.ent && ctx.state.ent.trialLeft) || 0, expiresAt: null }); step = "choose"; extendOpen = false; paint(); };
  $("signout").onclick = signOut;
  $("signout2").onclick = signOut;
  $("start-days").onclick = startDays;
  if (testLogin) {
    $("testlogin").style.display = "block";
    $("testlogin-go").onclick = () => onGoogle("test:" + ($("testlogin-email").value.trim() || "tester@example.com"));
  }
  choosePlan(ctx.state.plan || "w");
  if (await resumePendingOrder()) return;
  // "Get the 7-day pass" on the pricing page: straight to checkout for that pass.
  const want = new URLSearchParams(location.search).get("buy");
  if (want === "w" || want === "m") {
    history.replaceState(null, "", location.pathname);
    ctx.track("mock_buy_link", { plan: want });
    await openPasses("", { plan: want, checkout: true });
  }
}

// ------------------------------------------------------------------ passes

function choosePlan(id) {
  ctx.state.plan = id;
  for (const el of document.querySelectorAll(".plan")) el.classList.toggle("on", el.dataset.plan === id);
  const p = planOf(id);
  if (p) {
    $("buy-cta").textContent = `Buy the ${p.label.replace("-Day Pass", "-day pass")} →`;
    $("pay").textContent = `Pay Rs ${p.amount} →`;
    $("checkout-plan").textContent = `${p.label} · Rs ${p.amount}`;
  }
}

/**
 * @param {string} [message]
 * @param {{plan?: "w"|"m", checkout?: boolean}} [opts]  the pricing page's buttons
 *        open the app straight at checkout for the pass that was clicked
 */
export async function openPasses(message, opts = {}) {
  ctx.show("s-pass");
  say(message || "");
  if (opts.plan && planOf(opts.plan)) choosePlan(opts.plan);
  if (opts.checkout) { step = "checkout"; if (ctx.state.ent && ctx.state.ent.kind === "pass") extendOpen = true; }
  if (!ctx.passesOn) {
    $("pass-body").style.display = "none";
    say("Passes open in a few days. Until then, invite a friend: you both get 20 free minutes.", "");
    return;
  }
  $("pass-body").style.display = "block";
  paint();
  ctx.track("mock_pass_view", { signed_in: !!(ctx.state.ent && ctx.state.ent.account), has_pass: ctx.state.ent && ctx.state.ent.kind === "pass" });
  await showGoogleButton();
}

async function showGoogleButton() {
  if (!cfg || !cfg.google_client_id || googleReady || $("checkout").style.display === "none") return;
  try {
    await loadScript("https://accounts.google.com/gsi/client");
    window.google.accounts.id.initialize({ client_id: cfg.google_client_id, callback: (r) => onGoogle(r.credential), ux_mode: "popup" });
    window.google.accounts.id.renderButton($("gbutton"), { theme: "filled_black", size: "large", shape: "pill", text: "continue_with", width: 300 });
    googleReady = true;
  } catch (_) { say("Google sign-in could not load. Check your connection and try again.", "bad"); }
}

function paint() {
  const ent = ctx.state.ent || {};
  // Cashfree takes over the page, which would end a running interview with no
  // report. Say so, and keep the pay buttons out of reach until it is over.
  const running = !!(ctx.running && ctx.running());
  $("pass-running").style.display = running ? "flex" : "none";
  $("buy-cta").disabled = running;
  $("pay").disabled = running;
  const account = ent.account;
  const live = ent.kind === "pass";

  // Your account, when a pass is running.
  $("account-card").style.display = live ? "block" : "none";
  if (live) {
    $("pass-who").textContent = account ? account.email : "";
    $("pass-days").textContent = daysLeft(ent.secondsLeft);
    $("pass-until").textContent = `Unlimited mocks until ${when(ent.expiresAt)}`;
    const inv = ent.invite;
    $("pass-stats").textContent = inv
      ? `${inv.friends_tried} friend${inv.friends_tried === 1 ? "" : "s"} tried it through your link · ${inv.friends_bought} bought a pass`
      : "";
    $("extend").textContent = extendOpen ? "Choosing…" : "Extend my pass";
  }

  // Buying: hidden behind "Extend" once a pass is live.
  const buying = !live || extendOpen;
  const signinOnly = step === "signin" && !account;
  if (step === "signin" && account) step = "choose";       // signed in: nothing left to ask
  $("buy-block").style.display = buying && step === "choose" ? "block" : "none";
  $("checkout").style.display = buying && (step === "checkout" || signinOnly) ? "block" : "none";
  $("pass-signin").style.display = account ? "none" : "block";
  $("pass-pay").style.display = account && !signinOnly ? "block" : "none";
  $("have-pass-row").style.display = account ? "none" : "block";
  $("checkout-label").textContent = signinOnly ? "Welcome back" : "You are buying";
  $("checkout-plan").style.display = signinOnly ? "none" : "block";
  $("checkout-back").textContent = signinOnly ? "Back" : "Change";
  $("signin-why").textContent = signinOnly
    ? "Sign in with the Google account you bought with, and your pass appears here."
    : "Sign in with Google first, so your pass follows you to any phone or laptop.";
  if (account) $("pass-who2").textContent = `Signed in as ${account.email}`;

  // Words at the top follow the state, so the page never asks for money twice.
  $("pass-kicker").textContent = live ? "Your account" : "Passes";
  $("pass-title").innerHTML = live ? 'Your pass is <em>live.</em>' : 'Unlimited mocks, <em>one payment.</em>';
  $("pass-lede").textContent = live
    ? "Practise as much as you like until it ends. Buying again adds the days on top, and nothing renews by itself."
    : "No subscription, and it never renews by itself. The clock starts when you pay, and the pass ends exactly on time.";

  const banked = (ent.invite && ent.invite.banked_days) || 0;
  $("freedays").style.display = banked > 0 ? "block" : "none";
  if (banked > 0) {
    $("freedays-text").textContent = `You have ${banked} free day${banked > 1 ? "s" : ""} from friends who bought a pass.`;
    $("start-days").textContent = account ? `Start my ${banked} free day${banked > 1 ? "s" : ""}` : "Sign in above to start them";
    $("start-days").disabled = !account;
  }
  if (buying && (step === "checkout" || signinOnly)) showGoogleButton();
}

/* A Google account is all it takes. No Gemini key is needed to sign in or to
 * buy; the key only matters once an interview starts. */
async function onGoogle(credential) {
  const cameToSignIn = step === "signin";
  say("Signing you in…");
  try {
    ctx.setEntitlement(await signIn(credential, ctx.state.hash));
    ctx.track("mock_sign_in", { with_key: !!ctx.state.hash, to_buy: !cameToSignIn });
    const live = ctx.state.ent.kind === "pass";
    if (cameToSignIn) { step = "choose"; say(live ? "Welcome back. Your pass is live." : "Signed in. There is no active pass on this account, so choose one below.", live ? "ok" : ""); }
    else say("");
    paint();
    if (!cameToSignIn && !live) $("phone").focus();
  } catch (err) { say(err.message, "bad"); }
}

async function pay() {
  const phone = $("phone").value.replace(/\D/g, "");
  if (phone.length < 10) { say("Enter your 10-digit mobile number. Cashfree needs it for the receipt.", "bad"); return; }
  $("pay").disabled = true;
  say("Opening secure checkout…");
  try {
    const order = await startOrder(ctx.state.plan || "w", phone);
    try {
      localStorage.setItem(PENDING, JSON.stringify({ order_id: order.order_id, hash: ctx.state.hash || null, at: Date.now() }));
      localStorage.setItem(PHONE, phone.slice(-10));
    } catch (_) { /* private mode */ }
    ctx.track("begin_checkout", { product: "prep-sarthi", plan: ctx.state.plan || "w", value: order.amount, currency: "INR" });
    await loadScript("https://sdk.cashfree.com/js/v3/cashfree.js");
    window.Cashfree({ mode: order.mode }).checkout({ paymentSessionId: order.payment_session_id, redirectTarget: "_self" });
  } catch (err) {
    say(err.status === 401 ? "Your sign-in expired. Sign in again." : err.message, "bad");
    if (err.status === 401) { session.clear(); ctx.setEntitlement({ ...ctx.state.ent, account: null }); paint(); }
    $("pay").disabled = false;
  }
}

/* Back from Cashfree (or the tab was closed mid-payment): ask until it is settled. */
async function resumePendingOrder() {
  let pending = null;
  try { pending = JSON.parse(localStorage.getItem(PENDING) || "null"); } catch (_) { /* corrupt */ }
  const fromUrl = new URLSearchParams(location.search).get("order_id");
  if (fromUrl) pending = { order_id: fromUrl, hash: (pending && pending.hash) || null, at: (pending && pending.at) || Date.now() };
  if (!pending || !session.get() || Date.now() - (pending.at || 0) > 3600_000) return false;
  if (fromUrl) history.replaceState(null, "", location.pathname);
  ctx.state.hash = ctx.state.hash || pending.hash;
  ctx.show("s-pass");
  $("pass-body").style.display = "none";
  // Cashfree sends people back with ?order_id= after a payment, good or bad.
  // Arriving without it means they pressed Back on Cashfree's page: ask a few
  // times in case the money did move, then stop pretending something is pending.
  const cameBackByHand = !fromUrl;
  say(cameBackByHand ? "Checking whether a payment went through…" : "Confirming your payment… keep this page open.");
  for (let i = 0; i < (cameBackByHand ? 3 : 40); i++) {
    let r;
    try { r = await orderStatus(pending.order_id, pending.hash); } catch (_) { r = { status: "pending" }; }
    if (r.status === "paid") {
      try { localStorage.removeItem(PENDING); } catch (_) { /* ignore */ }
      ctx.setEntitlement(r.entitlement);
      ctx.track("purchase", { product: "prep-sarthi", plan: r.plan });
      step = "choose"; extendOpen = false;
      $("pass-body").style.display = "block"; paint();
      say(`Paid. Your ${r.plan} is live. Practise as much as you like.`, "ok");
      $("pass-back").textContent = "Back";
      return true;
    }
    if (r.status === "failed") {
      try { localStorage.removeItem(PENDING); } catch (_) { /* ignore */ }
      step = "choose";
      $("pass-body").style.display = "block"; paint();
      say("That payment did not go through, and nothing was charged. You can try again.", "bad");
      return true;
    }
    await new Promise((ok) => setTimeout(ok, 2500));
  }
  if (cameBackByHand) {
    try { localStorage.removeItem(PENDING); } catch (_) { /* ignore */ }
    step = "checkout";
    $("pass-body").style.display = "block"; paint();
    say("That payment was not completed, and nothing was charged. You can pay whenever you are ready.", "");
    return true;
  }
  $("pass-body").style.display = "block"; paint();
  say("The payment is still being confirmed. If money left your account, your pass will appear here within a few minutes. Otherwise write to support@interviewsarthi.com.", "");
  return true;
}

async function startDays() {
  try {
    await startFreeDays();
    ctx.setEntitlement(await ctx.refresh());
    extendOpen = false; step = "choose";
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
