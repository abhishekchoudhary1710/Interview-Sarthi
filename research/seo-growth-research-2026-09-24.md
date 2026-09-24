# InterviewSarthi: SEO research and growth plan

Research date: **24 September 2026**. This report supplements [the 15 September audit](SEO_GEO_RESEARCH_2026-09-15.md) and the approved three-product homepage. It distinguishes repository observations, current primary-source guidance, and proposed work. It is not a Search Console or analytics account audit.

## The main opportunity

InterviewSarthi already has a substantial website. Before this SEO release, its sitemap manifest contained **59 intended canonical pages**: 20 at the root, 18 under `/guides/`, 14 under `/apply/`, six under `/prep/`, and one under `/live/`. The best next step is to make those pages more trustworthy and useful, connect them to the right app, and show actual product evidence. More generic articles are a lower priority.

The three products solve distinct problems. Each deserves its own search intent and conversion path:

| Product | Visitor's problem | Concrete explanation | Current India entry offer |
| --- | --- | --- | --- |
| Apply Sarthi | Searching many job portals and repeatedly filling applications | Find jobs from multiple sources, see how they match the CV, and review application autofill | Free during early access |
| Prep Sarthi | Practising alone and not knowing which answers need work | Speak through a mock interview based on the CV and target role; review feedback and practise weak answers | 20 minutes free, then ₹99 for seven days or ₹249 for 30 days |
| Live Sarthi | Needing answer suggestions during an interview call | A Windows assistant shows suggested answers; responses start in about 1.5 seconds and the panel is hidden from supported screen capture | 30 minutes free per device, then ₹99 for two days |

These are product facts supplied by the current implementation and owner brief, not independently measured outcome claims. AI provider limits and charges remain separate. Speed varies; supported capture is not universal invisibility. Interview rules still determine whether live assistance is permitted. Job aggregation does not mean every vacancy from every portal is present.

The umbrella homepage should introduce all three and preserve brand recall from reels. A visitor landing directly on an article also needs a clear next step. For example, someone reading a TCS interview answer should find relevant spoken practice; someone reading about repetitive forms should find Apply. Recommending the appropriate app is more useful than showing the same Live download button everywhere.

## What is already in place

The repository includes a canonical sitemap manifest and generator, a static SEO auditor, tests, a source-reviewed facts page, a guide hub, product landing pages, comparison pages, real screenshots and an existing demonstration video. The recently deployed homepage explains all three products; the old Windows landing page is preserved at `/live/`. Stable URLs, product facts and receipt handling should survive further SEO edits.

The existing content inventory provides these starting points:

| Existing section | Assets already available | Highest-value improvement |
| --- | --- | --- |
| Root and Live: 21 pages together | Umbrella homepage, Windows product page, category guide, comparisons, screen-sharing explanation, setup guide, facts, support and policy pages | Separate brand, product, comparison and troubleshooting intent. Keep titles, links, prices and product identity consistent after moving Live from the root |
| General guides: 18 pages | Six employer guides, grouped HR guides, fresher guidance, career gaps, salary, self-introduction, strengths/weaknesses and Hinglish examples | Check employer-specific facts against current employer sources; link to an appropriate practice step; show worked answers instead of claiming exact interview questions |
| Apply: 14 pages | Product page, autofill explanation, safety guide, five comparisons, applying hub, ATS/Naukri/no-callback guides and a jobs-data article | Demonstrate review-before-submit and supported forms. Date snapshot counts. Remove universal claims about competitors or portal behaviour without evidence |
| Prep: six pages | Product page, price comparison and four company practice pages | Add a complete CV-and-job-description walkthrough, a clearly labelled worked feedback example, and a practical next practice session |

These counts describe the pre-release inventory, not the number of pages Google has indexed. The deeper content review sampled representative pages in each section; the release's technical audit should enumerate every final canonical URL separately.

Several useful trust assets already exist but need honest labelling. The benchmark methodology in [research/README.md](README.md) explicitly says no participant study or comparative measurements have yet been completed. It is a research protocol, not a performance result. The Apply jobs dataset is potentially distinctive first-party material, but a dated collection is not a live count of the Indian job market.

## Findings to fix before expanding content

These are observations of the starting content on 24 September, before the parallel implementation pass. They do not describe the final release status.

