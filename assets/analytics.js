/* Interview Sarthi — website analytics.
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
 * What this reports: page views, plus the three steps of the funnel —
 * download_click, begin_checkout, purchase. Nothing about the app itself is
 * touched; the desktop app still sends nothing anywhere.
 */
(function () {
  "use strict";

  var GA4_ID = "G-CCFHWPJD9K";
  var CLARITY_ID = "XXXXXXXXXX";

  var gaOn = GA4_ID.indexOf("XXXX") === -1;
  var clarityOn = CLARITY_ID.indexOf("XXXX") === -1;

  /* ---- Google Analytics 4 ---- */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  if (gaOn) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4_ID;
    document.head.appendChild(s);
    gtag("js", new Date());
    gtag("config", GA4_ID, { anonymize_ip: true });
  }

  /* ---- Microsoft Clarity ---- */
  if (clarityOn) {
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

  /* The three passes, keyed by the Dodo product id in the checkout link, so a
   * price change on the site does not silently desync the reported revenue. */
  var PASSES = {
    pdt_0NmLzNTWbybTsXtpmtmaH: { name: "7-Day Pass", value: 399 },
    pdt_0NmHQqaKlKiZ57ISIRzdn: { name: "1-Month Pass", value: 999 },
    pdt_0NmHNZ2I6qiJg6CrzInBg: { name: "3-Month Pass", value: 1999 }
  };

  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href") || "";

    if (href.indexOf("releases/latest/download") !== -1) {
      track("download_click", {
        /* where on the page the click came from, so you can tell whether the
         * hero, the pricing table or the closing CTA is doing the work */
        placement: a.closest("nav") ? "nav" : (a.closest("section") ? "section" : "page")
      });
      return;
    }

    var buy = href.match(/checkout\.dodopayments\.com\/buy\/(pdt_[A-Za-z0-9]+)/);
    if (buy) {
      var pass = PASSES[buy[1]] || { name: buy[1], value: 0 };
      track("begin_checkout", {
        currency: "INR",
        value: pass.value,
        items: [{ item_id: buy[1], item_name: pass.name, price: pass.value, quantity: 1 }]
      });
    }
  }, true);

  /* Dodo sends the buyer back to thanks.html?license_key=... — that redirect is
   * the only purchase signal a static site gets. The key itself is a secret and
   * is never sent on; localStorage just stops a page refresh double-counting. */
  if (new URLSearchParams(location.search).get("license_key")) {
    var once = "is_purchase_reported";
    try {
      if (!localStorage.getItem(once)) {
        localStorage.setItem(once, "1");
        track("purchase", { currency: "INR" });
      }
    } catch (e) {
      track("purchase", { currency: "INR" });
    }
  }
})();
