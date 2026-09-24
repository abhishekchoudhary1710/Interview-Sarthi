# Content audit and corrections — 24 September 2026

## Scope and limits

Reviewed About, all 18 pages in `guides/` (hub plus 17 articles), and the four company practice pages in `prep/`: TCS NQT, Infosys, Cognizant GenC and Capgemini. Baseline counts use the repository's pre-edit HEAD. This report describes working-tree changes; production checks are part of the overall SEO release.

This is a content audit, not a traffic report. No Search Console clicks, impressions, query positions, conversions or keyword-volume exports were available to this workstream. Proposed topics are hypotheses, not measured search demand or claimed viral trends.

## Baseline findings

| Finding | Evidence | Visitor impact |
| --- | --- | --- |
| Brand described as one Windows app | About said “one developer, one app” and made umbrella-wide no-server/no-account claims | Contradicted the three-product homepage and actual account/payment flows |
| Guides had no external citations | 0 of 18 pages linked an external source | Readers could not verify employer process, pay, dates or service terms |
| Preparation readers sent to Live first | 17 primary guide promos linked `/live/` and showed its overlay illustration | Practice users had to find a secondary Prep link |
| Employer facts stated as universal | Six company guides gave exact salary, timing, agreement or process claims without sources | These depend on role, route, batch and offer |
| Internal contradiction | Infosys guide claimed one combined round; its Prep page asserted separate rounds with exact timings | Conflicting instructions on the same site |
| Weak company-page attribution | Third-party site names without precise linked evidence | “Reviewed” did not establish support for each figure |
| Hub summaries overpromised | Salary/hiring statistics, invented US price ranges and “what they actually ask” phrasing | Link text did not match corrected destination content |
| Unsupported FAQ markup | Guide JSON-LD contained Q&A not presented as a visible FAQ | Structured data did not accurately describe visible content |
| Rhetoric presented as data | Salary guide claimed a sentence costs a lakh, budget bands differ by 30–50%, and unspecified counter-offer statistics | Examples could be mistaken for financial evidence |

## Implemented corrections

- About explains Apply, Prep and Live separately: purpose, platform, entry trial/price and different account/data needs. Founder/contact identity and `about.html#founder` are preserved.
- All 17 existing guide promos lead to Prep's voice mock interview and 20-minute trial. They use the real `assets/prep-app-current.png` with its actual 1360 × 960 dimensions, explain the Gemini-key requirement and provider limits, and retain relevant Apply/Live secondary paths.
- Six company guides identify their questions as independent practice examples. Primary employer links and bounded process summaries replace unsupported salary tables, universal durations, service-agreement amounts, hiring seasons and language-policy assertions. Useful project/technical/scenario practice remains.
- Two multi-company HR guides retain practical answer topics and examples with official hiring sources, removing invented scoring/rejection-rate claims.
- Eight employer guides now cite primary sources. Four Prep company pages also cite the matching employer, distinguish independent practice from the actual hiring process, and avoid promising questions, selection, fixed round counts or salary.
- The guides hub accurately describes its destinations and directly links the four company mock pages and new resume-based mock tutorial. Matching company guides link to their company practice page, with return links from Prep.
- Hidden FAQ objects were removed from guides. The four Prep FAQ objects now exactly describe their visible revised questions and answers. No rich-result promise is made.
- Removed unsupported monetary/statistical claims from salary advice; marked worked scripts as examples. Corrected selected first-interview, health-gap and Hinglish assertions that implied universal outcomes or invented frequencies.
- Owned navigation/footer copy routes main-brand links home, general plans to the umbrella comparison, and permitted real-time help specifically to Live at `/live/`.

“Official source checked 24 September 2026” records the actual check, not proof that every employer process is fixed on that date. Publication history is retained; the overall workstream synchronizes real modification dates and sitemap records separately.

## Primary employer sources

- [TCS All India NQT hiring](https://www.tcs.com/careers/india/tcs-all-india-nqt-hiring): advertised batch scope, test sections and test-related hiring categories. Registration for the advertised drive was closed when checked. Does not prove one interview duration or old agreement terms.
- [Infosys HackWithInfy](https://www.infosys.com/careers/hackwithinfy.html): a competition that can lead to interview opportunities, not a universal graduate hiring format.
- [Infosys Global Education Center](https://www.infosys.com/careers/graduates/global-education-center.html): supports the Mysuru Foundation Program; individual arrangements depend on the offer.
- [Wipro early careers](https://careers.wipro.com/content/Early-Careers/): identifies Elite and Turbo, without a universal salary/test/agreement table.
- [Accenture recruitment FAQs](https://www.accenture.com/in-en/careers/explore-careers/area-of-interest/journey-to-accenture): role-related assessments alongside interviews; invitation instructions govern.
- [Cognizant GenC](https://careers.cognizant.com/india-en/pathways-to-cognizant/genc-program/): explicitly allows process variation by role; current page states no service bonds.
- [Capgemini India recruitment](https://www.capgemini.com/in-en/careers/join-capgemini/recruitment-process/): variable assessment/interview steps; does not prove universal games, Python restrictions or exact interview timing.

## Why this supports a better search experience

[Google's people-first guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) emphasizes useful original information, accurate authorship, clear sourcing and descriptive titles. It warns against chasing trends without audience value and changing dates to imply unsupported freshness. Here, real product demonstrations and useful preparation are stronger material than unverified process claims across more company pages.

[Google's structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) require markup to represent actual page content. Removing unsupported/invisible FAQ claims addresses accuracy, not a promised ranking boost. The old FAQ documentation URL redirected to Search updates when checked; this work makes no FAQ rich-result eligibility assumption.

## What to do next

1. **Measure first.** Export Search Console page/query data for 28 and 90 days. Separate brand terms from non-branded traffic; pair impressions, clicks, CTR and position with guide → product → trial conversions. There is no reliable way to choose the best new keyword from this repo alone.
2. **Add first-hand proof.** Publish a consented, anonymized CV → weak answer → report → revised answer walkthrough. Explain AI-score limits. Do not imply measured improvement until measured.
3. **Document product claims.** For Live, record device/OS, meeting app, capture mode, network and time-to-first-response method. For Apply, show an actual supported job-to-form workflow, including what the user still reviews.
4. **Improve existing topics before multiplying pages.** Resume-based mock interviews, company practice, job-source aggregation and Windows live assistance all match actual features. These are intent hypotheses, not search-volume estimates. Avoid separate pages for trivial wording variants.
5. **Add a real reviewer.** A named qualified reviewer can improve preparation advice after actually reviewing it. Do not invent credentials or imply product-authored comparisons are independent.
6. **Maintain hiring sources.** Recheck when announcements change. Keep dates/terms tied to the exact batch. Remove expired application instructions rather than merely changing the year.
7. **Differentiate guide and product intent.** Guides should answer how to prepare; mock pages should show the actual practice workflow. Use Search Console later to decide whether overlapping pages need consolidation.
8. **Earn references with useful work.** Share transparent demonstrations or original research through authorized outreach. No external messages, purchased links, invented testimonials or mass-produced pages were created by this workstream.

## Validation

Parsed all 23 owned pages' JSON-LD and checked one H1 per page. Baseline: 18 guide pages, 0 with external source links, 17 Live-first promos. After: 8 employer guides with primary citations, all 17 promos lead to Prep. Corrected two duplicate HR descriptions detected by the strengthened audit. Latest whole-site audit after scoped fixes: 66 pages, 60 indexable; only the parent's in-progress resume tutorial sitemap entry remained outstanding. Final whole-site tests and production verification are performed by the main workstream.
