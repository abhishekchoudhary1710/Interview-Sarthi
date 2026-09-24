# Apply Sarthi public website: SEO audit

Audited **24 September 2026**, before the corrective implementation in this session. Scope: public HTTP responses and source-code review of `../Job-Hunt/jobhunt/public.py`, public routes in `web.py`, and relevant status/collection helpers. No runtime database, secret configuration, CV, account, application or paid AI request was accessed. No backend was edited or deployed by this research subtask.

This adds an important scope correction to [the main growth report](seo-growth-research-2026-09-24.md): **Apply already has a large public job website. It is not only a sign-in application.** The main site's 59-page starting inventory describes the marketing host, not the entire InterviewSarthi web presence. Old documents describing the app as a single indexable URL are outdated.

The findings below were handed to the implementation agent. They are a dated baseline, not a claim that they remain unfixed after the release. Refer to the final release validation for implemented corrections.

## Public inventory, measured from actual responses

The robots file, sitemap index, its four child files, the jobs directory, privacy page, two job pages and two hubs were readable without signing in. The requests used an audit user agent classified as a bot by the source's aggregate page counter. No application buttons, tracked `/go/` links or authenticated APIs were called.

| Public resource | Result at audit time |
| --- | --- |
| [robots.txt](https://apply.interviewsarthi.com/robots.txt) | HTTP 200; permits public pages; disallows `/api/`, `/healthz`, `/extension.zip` and `/go/`; names the app's sitemap |
| [Sitemap index](https://apply.interviewsarthi.com/sitemap.xml) | HTTP 200; four child sitemaps |
| [Static pages sitemap](https://apply.interviewsarthi.com/sitemaps/pages.xml) | Three URLs: root, `/jobs`, `/privacy` |
| [Hubs sitemap](https://apply.interviewsarthi.com/sitemaps/hubs.xml) | 1,472 distinct URLs: 857 company hubs and 615 role hubs |
| [Jobs sitemap 1](https://apply.interviewsarthi.com/sitemaps/jobs-1.xml) | 20,000 distinct URLs |
| [Jobs sitemap 2](https://apply.interviewsarthi.com/sitemaps/jobs-2.xml) | 8,754 distinct URLs |
| [Jobs directory](https://apply.interviewsarthi.com/jobs) | HTTP 200; indexable; self-canonical; displayed 29,040 roles and 291 pages |
| [Second directory page](https://apply.interviewsarthi.com/jobs?page=2) | HTTP 200; `noindex, follow`; canonical includes `?page=2`; ordinary next/previous HTML links |
| [Privacy](https://apply.interviewsarthi.com/privacy) | HTTP 200; self-canonical; no noindex directive; describes CV processing and account data |

Total measured sitemap inventory: **30,229 distinct public URLs**, including **28,754 job URLs**. These are submitted URLs, not Google-indexed pages or verified still-open positions. The collection changes continuously; these counts should not become evergreen marketing claims.

The directory count exceeds sitemap job URLs by 286 in this snapshot. Source review found a structural reason counts can differ: `count_public` counts source/status rows, while page generation subsequently excludes identifiers that cannot safely round-trip in a public path. Concurrent collection may also affect independently fetched counts; no database reconciliation was performed. Counts, lists and sitemap eligibility should share a common definition.

## Strengths worth preserving

- Job pages return actual HTML descriptions, metadata and links without requiring JavaScript or an account.
- The two sampled job pages have self-canonicals, one main heading, `JobPosting` and breadcrumb JSON-LD, visible source attribution and outbound application links.
- Incorrect decorative job slugs redirect to the intended slug with HTTP 301 in the route implementation.
- Closed jobs return HTTP 410 with noindex in the route implementation. Unknown or disallowed jobs return 404. Closed rows are omitted from public sitemaps.
- Source collection only closes missing jobs after a successful complete collection where applicable, and a separate expiry routine exists. This is safer than marking jobs closed when a partial fetch fails.
- Public descriptions pass through an HTML allowlist before rendering.
- Public company and role hubs create links into the job catalogue. Their minimum-count thresholds reduce empty pages, although a count threshold alone does not establish useful content.
- CV, matching, tailoring and tracker operations require a signed-in user. Robots exclusions are supplemental discovery controls, not access control.

The 410, slug and account behaviours above were reviewed in code; they were not verified using a real closed job, account or private document in this audit.

## Verified live problems

| Priority | Finding and direct evidence | Why it matters / required correction |
| --- | --- | --- |
| P1 | [Customer Success Manager Mexico at JumpCloud](https://apply.interviewsarthi.com/jobs/remoteok/customer-success-manager-mexico-jumpcloud/1137406) visibly says Mexico City, Mexico and Remote, but its JSON-LD declares `addressCountry: IN` and eligible applicant country India | The structured geography contradicts the visible location and invents eligibility. Derive actual countries from reliable source data; omit unsupported properties or withhold job-rich-result markup when required facts cannot be established |
| P1 | [AI jobs hub](https://apply.interviewsarthi.com/roles/ai) claimed 2,684 AI roles while its first result was Buyer – Central Sourcing, Global Tail Sourcing | The route uses a substring search for `ai`, which also matches words such as tail and chain. Use a consistent role classifier or word-aware match and verify examples before claiming a specialized collection |
| P1 | `/jobs?page=999999` returned HTTP 200 with an empty directory, a page-999999 title and a previous link to page 999998 | Arbitrary out-of-range pages form a crawl trap. Return 404 for unavailable pages; keep real pagination reachable. Noindex does not remove the cost of fetching unlimited empty URLs |
| P1 | All entries in the static and hub sitemaps reported 24 September; source functions generate today's date on every request. Job sitemap dates come from `last_seen` | Request time and collection sightings do not establish substantive page updates. Track content changes or omit lastmod where there is no defensible value |
| P1 | Directory and hub Live promotions said invisible screen sharing and answers under 1.5 seconds, and the sampled company/role hub CTAs linked to the umbrella root | This no longer matches the scoped Live claim or its `/live/` destination. Update product names, response-time scope, supported capture language and actual Live links while retaining the brand link to `/` |
| P2 | The Mexico job's button says it opens JumpCloud's site, but its destination is RemoteOK | Label the actual destination and use an employer link where reliably available. Do not call every external board the employer's own site |
| P2 | The sampled Mexico description contains encoding artifacts around the registered-trademark symbol | Normalize character encoding at ingestion without silently changing the employer's meaning; poor imported text weakens readability |

The India sample, [Amazon Cross Border Tech](https://apply.interviewsarthi.com/jobs/amazon/software-development-engineer-ii-amazon-cross-border-tech-adci-karnataka/10370961), returned HTTP 200 with visible Bengaluru and structured country IN. Its metadata contained the employer date 19 March 2026. An old date is not by itself proof of a closed job. The employer application destination was inspected as a link, not followed or submitted.

## Source-confirmed hazards needing fixtures and regression checks

These behaviours exist in the starting source. The two public job samples do not establish how often they occur in the live corpus.

1. **Salary type, currency and period are assumed.** `job_posting_ld` inserts raw `salary_text` into a quantitative `value` and always sets INR/YEAR. A salary range, monthly amount or foreign currency would be misrepresented. Only emit normalized, employer-supplied salary facts when their units are known; keep uncertain text visible without inventing numeric markup.
2. **First discovery can be substituted for the employer's publication date.** Missing `posted_at` falls back to `first_seen`. Keep source publication and crawler discovery separate. Missing original dates should not be repaired with fabricated freshness.
3. **Job-rich-result eligibility is too permissive.** The public predicate checks status, source and addressable identifier, but not description completeness, employer identity, geography or application destination. Missing descriptions can become the title in markup; missing organizations become a dash. Useful public fallback pages may be retained while withholding unsupported `JobPosting` data.
4. **Geographic scope is not enforced consistently.** Public selection does not filter on the stored India eligibility field, while directory and role titles claim India. Either make collections match their stated scope or name them accurately. Unknown eligibility must not be converted to India eligibility.
5. **Role URLs accept arbitrary matching substrings.** Besides the observed AI false positives, the route can construct additional indexable collections for terms not in the sitemap. Restrict indexable hubs to maintained useful categories with stable matching; return an appropriate response for unsupported terms.
6. **Expired status depends on collection and cache behaviour.** The correct 410 route acts on stored status. Public responses permit 30-minute caching and up to 24 hours of stale revalidation. Verify expiry runs and cache invalidation together with synthetic fixtures; do not claim the live site removes every expired listing instantly.
7. **Public API source exclusions need an ownership regression test.** The list serializer excludes extension-origin records, but the detail serializer does not visibly apply the same source restriction. No private record was requested, and this audit does not assert an observed data leak. Confirm that a public detail request cannot expose a user's extension-only record using an isolated fixture before broadening crawl access.

Google's job documentation requires genuine publication dates, complete descriptions and accurate employer/location facts; salary markup must represent the employer's actual amount and units. Expired listings and inaccurate markup need explicit handling. These conditions are eligibility requirements, not a guarantee of inclusion. [Google JobPosting guidance](https://developers.google.com/search/docs/appearance/structured-data/job-posting)

Google uses sitemap lastmod when it accurately reflects meaningful changes and ignores changefreq. A continuously changing catalogue should track changes rather than repeatedly stamping all pages with today's date. [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

## Pagination, canonical and discovery recommendations

Keep each real pagination URL self-canonical. Do not canonicalize every later page to page one when it contains different jobs. The existing noindex policy for later list pages is a deliberate indexing choice, but it should not be the sole discovery strategy for tens of thousands of jobs. Preserve ordinary crawlable links, accurate sitemaps and useful company/role hubs.

The main `/apply/` page explains the product, while `apply.interviewsarthi.com/jobs` serves current vacancy browsing. They are different resources and should not canonicalize to one another. Give each an appropriate title and link between them with useful wording such as browsing current jobs or understanding CV matching.

The app-root title and description still start with signing in, although public browsing is available. Update that expectation when making backend metadata changes. Public listing pages should have one useful job purpose rather than becoming repeated sales pages with little vacancy content. Keep related roles relevant and use Prep links where they help the applicant prepare for that specific job.

The public-source allowlist documents why some feeds and employer boards are included and certain aggregators are excluded. That rationale is not itself proof of republication permission. Maintain the source permissions and removal process alongside operational records before expanding coverage. This audit did not review source agreements.

## Product facts and privacy wording

The public privacy page and `web.py` distinguish two AI-key paths:

- Browsing jobs requires no Gemini key.
- CV reading uses the user's key when supplied; otherwise a platform key can support that initial processing within usage limits.
- Tailoring a CV to a particular job requires the user's own key.
- CV matching after profile creation uses the stored profile/vector matching; it is not a new paid AI call for every visible result.

Do not describe every Apply AI action as always using the user's own key. A concise product note can say **“Browse jobs without a Gemini key. CV tailoring needs your own key.”** The more detailed processing explanation belongs in the linked privacy/setup pages.

The privacy page says CV files and extracted profiles are stored on the server for the account, unlike a browser-only claim. Shared umbrella copy must keep those product differences explicit. Statements about Google's handling of API content should be maintained against the applicable provider terms separately; this audit did not submit any CV or verify a particular account's billing tier.

Aggregate public page views are recorded by day, path, referring host and bot flag in source; no tracking cookie is introduced by that counter. Tracked product links use a separate event route. This audit avoided invoking those conversion links. No claim is made about real traffic totals because the operational analytics database was not read.

## Implementation and release gates

The public backend is a distinct deployment from the static marketing repository. Updating the GitHub Pages homepage alone cannot fix these routes. The implementation agent owns the corrective source changes; the release record must state whether the backend was actually deployed.

Before marking the Apply public work complete:

1. Use synthetic data to test Indian and foreign jobs, remote geography, unknown employer/date, salary formats, closed/expired statuses, private extension records and pagination bounds.
2. Confirm that list counts, hub eligibility and sitemap entries use the same public predicate, and that arbitrary role fragments do not create misleading indexable hubs.
3. Verify job markup matches visible details, public redirects retain canonical URLs, and invalid detail pages cannot return job-rich-result JSON-LD.
4. Recheck a small public sample after deployment, including the audited Mexico page and AI hub where still available. Report corrections without implying every one of the roughly 30,000 URLs was individually crawled.
5. Use owner Search Console and Bing reports for this subdomain, or a domain property covering it, to inspect actual indexing and job enhancements. Submit the app's own sitemap through available authorized workflows. Existing sitemap presence is not evidence that it has been submitted in an account.

Correcting the existing catalogue's geography, relevance and freshness is a higher priority than creating additional location or role pages. Its public inventory creates a substantial opportunity, but the size alone does not demonstrate search traffic or authority.
