# ApplySarthi content build — 18 September 2026

ApplySarthi had one page on this site (`apply/index.html`) against Interview Sarthi's 38. One page can
rank for a product name and very little else, so this round built the surrounding content the other
product already had: a category page, a comparison set, a guides hub with guides under it, an
objection-handling page, and a first-party dataset.

This was the 18 September content build. The app now also has public job details, a job directory, company and role pages, and separate sitemaps at `apply.interviewsarthi.com`. The marketing site and public job site have different search intents. See [the 24 September public-site audit](research/seo-apply-public-audit-2026-09-24.md).

## What was added

Thirteen pages, all under `apply/`:

| Page | Role |
|---|---|
| `auto-apply-jobs-india.html` | Category page. The three kinds of auto-apply tool; why Naukri and Foundit break most of them. |
| `best-auto-apply-tools-india.html` | Comparison hub. Six products, published prices, Indian board coverage. |
| `is-auto-apply-safe.html` | Objection handling. Five risks ranked by how often they actually bite. |
| `job-application-statistics-india.html` | First-party dataset. Field coverage, sources and cities across 60,975 open postings. |
| `guides/index.html` | Guides hub. |
| `guides/naukri-auto-apply.html` | Why server-side tools cannot reach Naukri, and what can. |
| `guides/why-no-interview-calls.html` | Five reasons applications go unanswered, in order. |
| `guides/ats-resume-format-india.html` | What parsers actually fail on; Indian CV conventions worth dropping. |
| `vs-lazyapply.html` | Volume against aim. |
| `vs-simplify-jobs.html` | Closest in philosophy; different coverage. |
| `vs-loopcv.html` | Auto-apply plus outbound employer email. |
| `vs-jobright-ai.html` | Strong matching, United States market. |
| `vs-aiapply.html` | A suite against a specialist. |

## How they are maintained

The pages are generated. `scripts/apply_pages/` holds each page's own argument; `scripts/build_apply_pages.py`
wraps it in the shared chrome and writes ordinary static HTML into the tree. The generated files are
committed like any other page — the generator exists so that a change to the header, footer or schema is
made once rather than thirteen times.

```bash
python scripts/build_apply_pages.py            # rewrite the pages
python scripts/build_apply_pages.py --check    # fail if a committed page is stale (runs in CI)
```

`scripts/apply_pages/_shared.py` is the fact register for this content. **Every number stated on an
ApplySarthi page must exist in that file**, where it carries a note saying where it was read from. A
figure that is not in `_shared.py` may not be asserted on a page; link to the source that has it instead.

## Evidence standards held to

Competitor facts were read from each company's own public pages on 18 September 2026 and are linked from
the page that cites them. Where a company does not publish a price publicly — Simplify's paid tier,
Jobright's candidate plans, AIApply's plans — the pages say so rather than repeat a third-party figure.
Each comparison ends with what we could not verify, and states that a gap is missing public information
rather than a missing feature.

The dataset page publishes first-party figures read from the ApplySarthi database on 18 September 2026,
with the method and its limits stated: open postings rather than vacancies, presence of a field rather
than its accuracy, and a sample weighted towards employers whose boards are technically reachable.

No outcome claims, response-rate figures or "X% of resumes are rejected" statistics were published,
because none could be sourced.

## Validation

```text
SEO audit: 54 pages, 52 indexable, 0 errors, 0 warnings   (was 41 / 39)
Sitemap matches the reviewed page manifest.
build_apply_pages.py --check: 13 pages match their source.
Python regression tests: 8 passed
```

## Still outstanding

- ~~The share image is wrong.~~ **Done, 18 September 2026.** All fourteen ApplySarthi pages now use
  `assets/og-apply.jpg` instead of `assets/og.jpg`, which pictures the Interview Sarthi overlay and stays
  on that product's pages. The card is rendered from `assets/og-apply.source.html`, whose `LIVE` object
  holds the wording that is published; open it with `?h=&s=&size=` to try an alternative before
  re-rendering. Changing it means editing that file, re-rendering to `assets/og-apply.jpg`, and updating
  `LIVE` to match — `OG_IMAGE` in the generator and the two references in `apply/index.html` already
  point at the stable filename and do not need touching again.

  The published wording is *"We auto-apply to every job that fits you."* That is the owner's decision,
  taken with the following noted: ApplySarthi does not submit by default — Autopilot is off until
  switched on — so the headline promises more than a new user's first session delivers, and it places
  ApplySarthi in the blind-auto-apply category that `vs-lazyapply.html` and `vs-loopcv.html` argue
  against. Worth revisiting if early users arrive expecting applications to send themselves.
- **Pricing.** ApplySarthi is described as free in early access, which is currently true. When plans
  launch, the offer in `apply/index.html`'s schema and the price column in
  `best-auto-apply-tools-india.html` both need updating, and `_shared.py` is where to start.
- **Competitor facts age.** Re-read the five linked pricing pages before quoting them in any new content,
  and update `REVIEWED` in `_shared.py` when you do.
