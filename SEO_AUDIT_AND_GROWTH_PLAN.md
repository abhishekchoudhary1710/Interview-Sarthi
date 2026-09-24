# InterviewSarthi: full SEO audit and growth plan

Reviewed **24 September 2026**. This is the release report for the three-product website and Apply Sarthi's public job pages. It separates completed website work, observed public facts and the next work needed to grow traffic. Search Console, Bing Webmaster Tools and GA account reports were not accessed.

## Main finding

InterviewSarthi already has a useful content base and three products that answer different needs. The biggest opportunity is to make those differences clear, connect each useful article to the right app, and publish evidence of the actual experience. Increasing the number of generic articles is a lower priority.

The approved homepage stays the umbrella: **find jobs, practise interviews, get live answer suggestions**. Product pages explain the details and show the real interface. Each product needs its own search audience and measurable next step.

| Product | User problem and clear promise | Entry offer | Best next action |
| --- | --- | --- | --- |
| Apply Sarthi | Stop switching between job portals. Find jobs from multiple sources, match your CV and fill applications faster | Free during early access | Browse jobs; create an account for CV matching and application tools |
| Prep Sarthi | Stop practising alone without feedback. Take a spoken mock interview from your CV and target job, then work on weak answers | 20 minutes free; ₹99 for seven days; ₹249 for 30 days | Start a relevant mock interview |
| Live Sarthi | Get suggested answers on your Windows screen during a permitted interview call | 30 minutes free per device; ₹99 for two days | Watch the existing demo and install the Windows app |

Live's roughly 1.5-second response start is a product claim with variable real-world timing. Its panel is hidden from supported Windows capture; that does not establish invisibility to every recorder, camera or monitoring system. Prep and Live require a Gemini key, with separate provider limits and possible charges. Apply browsing does not need a key; initial CV reading can use platform capacity, while tailoring uses the user's key. No tool or page can guarantee an offer.

## What exists today

The marketing website started this release with **59 intended indexable pages**. It now has **60**, after adding one practical Prep walkthrough. The final automated inventory examines 66 content pages, keeping application, receipt and error surfaces out of the indexable marketing set. Seven legacy `/mock/` redirects preserve useful old paths.

| Section | Final canonical marketing pages | Existing value |
| --- | ---: | --- |
| Root pages | 20 | Brand homepage, about, product-category guidance, comparisons, support, research and policies |
| Interview guides | 18 | Employer questions, fresher guidance, HR examples, salary, career gaps and Hinglish answers |
| Apply marketing | 14 | Product explanation, autofill guidance, five comparisons, ATS/Naukri/no-callback guidance and a dated jobs-data article |
| Prep marketing | 7 | Product, prices, four company practice pages and the new CV/job-description walkthrough |
| Live | 1 | Original Windows product website, real demo, features, installation and pass selection |

Apply's public app is a **separate search surface**. The public sitemap snapshot taken before this release contained **30,229 URLs: 28,754 job pages, 857 company hubs, 615 role hubs and three static pages**. These are advertised sitemap entries, not verified Google-indexed pages or traffic figures. Counts change as jobs open and close. The app directory originally reported a different total because its count included IDs excluded from published URLs; the implementation now applies the same publication filter before counting and paginating.

All 60 marketing pages received automated technical checks and desktop/mobile rendering checks. Content review covered the guide set, product pages and selected comparisons in depth. The much larger Apply catalogue was assessed through source code, synthetic regressions, public sitemaps and a small sample of live pages; it was not individually reviewed vacancy by vacancy.

Evidence and detailed inventories:

- [Baseline marketing audit](research/seo-baseline-2026-09-24.json)
- [Final marketing audit](research/seo-final-2026-09-24.json)
- [Page-by-page search-intent map](research/seo-page-map-2026-09-24.csv)
- [Content review](research/seo-content-audit-2026-09-24.md)
- [Public Apply audit, before fixes](research/seo-apply-public-audit-2026-09-24.md)
- [Current research and primary sources](research/seo-growth-research-2026-09-24.md)

## Completed changes in this release

### Clearer product identity and page metadata

