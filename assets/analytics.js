/* Interview Sarthi: website analytics.
 *
 * Paste your two IDs below and the site starts reporting. A value left as its
 * placeholder simply keeps that tool switched off, so this file is safe to ship
 * before you have signed up for either.
 *
 *   GA4_ID      analytics.google.com  ->  Admin  ->  Data streams  ->  your web
 *               stream  ->  Measurement ID.  Looks like G-ABCD1234EF.
 *   CLARITY_ID  clarity.microsoft.com ->  new project  ->  Settings  ->  Setup
 *               ->  the id inside the install snippet. Looks like abcd1234ef.
 *
 * What this reports: page views, plus the three steps of the funnel:
 * download_click, begin_checkout, purchase. Nothing about the app itself is
 * touched; the desktop app still sends nothing anywhere.
 */
(function () {
  "use strict";

  // The homepage routes legacy links and receipts before any tracking starts.
  if (window.sarthiHomeRedirecting) return;

  var GA4_ID = "G-CCFHWPJD9K";
  var CLARITY_ID = "yb9mq7tzkq";

  var gaOn = GA4_ID.indexOf("XXXX") === -1;
  var clarityOn = CLARITY_ID.indexOf("XXXX") === -1;

  /* ---- Google Analytics 4 ---- */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  /* Remove receipt/query secrets from the browser URL before either analytics
   * SDK can read it. Keep the key in memory for the existing receipt handler. */
  var incomingParams = new URLSearchParams(location.search);
  var licenceKey = incomingParams.get("license_key");
  var privateReturn = incomingParams.has("license_key");
  if (privateReturn) {
    try { history.replaceState(null, "", location.pathname + location.hash); }
    catch (e) { gaOn = false; clarityOn = false; }
  }

  if (gaOn) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4_ID;
    document.head.appendChild(s);
    gtag("js", new Date());
    gtag("config", GA4_ID, {
      anonymize_ip: true,
      page_location: location.origin + location.pathname,
      page_referrer: safeReferrer(document.referrer)
    });
  }

  /* ---- Microsoft Clarity ---- */
  /* Receipt content can include a license key; never record that page.
   * The Prep Sarthi app shows interview captions and the report, which are the
   * visitor's own CV and words; session recording never runs there either. */
  /* The app moved from /mock/app to /prep/app on 23 Sep 2026. Both are still checked:
   * the old path keeps a redirect stub, and a visitor sitting on it for the moment
   * before the redirect fires must not be recorded either. */
  var inPrepApp = location.pathname.indexOf("/prep/app") === 0 ||
                  location.pathname.indexOf("/mock/app") === 0;
  if (clarityOn && !privateReturn && !inPrepApp && location.pathname !== "/thanks.html") {
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1;
      t.src = "https://www.clarity.ms/tag/" + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", CLARITY_ID);
  }

  /* ---- Funnel events ----
   * Named so the same call reaches both tools: GA4 gets a gtag event, Clarity
   * gets a tag you can filter recordings by. */
  function track(name, params) {
    if (gaOn) gtag("event", name, params || {});
    if (clarityOn && window.clarity) window.clarity("set", name, "yes");
  }

  function safeReferrer(value) {
    try { var url = new URL(value); return url.origin + url.pathname; }
    catch (e) { return ""; }
  }

  function aiSource(value) {
    var aliases = {
      "chatgpt": "chatgpt", "chatgpt.com": "chatgpt", "chat.openai.com": "chatgpt",
      "claude": "claude", "claude.ai": "claude",
      "perplexity": "perplexity", "perplexity.ai": "perplexity",
      "gemini": "gemini", "gemini.google.com": "gemini",
      "copilot": "copilot", "copilot.microsoft.com": "copilot"
    };
    return aliases[String(value || "").toLowerCase().replace(/^www\./, "")] || "";
  }
  var referralSource = aiSource(incomingParams.get("utm_source"));
  if (!referralSource) {
    try { referralSource = aiSource(new URL(document.referrer).hostname); } catch (e) { }
  }
  /* One event per source per browser tab session. Attribution is a signal,
   * not proof of an AI recommendation. No raw referrer/query values are sent. */
  if (referralSource && !privateReturn && location.pathname !== "/thanks.html") {
    var referralOnce = "ai_referral_" + referralSource;
    var shouldReport = true;
    try {
      shouldReport = !sessionStorage.getItem(referralOnce);
      if (shouldReport && gaOn) sessionStorage.setItem(referralOnce, "1");
    } catch (e) { /* Storage denied: still permit this page's event. */ }
    if (shouldReport && gaOn) gtag("event", "ai_referral_visit", {
      ai_source: referralSource, landing_page: location.pathname
    });
  }

  /* The passes, keyed by the plan code in the checkout link
   * (license.interviewsarthi.com/buy?plan=30d), so a price change on the site
   * does not silently desync the reported revenue. Rupee prices: the value
   * is what the report is for, not what a foreign card was charged.
   * Only 2d and 30d are sold since 25 Sep 2026. The two withdrawn passes stay
   * here, at the price they were sold for, so a key bought before then still
   * reports its value when it reaches thanks.html. No page links to them. */
  var PASSES = {
    "2d": { name: "2-Day Pass", value: 99 },
    "30d": { name: "1-Month Pass", value: 299 },
    "7d": { name: "7-Day Pass", value: 399 },
    "90d": { name: "3-Month Pass", value: 1999 }
  };
  /* The licence server names the pass by its label ("1-Month Pass"). */
  function passByName(label) {
    for (var code in PASSES) {
      if (PASSES[code].name === label) return { id: code, name: label, value: PASSES[code].value };
    }
    return null;
  }

  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href") || "";

    // Measure which app a visitor chooses from any marketing page. Never send
    // link queries, CV text, keys, email or a full destination URL.
    try {
      var target = new URL(href, location.href);
      var product = "", kind = "product_page";
      var ours = target.origin === location.origin || target.origin === "https://interviewsarthi.com";
      if (target.hostname === "apply.interviewsarthi.com" && /^https?:$/.test(target.protocol)) {
        product = "apply"; kind = "application";
      } else if (ours) {
        var productPath = target.pathname.replace(/\/index\.html$/, "/").replace(/\/$/, "");
        if (productPath === "/apply") product = "apply";
        if (productPath === "/prep" || productPath === "/mock") product = "prep";
        if (productPath === "/live") product = "live";
        if (productPath === "/prep/app" || productPath === "/mock/app") {
          product = "prep"; kind = "application";
        }
      }
      if (product && !privateReturn && location.pathname !== "/thanks.html" && !inPrepApp) {
        track("product_click", {
          product: product, destination_kind: kind,
          placement: a.closest(".quick-pick") ? "quick_pick" : a.closest("header, nav") ? "navigation" : a.closest("#products") ? "product_card" :
            a.closest("#plans, #pricing") ? "pricing" : a.closest("footer") ? "footer" : "page"
        });
      }
    } catch (e) { /* Invalid or non-web links still navigate normally. */ }

    /* Both install paths count as a download: the Microsoft Store listing and
     * the direct .exe on GitHub Releases. */
    if (href.indexOf("releases/latest/download") !== -1 ||
        href.indexOf("apps.microsoft.com") !== -1) {
      /* platform.js gates this anchor on non-Windows devices: the tap opens a
       * "send me the link" sheet instead of downloading, so it is not a
       * download. The sheet's own "Download anyway" link is ungated and still
       * lands here. */
      if (a.hasAttribute("data-gated")) return;
      track("download_click", {
        /* where on the page the click came from, so you can tell whether the
         * hero, the pricing table or the closing CTA is doing the work */
        placement: a.closest("nav") ? "nav" : (a.closest("section") ? "section" : "page"),
        /* which install path: the Store listing or the direct installer */
        method: href.indexOf("apps.microsoft.com") !== -1 ? "store" : "exe"
      });
      return;
    }

    /* Every buy button goes to license.interviewsarthi.com/buy?plan=30d (or 2d), which
     * sends the buyer on to Dodo or Cashfree. The plan code names the pass. */
    var buy = href.match(/license\.interviewsarthi\.com\/buy\?plan=(\d+d)\b/);
    if (buy) {
      var pass = PASSES[buy[1]] || { name: buy[1], value: 0 };
      /* Park it so the purchase event on thanks.html can report the amount.
       * The return trip carries the key (Dodo) or an order id (Cashfree),
       * never the product. */
      try {
        localStorage.setItem("pending_pass", JSON.stringify({
          id: buy[1], name: pass.name, value: pass.value, at: Date.now()
        }));
      } catch (e) { /* private mode: the purchase still reports, without value */ }
      track("begin_checkout", {
        currency: "INR",
        value: pass.value,
        items: [{ item_id: buy[1], item_name: pass.name, price: pass.value, quantity: 1 }]
      });
    }
  }, true);

  /* A purchase reaches thanks.html one of two ways. Dodo sends the buyer back
   * with ?license_key=..., read here on load. The licence server (Cashfree)
   * sends ?order_id=..., and thanks.html calls window.sarthiReportPurchase
   * once its poll has the key. The key itself is a secret and is never sent
   * on; localStorage just stops a page refresh double-counting. */
  function reportPurchase(key, passLabel) {
    if (!key) return;
    /* A short non-reversible hash of the key. It gives GA4 a transaction_id to
     * deduplicate on and lets a second purchase report, without the key itself
     * ever leaving the page. */
    var txid = (function (str) {
      var h = 5381;
      for (var i = 0; i < str.length; i++) { h = ((h << 5) + h + str.charCodeAt(i)) | 0; }
      return "t" + (h >>> 0).toString(36);
    })(key);

    var pending = null;
    try { pending = JSON.parse(localStorage.getItem("pending_pass") || "null"); } catch (e) { }
    /* A buyer who paid on another device, or in private mode, has nothing
     * parked; the licence server's pass label fills the gap. */
    if (!(pending && pending.value) && passLabel) pending = passByName(passLabel);

    var payload = { currency: "INR", transaction_id: txid };
    if (pending && pending.value) {
      payload.value = pending.value;
      payload.items = [{
        item_id: pending.id, item_name: pending.name,
        price: pending.value, quantity: 1
      }];
    }

    /* Keyed to the licence, so buying a second pass in the same browser still
     * reports; only a refresh of the same receipt is suppressed. */
    var once = "purchase_reported_" + txid;
    try {
      if (!localStorage.getItem(once)) {
        localStorage.setItem(once, "1");
        localStorage.removeItem("pending_pass");
        track("purchase", payload);
      }
    } catch (e) {
      track("purchase", payload);
    }
  }
  window.sarthiReportPurchase = reportPurchase;
  window.sarthiTrack = track;
  if (licenceKey) reportPurchase(licenceKey, "");
})();