1. **The strongest Prep demonstration is missing from the guide journey.** Its product page shows a sample report, while its support content concentrates on company processes and prices. Add one accessible article showing a fictional CV, a fictional target role, the first answer, the follow-up, the feedback, and a stronger second attempt. Mark the example as illustrative, not a customer session or a measured improvement. Link to actual screenshots and the real app.
2. **Some comparisons make claims their evidence does not establish.** The Prep price page claimed a particular browsing location, no estimates, broad buyer preferences and a roughly fifty-fold human-versus-AI price difference. Retain only offers verified on official pages, with dates, currencies, billing periods, trial limits and unknowns. Do not compare an hourly human service with a multi-day AI pass as though they were identical units.
3. **Employer guides sometimes sound more certain than the evidence permits.** Statements about the most common failure reason, exact panel structure, pay or interview duration need a cited basis and scope. Drive, role, campus and date can differ. Distinguish a recommended practice plan from a prediction of the employer's actual process. Keep historical URLs while improving their content.
4. **Apply copy contains avoidable absolutes.** Claims such as only one collection method working, universal portal blocking, or competitors being unable to support a board should be replaced with scoped observations or removed. A product's implemented method can be described without asserting every alternative is impossible.
5. **Old guide summaries need to agree with the destination.** The guide hub still described some statistics resources in stronger terms than the source-review pages warranted. Update card summaries when an article changes; otherwise visitors and crawlers get inconsistent expectations.
6. **Search language needs a clear page owner.** The umbrella, category guide, comparison roundup and Live product page can all mention AI interview assistance, but they should not all promise the same answer to the same query. The mapping below separates their purpose. This is an intent risk assessment, not measured keyword cannibalization.

## Search language and page ownership

The phrases below are candidates grounded in product functions and current vendor terminology. They are **not verified high-volume, viral or rising keywords**. No Keyword Planner, Search Console query export or usable Google Trends series was available in this research. Prioritize them by fit to the product and actual impressions once account data is available.

| Search need / phrase family | Primary destination | What that page should answer |
| --- | --- | --- |
| InterviewSarthi; Interview Sarthi; products and plans | `/` | What the brand does, which of the three apps to choose, free allowance and starting price |
| AI job search India; jobs matched to my resume; jobs from multiple portals | `/apply/` | Sources, matching, actual interface, what is free, how a user starts |
| Autofill job applications; auto apply jobs India | `/apply/auto-apply-jobs-india.html` | Matching, autofill and autonomous submission are different; explain what Apply actually does |
| Naukri application autofill | `/apply/guides/naukri-auto-apply.html` | Supported behaviour, user review and practical limitations, with a current demonstration |
| Why am I not getting interview calls? | `/apply/guides/why-no-interview-calls.html` | Diagnose targeting and application problems; show an honest CV-to-role example |
| ATS resume format India | `/apply/guides/ats-resume-format-india.html` | A readable example and a checkable formatting checklist; no invented universal ATS pass score |
| AI mock interview; mock interview from resume; voice interview practice | `/prep/` | Spoken interview, CV/role context, follow-up questions, feedback, free allowance and setup |
| Mock interview from CV and job description; practise weak interview answers | One new Prep walkthrough, linked from `/prep/` | A complete practical example and what to do differently on the next attempt |
| AI mock interview price India; free mock interview limits | `/prep/ai-mock-interview-price-india.html` | Comparable current offers and total payable amounts; free-trial and key requirements |
| TCS / Infosys / Cognizant / Capgemini mock interview | Existing `/prep/*-mock-interview.html` pages | A specific practice session and relevant app handoff, with scoped employer references |
| Company interview questions; HR answer examples | Existing `/guides/` articles | Useful questions, worked answers and evidence; link to practice without duplicating the product page |
| Live AI interview assistant; interview copilot for Windows; real-time interview answers | `/live/` | What appears on screen, supported Windows versions, setup, demo, speed scope and passes |
| Can an interviewer see my screen? | `/can-interviewer-see-my-screen.html` | Distinguish ordinary screen sharing, capture exclusions and their limits; link to Live's actual compatibility |
| What is an AI interview assistant in India? | `/ai-interview-assistant-india.html` | Explain product categories and how to choose between practice and live assistance |
| Best AI interview assistant; alternatives and comparisons | Existing roundup and `/vs-*.html` pages | Dated selection criteria, evidence, trade-offs and ownership disclosure; no invented ranking or review score |

