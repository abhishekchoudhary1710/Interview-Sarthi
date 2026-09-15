# SEO/GEO implementation report

Completed locally: 15 September 2026. Repository: `abhishekchoudhary1710/Interview-Sarthi`.
Base: `e942363`. Review branch: `seo-geo-entity-2026-09`.

## Outcome

Implemented the repository portions of the supplied plan after reviewing the current source, live website and official competitor/provider sources. Website changes are prepared for a draft pull request; they have not been merged or deployed. GitHub repository description, homepage and eight relevant topics were updated directly.

The biggest concrete corrections are consistent 30-minute trial copy, the closing weekly checkout button pointing to the weekly product, stable organization/software/founder relationships, a public Facts page, evidence-based comparison content and repeatable SEO checks.

## Product facts used

The current homepage pricing cards, offers and FAQ support a 30-minute trial per computer; ₹99/2 days/1 device; ₹399/7 days/1 device; ₹999/30 days/2 devices; ₹1,999/90 days/2 devices. Passes do not automatically renew. Windows 10 version 2004+ and Windows 11; English, Hindi and Hinglish; user-supplied Gemini key. Google quotas and paid usage are separate.

These are verified **advertised website facts**. Desktop enforcement, Store text and Dodo settings were not independently tested. `SITE_FACTS.md` records evidence and these boundaries. No desktop behavior or billing product configuration was changed.

## Schema and content

- Standard organization, website, software and founder IDs; existing organization authorship retained rather than inventing individual review credentials.
- Organization `sameAs` uses the verified public repository. Founder GitHub identity comes from the existing About page and repository owner. Unverified social and Store identity claims were not added.
- Software schema links to the organization and official download destination. Existing offer prices preserved.
- Facts/About, category page, comparison pages, guide hub and Hinglish hub have clearer roles and links.
- Comparison metadata and unordered product list consistently describe seven products. Public sources and review dates are explicit; inaccessible current prices are marked unknown. Repeated unsupported competitor claims were removed.
- Statistics URL is retained as a source-led research resource; unsupported population figures and unlike-period savings claims were removed. No invented research was published.
- Screen-sharing and interview-rules pages now focus on permission and documented limitations. Their old FAQ schema was removed where its claims no longer match visible content.
- Existing company-guide content largely remains; trial, publisher links and modification metadata changed. A complete re-verification of hiring calendars/salary bands was outside the available evidence and is listed for owner follow-up.

## Crawl and date handling

`robots.txt`, existing Search Console verification, IndexNow workflow, canonical domain and receipt/error noindex behavior are preserved. The sitemap now contains 38 indexable pages, including Facts. A reviewed allow-list with explicit dates drives generation; CI detects sitemap drift. Existing URLs remain intact.

New dates reflect this content review; formatting-only dates for Terms/Refunds were not set to today. Generator builds do not advance dates. Live pre-deployment checks returned 200 for all 11 sampled public endpoints, including robots and sitemap. That does not establish bot-specific CDN behavior or actual indexing.

## Analytics and conversion

Added an allow-listed `ai_referral_visit` event with source category and landing path; query strings are not included. Source events are deduplicated per browser tab session. Ordinary Google traffic and lookalike malicious hostnames are not classified as AI referrals. Existing SDK enable flags remain in effect.

Receipt query values are removed before analytics initialization, Clarity recording is excluded from receipts, and receipt rendering/purchase tracking still work. The incorrect final 7-Day CTA now uses the same product as the weekly pricing card. Analytics calls the ₹99 plan `2-Day Pass`.

Client-side purchase events remain return-page signals, not verified payment records. No paid checkout, remote analytics dashboard or desktop app test was performed.

## Validation

```text
SEO audit: 40 pages, 38 indexable, 0 errors, 0 warnings
Sitemap matches the reviewed page manifest.
Python regression tests: 8 passed
Node analytics regression tests: 6 passed
Browser viewport checks: 80 passed (40 pages at 390px and 1366px)
Browser receipt rendering, weekly checkout destinations and AI event checks: passed
Live HTTP baseline: 11/11 sampled URLs returned 200
```

One mobile statistics-table overflow was found and fixed. Browser execution used Microsoft Edge through Playwright with all external requests blocked; no test analytics or purchases were sent. Screenshots/results are in ignored `.seo-preview/`. This is not a Lighthouse or field Core Web Vitals score.

The baseline audit and final inventory are retained in `research/seo-baseline.json` and `research/seo-final.json`. CI runs sitemap, SEO, Python and Node checks on pull requests and relevant pushes. Browser QA is an optional local command documented in README.

## Reach work and remaining owner actions

Added research findings with sources, a benchmark protocol and empty dataset, 25 fixed tracking queries, empty monthly measurement CSV, and a 90-day roadmap. The public Hinglish hub includes a practical mock-call checklist.

Owner work: confirm Store/app/billing facts, review and release the branch, inspect important URLs in Search Console, configure GA4 report dimensions, collect real benchmark observations, verify genuine official profiles and seek independent reviews. No outreach, fake profiles, reviews, backlinks or benchmark results were created. See `OWNER_ACTIONS_SEO_GEO.md`.

