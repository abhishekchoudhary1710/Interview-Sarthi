# Interview Sarthi: research and implementation evidence

Reviewed 15 September 2026. Baseline repository `e942363`; 39 HTML pages, 37 indexable. This is a public-source and repository audit, not a Search Console, paid backlink or field-performance audit.

## Findings that changed the implementation

| Finding | Evidence | Action |
| --- | --- | --- |
| Conflicting trials on the same site | Homepage FAQ: 30 minutes; closing CTA: three sessions; guide hub: three 15-minute sessions | Normalize to the current homepage offer; record app-enforcement verification separately |
| Wrong final weekly checkout destination | `index.html` final weekly CTA used the 90-day product ID, while weekly pricing card used the weekly ID | Correct destination; test both weekly anchors and revenue attribution |
| Good baseline metadata and local links | `seo-baseline.json`: existing titles, descriptions, canonicals, JSON-LD and sitemap for all intended pages | Preserve structure; add automated checks and entity links |
| Entity graph lacked connected IDs/profiles | Homepage and guides used missing/different Organization identifiers | Standardize graph relationships; use verified repository and existing founder GitHub identity |
| Category/comparison overlap | Category page repeated a competing price table with different figures from comparison pages | Make category page educational and keep source-reviewed comparisons distinct |
| Comparison metadata disagreed on tool count | Title said eight; social tags/schema said six | Use a consistent seven-product comparison, without artificial rankings |
| Outdated competitor information | Parakeet current credit pricing differs; LockedIn public navigation includes desktop/mobile; some pricing amounts not publicly extractable | Remove stale numbers and unsupported absence claims; label verification gaps |
| Unsupported statistics and weak source chains | Population assumptions, salary aggregates, detection percentages and unlike-period price multiples | Replace with a primary-source research resource, retain URL and document the change |
| Gemini copy guaranteed free usage | Homepage and setup guide promised sufficient free quota | Explain model/project limits, separate billing and current key setup |
| Receipt query values could reach analytics | GA initialization preceded URL cleanup; Clarity ran on receipt pages | Strip receipt queries before SDK loading; suppress recording; preserve receipt display/purchase event |

## Search visibility sample

Queries sampled included `Interview Sarthi` with external-site exclusions, `Interview Sarthi GitHub LinkedIn review`, and `best AI interview assistant India Hinglish`. Results included the official site/About page and unrelated Sarthi identities. Category searches surfaced India/Hinglish competitors such as PrerakAI, InterviewGPT and Tayyari AI, plus employer-side hiring products.

Interpretation: the category is crowded and “AI interview” has mixed candidate/employer intent. Keep the phrase **for Indian job seekers** prominent. Hindi/Hinglish is useful differentiation but not unique to this product. This sample does not prove that independent mentions are absent, establish Google rank, or quantify authority. No star counts, age-based conclusions or numerical audit scores were carried over from the attached report.

Primary product pages observed: [PrerakAI](https://prerakai.in/best-interview-assistance-tool-in-india), [InterviewGPT language guide](https://www.interviewgpt.in/blog/hindi-hinglish-ai-interview-assistant), [Tayyari AI](https://tayyariai.com/). Their own promotional claims are not independent evidence of performance.

## Vendor verification ledger

| Vendor | Official source reviewed | Result |
| --- | --- | --- |
| Cluely | https://cluely.com/pricing | Public monthly tiers verified; no independent capability tests |
| OphyAI | https://ophyai.com/in/pricing | India prices and separate trial allowances visible; generic `/pricing` redirects to US locale |
| Parakeet AI | https://www.parakeet-ai.com/ | Current credit pack and call-unit definitions visible; old comparison outdated |
| Final Round AI | https://www.finalroundai.com/pricing | Redirected to homepage; current payable amount not verified |
| LockedIn AI | https://www.lockedinai.com/pricing | Plan types and desktop/mobile links visible; payable amounts not exposed in retrieved text |
| Verve AI | https://www.vervecopilot.com/pricing | Features visible; payable amount not verified in retrieved text |
| CrackInterviewAI | https://crackinterviewai.com/ | Fetch unsuccessful; removed unsupported comparison row rather than carry unverified claims forward |

No accounts were created, paid plans purchased, private data submitted or apps installed for competitor testing. The Microsoft Store page could not be fetched; existing distribution links are preserved without invented Store claims.

## Technical reference checks

- [Google AI features](https://developers.google.com/search/docs/appearance/ai-features): ordinary search eligibility/content principles apply; no special AI schema or text file is required. This supports improving existing content and links.
- [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap): dates should reflect substantive changes. The new reviewed manifest prevents build-time date inflation.
- [Breadcrumb documentation](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb): visible navigation and structured trails should agree.
- [Gemini limits](https://ai.google.dev/gemini-api/docs/rate-limits) and [key documentation](https://ai.google.dev/gemini-api/docs/api-key): quotas and key requirements are provider-dependent; installed-app compatibility still requires testing.
- [Microsoft capture-affinity API](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity): capture exclusion has documented limitations. The screen-sharing page now avoids universal guarantees.

The live HTTP follow-up returned 200 for all 11 sampled URLs, including robots.txt and sitemap.xml. The production robots response contains wildcard Allow; the sitemap matches the older published dates. Results and response bodies are recorded in `live-http-baseline.json`. This was an ordinary HTTP client, not a verified Google/AI crawler test; host/CDN behavior for those clients and indexing still need post-deployment verification.

## Additional reach ideas implemented

1. Make price comparisons auditable and correct the checkout mismatch: reach should lead to the intended purchase path.
2. Give mixed-intent queries a clear audience and distinguish live assistance from autonomous mock interviews.
3. Add a practical Hinglish checklist inside the existing hub, plus topic navigation that leads readers to the relevant next guide.
4. Treat the Facts page as a stable public citation destination for identity and commercial facts.
5. Maintain source dates and disclose unknowns; do not claim superiority based on absent competitor data.
6. Add CI checks so future edits do not reintroduce stale offers or orphan the Facts page.

## Limits and content risks

Search Console and analytics account reports were unavailable, so keyword cannibalization is an intent assessment, not measured query competition. No field Core Web Vitals, Lighthouse score or independent backlink index was obtained. Browser checks validate local rendering with external requests blocked; they do not measure production latency.

The price/statistics rewrites deliberately remove unsupported assertions and shorten several pages. Existing URLs are retained, but ranking/CTR may change after recrawl. Monitor query/page performance and restore useful historical detail only with a verified source and date. The existing company guides were not fully fact-checked against every current hiring drive; salary bands, calendars and process assertions remain candidates for a separate employer-source review.

No SEO implementation guarantees higher rankings or AI recommendations. Measure changes after release and prioritize original evidence and independent recognition using the owner roadmap.