Do not create a new page for each spelling, tiny keyword variation, city or employer without distinct useful content. Existing guide URLs need not be renamed to introduce new wording. Redirects are appropriate for genuinely retired duplicates, after checking their query and link history.

Possible plain product copy, derived from InterviewSarthi's functions rather than copied competitor slogans:

- Apply: **Find jobs from multiple portals. Fill applications faster.**
- Prep: **Practise a spoken interview from your CV. Find and fix weak answers.**
- Live: **Get answer suggestions during your interview. Hidden from supported screen sharing.**

Use a natural category phrase in the title and introduction, then explain the actual task. Google advises descriptive, concise titles and may generate a different title link from other page signals. Repeating keywords across every heading is not a useful substitute for clarity. [Google title guidance](https://developers.google.com/search/docs/appearance/title-link)

## What current competitor pages establish

Official product pages were inspected on 24 September 2026. This establishes the wording and advertised workflows visible in this sample; it does not independently verify vendor performance, rankings, customer counts or search demand. No competitor accounts were created and no paid tests were run.

| Official source | Observed positioning | Implication for InterviewSarthi |
| --- | --- | --- |
| [Jobright job matching](https://jobright.ai/ai-job-match) | Resume-based matching, target preferences and an explanation of fit | Show why a job matches instead of presenting aggregation as the only value |
| [Simplify Copilot](https://simplify.jobs/copilot) | Application autofill, tailored resumes and application tracking | Explain review-before-submit and demonstrate one real form; a free entry offer alone is not unique |
| [Final Round AI](https://www.finalroundai.com/) | Live assistant terminology alongside role preparation, spoken practice and debriefs | Distinguish Prep's practice experience from Live's on-call answer suggestions immediately |
| [Final Round's mock guide](https://www.finalroundai.com/blog/ai-mock-interview-guide) | CV/role context and specific feedback are prominent | A real walkthrough and answer-level feedback need more visibility than general confidence promises |
| [LockedIn AI](https://www.lockedinai.com/) | Live answers, mock practice, desktop modes and a broader career toolkit | Use familiar category language, but keep supported devices and limits explicit |
| [ParakeetAI](https://www.parakeet-ai.com/) | Live call assistance and screen-sharing demonstrations | A dated test showing the receiver's screen would substantiate Live's claim more usefully than stronger adjectives |

The practical differentiators to demonstrate are the Indian job-search workflow, short rupee-denominated passes, the separate practice/live choice, and transparent supported behaviour. Low starting prices can be shown directly. Claims such as cheapest, best, most accurate, completely undetectable or guaranteed offer require evidence the research does not supply.

## Current Google and Bing guidance that changes priorities

**AI visibility uses ordinary search foundations.** Google's current guide emphasizes original, useful evidence and rejects mass pages for query variations. It says Google Search does not use `llms.txt` for visibility or rankings and requires no special AI schema. Keep the existing file accurate for other consumers, but do not treat it as a growth channel. Original walkthroughs, accurate product facts and usable pages are a stronger investment. [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)

**FAQ expansion is no longer a Google rich-result project.** Google's change log says FAQ rich results stopped appearing from 7 May 2026, and documentation was removed in June. Keep visible FAQs for genuine user questions; do not count FAQ markup as a traffic benefit or add repeated questions across dozens of pages. [Google documentation updates](https://developers.google.com/search/updates)

**AI reporting has changed since older audits.** The current Search Console Generative AI performance report covers impressions in AI Overviews and AI Mode, with page, country, date and device views. Availability depends on rollout and sufficient impressions. Absence of this report is not proof of a technical error. Do not describe it as an AI conversion or click report. [Google report documentation](https://support.google.com/webmasters/answer/16984139)

**An owner setting can affect inclusion.** Google's Search generative AI control documentation says its worldwide rollout completed on 31 August 2026. Inclusion is the default; child properties may inherit a parent choice. Check the actual property when access is available. This control is distinct from model-training controls and ordinary indexing. No account settings were changed here. [Google inclusion control](https://support.google.com/webmasters/answer/16908024)

**Bing provides another measurable channel.** Bing's AI Performance reporting documents cited pages and grounding queries; current preview additions include intent, topic and comparison views. Use actual account data if available rather than a made-up AI visibility score. [Bing AI Performance](https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c), [Bing's June 2026 additions](https://blogs.bing.com/search/2026/6/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare/)

**Submission is a notification, not a ranking guarantee.** The repository already has an IndexNow workflow. Its response should be checked, and changed URLs should be submitted responsibly. An HTTP 200 confirms receipt, not indexing. Google recrawling requests and sitemaps likewise do not guarantee index inclusion. [IndexNow documentation](https://www.indexnow.org/documentation), [Google recrawl guidance](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)

**Markup must describe real visible content.** Keep coherent organization, breadcrumb and application entities with correct URLs and offers. Do not invent stars or reviews to satisfy software rich-result requirements. Avoid marking the homepage, Apply landing page or search-result lists as individual jobs. The existing public Apply vacancy pages need actual job details, appropriate publication authority, an application path and expired-job handling before receiving `JobPosting`. [Software application documentation](https://developers.google.com/search/docs/appearance/structured-data/software-app), [JobPosting documentation](https://developers.google.com/search/docs/appearance/structured-data/job-posting)

**Video can earn its own discovery path if the page actually serves the video.** Keep the existing homepage demonstration for explanation. A dedicated watch page becomes useful when an original demonstration is its principal content, with a crawlable thumbnail, player and accurate accompanying text. A modal opened only after a click should not be assumed to qualify for video indexing. [Google video guidance](https://developers.google.com/search/docs/appearance/video)

**Authority should come from work worth citing.** Publish honest tests, useful examples and consented customer stories. Avoid purchased ranking links, automated forum promotion or fabricated endorsements. Ordinary spam rules also apply to AI search. [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies), [Bing webmaster guidelines](https://www.bing.com/webmasters/help/bing-webmaster-guidelines-30fba23a)

## Prioritized 30 / 60 / 90 day plan

This is a proposed operating plan. Completion of a future item must not be implied by the current release.

| Window | Work | Evidence of completion |
| --- | --- | --- |
| Days 1–7 | Ship the complete technical audit fixes; verify the public root and all product destinations; resolve inaccurate pricing and product statements; preserve app/receipt noindex rules and old useful URLs | Final crawl manifest, passing automated checks and representative public/browser checks |
| Days 1–14 | Establish Search Console and Bing baselines; check root, Apply, Prep, Live and representative articles with URL Inspection; verify sitemap and selected canonicals | Dated account exports and inspection findings, when owner access is available |
| Days 7–30 | Publish the Prep CV/JD walkthrough and worked feedback example; update existing guide-to-product links and summaries; improve the Apply demonstration | One distinct practical tutorial plus updated existing pages, using real UI assets and explicitly labelled fictional examples |
| Days 15–30 | Record one complete Prep demonstration and one Apply demonstration; document Live receiver-side screen-sharing tests for supported configurations | Owned recordings, transcript/captions, versions and test conditions; no invented test results |
| Days 31–60 | Improve pages earning relevant impressions but few useful visits; source-check employer guides in order of actual traffic; refresh comparisons only where the current evidence warrants it | Query/page change log, reviewed sources and conversion measurements |
| Days 31–60 | Run a small consented or synthetic benchmark using the existing protocol; publish outcomes only after data collection and review | Raw non-personal observations, method, failures, sample size and reproducible calculations |
| Days 61–90 | Expand only topics confirmed by queries, support questions or usage. Consider a focused public role/job resource if it supplies genuinely current detail and can be maintained | A documented unmet need and useful unique content, not a page-count target |
| Days 61–90 | Share useful demonstrations, tools and evidence with relevant communities or educators under their rules; disclose ownership | Authentic engagement and relevant voluntary citations; outreach requires a separate explicit send instruction |

For the reel-to-website path, use the same spoken brand and the same three functional descriptions. A Prep reel should demonstrate the weak answer, follow-up and improvement; an Apply reel should show finding and reviewing a role; a Live reel should show both sides of a supported capture test. Link each campaign to the matching product page with non-personal campaign parameters. Publishing or messaging from external accounts was not performed in this task.

Prioritize **Prep walkthrough → Apply workflow proof → Live compatibility evidence → refresh existing winners**. This is a product-fit recommendation, not a forecast that Prep will necessarily receive the most search volume.

## Measurement and decisions

Use a weekly scorecard with a 28-day trend and the previous comparable 28 days. For small volumes, look at counts and individual queries before interpreting percentages. Record the release date; hiring cycles, seasonality and other changes can also affect results.

| Question | Measurement | Decision it supports |
| --- | --- | --- |
| Can search engines reach the intended pages? | Sitemap status, URL Inspection, index coverage and selected canonical for each important template | Fix access/canonical issues before changing content for rankings |
| Are we reaching new people? | Non-brand impressions and clicks by landing page and query family, split by country/device | Prioritize relevant opportunities; don't confuse brand demand from reels with new generic-query reach |
| Does the search result explain the page? | CTR considered alongside query, position and device | Improve inaccurate or vague titles/descriptions without changing winning intent blindly |
| Does traffic choose an app? | Existing product-link clicks by product and placement, plus landing page/source | Improve handoff and explanation; a product click is not an activated user |
| Do users experience the product? | Authorized, privacy-respecting activation/completion measures separately for each app | Distinguish more visits from more successful practice or applications |
| Does acquisition sustain the business? | Real completed purchases and refunds by attributable channel where available | Use confirmed transactions rather than simulated QA events or checkout clicks |
| Are AI search experiences citing the site? | Available Google AI impressions and Bing citation/page reports | Find useful source pages; neither metric alone demonstrates revenue |

Avoid sending CV text, spoken answers, email addresses, Gemini keys, license keys or receipt query values to analytics. Cross-domain attribution for the Apply app requires deliberate validation; do not assume a marketing-site session survives every app or checkout boundary. Existing privacy protection takes precedence over adding more measurement.

Performance needs field evidence. Google's current good-experience targets are **LCP ≤2.5 seconds, INP ≤200 milliseconds and CLS ≤0.1 at the 75th percentile**, evaluated across real user visits. Lab tests can identify causes but cannot certify field performance. [Core Web Vitals guidance](https://web.dev/articles/vitals)

### Public performance check attempted

On 24 September 2026, unauthenticated, read-only requests were made to the public PageSpeed Insights v5 API for:

- `https://interviewsarthi.com/`, `strategy=mobile`, `category=performance`
- `https://interviewsarthi.com/prep/`, `strategy=mobile`, `category=performance`

Both reached the service and returned **HTTP 429 / `RESOURCE_EXHAUSTED`**, with the reason **Queries-per-day quota exceeded** and a public quota limit value of zero. No Lighthouse result or CrUX field metrics were returned. Initial restricted-environment DNS failure was resolved for the read-only attempt; it was not evidence of a website DNS problem. This report supplies no performance score and makes no claim that Core Web Vitals pass or fail. The follow-up is an available PageSpeed UI/API run or the owner's Search Console field report, alongside the implementation's resource and browser checks.

## Limits and what requires owner data

This research did not access Search Console, Bing Webmaster Tools, analytics reports, a backlink index or a keyword-volume account. It did not inspect private user recordings, conduct a hiring study or verify every employer's current hiring drive. Public search samples and vendor pages are discovery evidence, not a controlled Google ranking study. A sparse or empty `site:` result is not proof of deindexing.

The owner-side next evidence is a Search Console performance export with query/page/device/country data, indexing and sitemap status, plus the corresponding Bing reports and aggregated product conversions. Credentials should not be pasted into this report. Until then, prioritization relies on site structure, verified product functions, visible content and current official guidance.

Success means more relevant discovery and more useful product use over time. Technical SEO makes that possible; original evidence and sustained product quality give people a reason to choose and recommend the site. Neither this release nor any keyword phrase guarantees a number-one ranking or a fixed traffic increase.

## Release status

This document records research and pre-fix findings. See [the completed audit and growth plan](../SEO_AUDIT_AND_GROWTH_PLAN.md) for implemented fixes, validation and release evidence. The new Prep walkthrough and pricing rewrite are part of that release; the remaining 30/60/90-day items are proposed work.