The comparative/statistics rewrites may change search impressions after recrawl; monitor query/page performance around the release date. Higher reach and AI recommendations cannot be verified before deployment and observation.

## Changed files

The file inventory below lists each changed or new repository file relative to the baseline.
- `.github/workflows/seo-checks.yml` ? CI validation.
- `.gitignore` ? Exclude runtime caches and local browser artifacts.
- `OWNER_ACTIONS_SEO_GEO.md` ? Release checks, account tasks and 90-day reach roadmap.
- `README.md` ? Public repository identity, setup, validation and maintenance.
- `SEO_GEO_IMPLEMENTATION_REPORT.md` ? Implementation outcomes, evidence, validation and limits.
- `SITE_FACTS.md` ? Maintainer fact/evidence register.
- `TRACKING_QUERIES.md` ? Fixed query set and measurement method.
- `about.html` ? Trial, product identity, founder links and editorial standards.
- `ai-interview-assistant-india.html` ? Distinct educational category guide with practical tool evaluation.
- `ai-interview-statistics-india.html` ? Primary-source research resource replacing unsupported aggregates.
- `assets/analytics.js` ? AI source classification, receipt privacy, preserved funnel events and pass label.
- `best-ai-interview-assistant-india.html` ? Source-reviewed comparison, disclosure, verification gaps and metadata.
- `can-interviewer-see-my-screen.html` ? Source-backed screen-sharing explanation and permission boundaries.
- `facts.html` ? New public identity, pricing, platform and editorial facts page.
- `free-gemini-api-key-guide.html` ? Current key/project guidance, quotas and source links.
- `guides/accenture-cognizant-capgemini-hr-interview.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/accenture-interview-questions-freshers.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/ai-in-interviews-rules.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/capgemini-interview-questions-freshers.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/career-gap-explanation-interview.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/cognizant-interview-questions-freshers.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/first-job-interview-guide-freshers.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/hinglish-interview-answers.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/index.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/infosys-interview-questions-freshers.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/reason-for-job-change.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/salary-expectation-answer.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/self-introduction-interview-hinglish.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/strengths-and-weaknesses-interview.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/tcs-infosys-wipro-hr-interview-questions.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/tcs-interview-questions-freshers.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/why-should-we-hire-you.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `guides/wipro-interview-questions-freshers.html` ? Guide trial/publisher/schema consistency and navigation; hub/rules updates where relevant.
- `help.html` ? Facts link, responsible-use copy, breadcrumbs and social metadata.
- `hinglish-interview-help.html` ? Practical language checklist, illustrative example label and related guides.
- `hr-interview-questions-hinglish.html` ? Entity, breadcrumb and footer links.
- `index.html` ? Product positioning, trial/schema, evidence-based pricing copy and weekly CTA fix.
- `online-interview-tips.html` ? Entity, breadcrumb and footer links.
- `privacy.html` ? Factual website analytics disclosure, breadcrumbs and social metadata.
- `refunds.html` ? Breadcrumb and social metadata only; policy preserved.
- `research/README.md` ? Research evidence, inventory or unfilled measurement protocol/template.
- `research/SEO_GEO_RESEARCH_2026-09-15.md` ? Research evidence, inventory or unfilled measurement protocol/template.
- `research/benchmark-template.csv` ? Research evidence, inventory or unfilled measurement protocol/template.
- `research/live-http-baseline.json` ? Research evidence, inventory or unfilled measurement protocol/template.
- `research/query-tracking-template.csv` ? Research evidence, inventory or unfilled measurement protocol/template.
- `research/seo-baseline.json` ? Research evidence, inventory or unfilled measurement protocol/template.
- `research/seo-final.json` ? Research evidence, inventory or unfilled measurement protocol/template.
- `scripts/check_live_site.py` ? Automated audit, reviewed sitemap dates or read-only HTTP checks.
- `scripts/generate_sitemap.py` ? Automated audit, reviewed sitemap dates or read-only HTTP checks.
- `scripts/seo_audit.py` ? Automated audit, reviewed sitemap dates or read-only HTTP checks.
- `scripts/seo_pages.json` ? Automated audit, reviewed sitemap dates or read-only HTTP checks.
- `sitemap.xml` ? 38 canonical indexable URLs and reviewed meaningful dates.
- `terms.html` ? Breadcrumb and social metadata only; policy preserved.
- `tests/analytics.test.cjs` ? SEO, conversion, analytics or browser regression coverage.
- `tests/browser_smoke.py` ? SEO, conversion, analytics or browser regression coverage.
- `tests/test_seo.py` ? SEO, conversion, analytics or browser regression coverage.
- `vs-cluely.html` ? Source-reviewed comparison, disclosure, verification gaps and metadata.
- `vs-final-round-ai.html` ? Source-reviewed comparison, disclosure, verification gaps and metadata.
- `vs-lockedin-ai.html` ? Source-reviewed comparison, disclosure, verification gaps and metadata.
- `vs-ophyai.html` ? Source-reviewed comparison, disclosure, verification gaps and metadata.
- `vs-parakeet-ai.html` ? Source-reviewed comparison, disclosure, verification gaps and metadata.