The main product titles and descriptions now explain actual tasks: jobs from multiple sources and autofill, mock interviews from a CV and job description, and the Windows live assistant. Search and social metadata identify the correct app. Home and Prep now have distinct sharing images made from the existing logo and real interface screenshots. Apply's app uses its existing Apply image instead of the Live overlay image.

Organization, website and software identities are consistent across the umbrella and app pages. Application destinations are distinct from marketing URLs. Article images and breadcrumbs are checked. All indexable marketing pages allow large image previews. This improves the information available to search engines; it does not guarantee a rich result, a particular displayed title or Discover inclusion.

### Better content and the right next step

The interview guides now primarily lead to Prep practice, with Apply and Live offered where relevant. Employer-specific guidance links to official sources and distinguishes practice suggestions from a guaranteed hiring process. Unsupported exact salaries, interview durations and absolute claims were removed in the reviewed guides.

The new [mock interview from your CV and job description walkthrough](https://interviewsarthi.com/prep/mock-interview-from-resume.html) shows the actual setup and feedback screens. Its teaching example is labelled fictional. It explains manually bringing a job description from Apply into Prep; it does not imply an automatic shared account or CV transfer.

The [Prep price comparison](https://interviewsarthi.com/prep/ai-mock-interview-price-india.html) was rewritten around verified offers from official pricing pages, with currencies, billing periods and trial limits. Unsupported broad tool counts and human-versus-AI savings ratios were removed. The three-app homepage still makes short rupee passes and free allowances visible without claiming universal cheapest or best status.

About, privacy, selected FAQs and Live capture explanations now distinguish the products and their data handling. Apply's account stores CVs on its server; this must not be confused with Live's processing or Prep's browser experience. Existing media and product destinations were retained.

### Technical maintenance and tracking

The sitemap includes the new tutorial and actual meaningful content-update dates. The expanded auditor checks redirects, canonicals, crawl permissions, sitemap agreement, schema, metadata, media references and image-related recommendations. Generated Apply articles now have valid paragraph structure and consistent product handoffs. A stale `/mock/` link was corrected.

Sitewide `product_click` events identify **apply**, **prep** or **live**, the link placement and whether the destination is a product page or application. Raw destination queries are not added to these events. Receipt and private Prep-app exclusions remain. Browser tests block real analytics requests. These events measure interest in a product; activation, a completed practice session and purchase are separate outcomes and require their own reporting.

The existing IndexNow workflow now treats an HTTP failure as a failed submission instead of silently succeeding. A successful notification means receipt, not guaranteed crawl, indexing or ranking. No Search Console account submission or account setting was performed in this release.

### Apply public-page corrections

This was the most significant technical finding. A sampled Mexico/remote vacancy was marked as India in JobPosting, and the AI role hub matched words such as “tail” and “chain.” A very large invalid page number returned an empty HTTP 200 page. Sitemaps also assigned fresh dates without a content edit.

The backend now:

- Matches role words rather than arbitrary substrings, including correct escaping for programming-language role URLs.
- Uses the same publishable-source, open-status and valid-ID conditions for directory counts, lists and sitemaps.
- Returns 404 for negative or out-of-range listing pages, while allowing the legitimate first page of an empty directory.
- Requires actual source facts before emitting JobPosting: employer, title, description, original date, application destination and explicit physical country.
- Omits guessed India eligibility, guessed INR/year salary fields and collection-date substitutes for employer publication dates.
- Omits unsupported JobPosting for remote listings until authoritative applicant geography is available. Readable job pages remain available.
- Removes misleading sitemap `lastmod` values based on request time or collector visits.
- Sends Live product links to `/live/`, uses accurate screen-sharing and timing scope, and labels external job links “View job and apply.”
- Returns 404 when an anonymous caller requests extension-captured job text through the detail API, matching the public-list exclusion.

The app root also explains public browsing in metadata and links to the readable job directory before JavaScript loads. No signed-in application workflow, collector, payment integration or database schema was redesigned by this release.

## What current research tells us

The most useful category phrases are **AI mock interview**, **mock interview from resume**, **job application autofill**, **jobs matched to your CV**, **live AI interview assistant** and **interview copilot**. Official competitor pages use these task-based categories. Their appearance on vendor websites does not establish search volume or a viral trend. No credible keyword-volume dataset or Trends series was obtained here.

Our proposed page ownership is:

| Search intent | Main destination | Content that earns the visit |
| --- | --- | --- |
| InterviewSarthi / Interview Sarthi | `/` | All three products, trial allowances and clear selection |
| Jobs from multiple portals / CV job matching | `/apply/` and public app, with separate marketing/browsing purposes | Current jobs, matching example, supported application workflow |
| Job application autofill / Naukri forms | Existing Apply guides | An actual form walkthrough and review-before-submit limits |
| AI mock interview / voice interview practice | `/prep/` | Actual interview setup, follow-ups, feedback and entry price |
| Mock interview from resume and job description | New Prep walkthrough | A complete setup-to-feedback example |
| Employer interview questions | Existing employer guides | Useful answers, employer references and relevant practice |
| AI mock interview prices India | Existing Prep price URL | Dated, comparable offers with limits |
| Live AI interview assistant for Windows | `/live/` | Real demonstration, compatibility, setup and pass options |
| Screen sharing and interview assistance | Existing capture explanation | Supported behaviour and receiver-side testing evidence |

Google's current guidance recommends useful original evidence and normal search fundamentals for its AI features. It does not require special AI markup, and says `llms.txt` has no effect on Google visibility or ranking. FAQ rich results stopped appearing in May 2026, so adding FAQ schema is not a growth strategy. Visible questions can still help a buyer. [Google AI guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), [documentation updates](https://developers.google.com/search/updates).

Job schema must represent real vacancy details. Search markup is not a place to infer a remote worker's eligible country from our target audience. Original posting dates and expiry handling matter. [Google JobPosting requirements](https://developers.google.com/search/docs/appearance/structured-data/job-posting).

## Priorities for the next 90 days

### First 14 days: establish a trustworthy baseline

Check the actual Search Console Domain property and Bing property. Export the last 90 days of queries and pages, split branded and nonbranded searches, and inspect the homepage, each product, the new tutorial and representative public jobs. Record submitted sitemaps, selected canonicals and job enhancement issues. Historic repository notes say a Domain property existed; account state was not independently verified here.

Create GA reporting for product clicks by landing page and product. Establish separate, verified activation events before calling these clicks conversions into active users. Apply's own aggregate public-page counters and product-link tracking are separate from marketing GA; do not add unlike metrics together as unique people.

Audit Apply's source fields and expiry handling. Preserve structured country, remote eligibility, original posting date, salary amount/currency/period and true content-change dates when the source supplies them. Restore JobPosting only for records that meet its requirements. Review thin hubs and republished descriptions using actual index coverage and user value rather than assuming 30,000 URLs are an advantage.

### Days 15–30: demonstrate the product

Record one complete Apply workflow and one Prep session using real app screens. For Live, document what the screen-sharing recipient sees under named Windows and meeting-app versions. Date the demonstrations and include limitations. Use an existing video prominently where it answers the visitor's question. A dedicated watch page is appropriate when the video is the page's principal content, with a crawlable thumbnail and accurate transcript. [Google video guidance](https://developers.google.com/search/docs/appearance/video).

Improve the existing pages with impressions and positions near the first page before creating new articles. Make the first paragraph answer the searcher's actual question and link to the relevant app. Refresh high-value competitor prices against official sources, rather than automatically changing a year in a heading.

### Days 31–60: publish evidence people can cite

Publish consented customer examples that show the before answer, feedback and revised answer. Avoid fabricated offer counts or testimonials. Run the existing benchmark protocol before describing accuracy or latency as measured. Turn a properly scoped, dated Apply dataset into a useful hiring-trends report only after checking sample coverage, duplicates and missing fields.

Seek relevant mentions through useful demonstrations, university placement communities and career educators. Any outreach needs an actual owner decision and appropriate consent; none was sent here. Do not buy ranking links or mass-post AI articles.

### Days 61–90: scale what produces useful visits

Use query/page data to select a small number of distinct new pages. Expand a company or role guide only when it can offer specific exercises or evidence. Merge genuinely redundant articles carefully after checking backlinks and query history. Review activation and paid outcomes by product, including assistive journeys from Apply to Prep, so an increase in broad traffic does not hide poor fit.

## Measurement and limits

Track nonbranded impressions, organic clicks, click-through rate, indexed canonical pages, job enhancement validity, product-click rate and independently verified activations. Compare like-for-like 28-day periods and annotate releases. Employer recruitment seasons and job inventory changes can affect results.

Core Web Vitals need real field data. The public PageSpeed API returned quota errors during this audit, so this report does not claim a Lighthouse score or passing field metrics. Mobile/desktop layout checks passed; that is a different test. The usual good field thresholds are LCP at or below 2.5 seconds, INP at or below 200 milliseconds and CLS at or below 0.1 at the 75th percentile. [Core Web Vitals definitions](https://web.dev/articles/vitals).

We do not yet know which queries already rank, how much organic traffic each app receives, where real users leave, or the conversion rate from search to paid use. Those require owner account data. The next prioritization should use that evidence. Neither this release nor a keyword choice guarantees a top position or a future traffic amount.

## Validation and release record

Pre-release validation: 60 indexable marketing pages; 66 content pages examined; zero static audit errors or warnings. All 60 marketing pages rendered at 390px and 1366px widths, giving 120 checks without overflow, broken images, local missing resources or JavaScript errors. Generated pages and sitemap match their source. Python SEO and Node analytics/routing/Prep-engine tests pass.

Apply validation uses synthetic temporary data for public pages, accounts, source adapters and browser-script boot logic. All 153 tests passed before restarting the web service. Production verification and release identifiers follow below. No real purchases or job applications are submitted by release QA.

See [owner actions](OWNER_ACTIONS_SEO_GEO.md) and [query tracking](TRACKING_QUERIES.md) for the ongoing routine.

### Production release, 24 September 2026

- Marketing implementation: [`9e2be1d`](https://github.com/abhishekchoudhary1710/Interview-Sarthi/commit/9e2be1dc1a951e9c4754df8ac1eb77e8aadfb8a1). GitHub Pages build, SEO checks and IndexNow workflow completed successfully. The production host serves this release; subsequent documentation commits record evidence without changing these pages.
- Apply implementation: `194de09`, descriptive metadata in `731f757`, and the rendered-title/heading correction in `64dea2d`, pushed to its existing main branch. Restarted only `jobhunt-web.service`; service reports active/running and its public health endpoint returns 200.
- [Public marketing verification](research/seo-public-verification-2026-09-24.json): all 60 URLs return 200 and exactly match local HTML; canonicals, indexing directives, one H1, titles, descriptions and JSON-LD pass. Live sitemap contains exactly the 60 expected URLs; robots points to it.
- [Public Apply verification](research/seo-apply-release-verification-2026-09-24.json): health, app, directory, AI hub, two sampled jobs and sitemaps return expected responses. Invalid pagination and anonymous extension-detail requests return 404. The sampled Mexico remote role has no invented India JobPosting. No per-record source facts were fabricated to restore omitted markup. Catalogue counts are live and can change between requests.
- [Production browser verification](research/seo-browser-verification-2026-09-24.json): homepage checked at eight widths from 320 to 1440 pixels; product links, mobile navigation, media tabs, screenshots, zoom, the existing video, prices and FAQs work. Legacy Live anchors and both mocked receipt-return formats work. Core product copy and prices remain available with JavaScript disabled. No JavaScript or same-host HTTP errors were observed.
- [Product-event checks](research/seo-product-events-verification-2026-09-24.json) confirm exactly one event per homepage app choice and successful signed-out Apply rendering with its descriptive title and one main heading.
- Validation totals: 16 Python marketing tests, four Node test files and 153 Apply tests pass. The final title change also passed 38 targeted app/account checks. Separately, 120 local page/viewport checks pass. Analytics and payment providers were intercepted during browser QA; no real purchase or job application was performed.

This confirms deployment and the checked functionality. Search ranking, index inclusion, field Core Web Vitals and revenue impact still require subsequent search/account observations.
