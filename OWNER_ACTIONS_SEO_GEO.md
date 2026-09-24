# Owner actions and 90-day SEO roadmap

Updated **24 September 2026**. Use [the audit and growth plan](SEO_AUDIT_AND_GROWTH_PLAN.md) for implementation and deployment status. These are remaining owner/account actions and a proposed operating plan; no Search Console, GA4 or Bing account changes, outreach or customer review requests are implied.

## Cover the whole website

InterviewSarthi introduces three products: **Apply** finds jobs and helps fill applications; **Prep** conducts spoken mock interviews and gives feedback; **Live** supplies answer suggestions during calls on supported Windows setups. Their marketing destinations are `/apply/`, `/prep/` and `/live/`.

The Apply subdomain already has public job pages, company/role hubs and its own sitemap. It is not only a sign-in page. Marketing-site deployment and Apply backend deployment are separate; verify both in the release report. [Apply public audit](research/seo-apply-public-audit-2026-09-24.md)

## First: establish owner-controlled measurements

1. **Search Console:** verify a Domain property for `interviewsarthi.com` through its DNS provider if one is not already available. Preserve existing verification. A Domain property covers the main host and Apply subdomain; filter reports by host/path to compare them separately. Do not paste credentials into repository files.
2. **Export the previous 90 days:** save dated query, page, country and device reports with clicks, impressions, CTR and position; retain the 28-day comparison too. Separate brand queries from new-user discovery. Export indexing, sitemap and available job-enhancement findings. No current account baseline has been obtained in this audit.
3. **Inspect representative URLs:** homepage, each product page, a guide, Prep walkthrough, an Apply job, company hub and role hub. Compare submitted versus Google-selected canonical, rendered content and indexing eligibility. Private app/receipt pages should retain their intended exclusions. Submit or verify both `https://interviewsarthi.com/sitemap.xml` and `https://apply.interviewsarthi.com/sitemap.xml`.
4. **Bing Webmaster Tools:** verify the relevant property/properties, inspect both hosts and their sitemaps, and review indexing and available AI citation reports. Check IndexNow workflow responses. A successful notification is not guaranteed crawling, indexing or ranking. [IndexNow documentation](https://www.indexnow.org/documentation)
5. **Record releases:** annotate actual marketing and backend deployment dates, promotions and price changes. This makes later comparisons interpretable.

## Measure choosing an app separately from using it

Validate the implemented `product_click` event in GA4 DebugView using controlled test traffic, then register these event-scoped custom dimensions if needed:

| Parameter | Implemented values | Meaning |
| --- | --- | --- |
| `product` | `apply`, `prep`, `live` | Which product the link leads to |
| `placement` | `navigation`, `product_card`, `pricing`, `footer`, `page` | Where the link was clicked |
| `destination_kind` | `product_page`, `application` | Product explanation versus app destination |

Treat this as a choice/handoff measure, optionally a secondary key event. It is not a signup, finished mock interview, installed app or sale. Track activation/completion separately where each app supports it. Existing `download_click` and checkout events also represent steps, not completed outcomes. Reconcile real purchases and refunds against payment-provider records; browser receipt events are not a sales ledger.

Retain `ai_referral_visit` with `ai_source` and `landing_page` as a limited referral classification. Missing referral signals remain unattributed. Cross-domain journeys need validation; do not assume a marketing visit stays attributable through the Apply app and payment provider. Never send CVs, spoken answers, email addresses, Gemini keys, license keys or receipt queries to analytics.

## Work over the next 90 days

| Period | Priority | Evidence to keep |
| --- | --- | --- |
| Days 1–30 | Establish the account baseline, verify indexing after release, improve the CV/JD Prep walkthrough and show Apply's actual review-before-submit workflow | Dated exports, inspection results, real screenshots and clearly labelled illustrative examples |
| Days 31–60 | Improve pages with relevant impressions but weak clicks or app handoffs; source-check employer guides; record supported Live capture tests and a complete Prep demo | Page/query change log, employer sources, owned recordings, captions and test conditions |
| Days 61–90 | Expand only demonstrated gaps; publish a benchmark only after running the existing protocol; develop authentic creator/educator relationships | Actual observations, consent where needed, disclosed ownership and voluntary relevant citations |

Run the fixed sample in [TRACKING_QUERIES.md](TRACKING_QUERIES.md) monthly. Review traffic weekly and compare equivalent 28-day periods, considering hiring seasonality and small sample sizes. Do not create repetitive company/city/role pages merely to increase page count. Correct inaccurate public job geography and relevance before promoting more catalogue pages.

Keep official profiles consistent with all three products when the owner next updates them. Any external posting, messaging or review request requires an explicit send instruction; this document does not perform those actions.

## Current search guidance

Google Search ignores `llms.txt` for ranking and requires no special AI markup. FAQ rich results stopped appearing in May 2026; keep useful FAQs for readers. Neither is a promised traffic channel. [Google AI guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), [Google updates](https://developers.google.com/search/updates)

In Search Console, check the inherited Search generative AI inclusion setting and the impressions report if available; do not infer a fault when a low-traffic property lacks the report. No settings were changed here. [Control](https://support.google.com/webmasters/answer/16908024), [report](https://support.google.com/webmasters/answer/16984139)

There is no justified numeric traffic or ranking promise without a baseline. Judge progress by relevant discovery, successful product use and confirmed business outcomes. Account reports, field performance, Store publishing and installed Windows compatibility still require owner access or the appropriate live environment.
