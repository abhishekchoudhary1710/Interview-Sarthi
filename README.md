# Interview Sarthi

InterviewSarthi brings together three apps for job seekers. The [homepage](https://interviewsarthi.com/) explains each app and its starting price:

- [Apply Sarthi](https://interviewsarthi.com/apply/): jobs from multiple portals, CV matching and application autofill.
- [Prep Sarthi](https://interviewsarthi.com/prep/): spoken AI mock interviews with follow-up questions and feedback.
- [Live Sarthi](https://interviewsarthi.com/live/): the existing Windows interview assistant, with CV-based answer suggestions during a call.

[Official website](https://interviewsarthi.com/) · [Product facts](https://interviewsarthi.com/facts.html) · [Microsoft Store](https://apps.microsoft.com/detail/9NMKQPSQ1KS8) · [Releases](https://github.com/abhishekchoudhary1710/Interview-Sarthi/releases)

## What this repository contains

The public static website, product information, interview guides, website analytics and the Prep browser app under `prep/app/`. The root page is the three-product homepage; the existing Windows product page is at `live/index.html`. This repository does not contain the desktop application's source code. Public availability of this repository does not establish an open-source license.

## Live Sarthi access

- Windows 10 version 2004 or later, or Windows 11.
- Transcription and resume-grounded suggestions for mock calls and permitted live use.
- English, Hindi and Hinglish support; bring your own Google Gemini key.
- 30 minutes free per computer, with all features and no card.
- One-time passes: ₹99 / 2 days on 1 device, ₹299 / 30 days on 2 devices ($9.99 and $29.99 outside India). No automatic renewal. Google API quotas and billing are separate.

See [SITE_FACTS.md](SITE_FACTS.md) for evidence, device limits and maintenance rules. Use assistance only where permitted by the employer, interviewer and assessment provider.

## Run locally

No frontend build or dependency installation is required:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://localhost:8000`. Website analytics are configured in `assets/analytics.js`; browser QA intercepts external requests so test events do not reach providers.

## Validate changes

Python 3.10+ and Node.js 18+:

```sh
python scripts/build_apply_pages.py --check
python scripts/seo_audit.py
python scripts/generate_sitemap.py --check
python -m unittest discover -s tests -p 'test_*.py'
node --test tests/analytics.test.cjs tests/home-routing.test.cjs tests/mock_engine.test.mjs tests/interview_plan.test.mjs
```

Optional browser checks require Python Playwright and Microsoft Edge:

```sh
python tests/browser_smoke.py
```

This checks desktop/mobile layouts, receipt rendering, weekly checkout destinations and analytics behavior without purchasing anything. Screenshots and results go to ignored `.seo-preview/`.

Prep's normal interview screen does not display diagnostic logs or a duplicate transcript.
Support sessions can explicitly use `/prep/app/?diagnostics=1`; this setting is not persisted.
Run `python tests/prep_diagnostics_smoke.py` with Playwright and Chromium to check this behaviour
and current captions without making AI or microphone calls. `BROWSER_EXECUTABLE` can select a local browser.

## Maintain sitemap dates

After a meaningful content change, record its actual date:

```sh
python scripts/generate_sitemap.py --record facts.html --date YYYY-MM-DD
python scripts/seo_audit.py
```

The reviewed allow-list in `scripts/seo_pages.json` controls inclusion and dates. Formatting edits and builds do not advance dates. Add new canonical pages deliberately; noindex receipt/error pages are excluded. Existing IndexNow behavior remains in its separate workflow.

## ApplySarthi pages

The guide and comparison pages under `apply/` are generated from `scripts/apply_pages/`, so the shared header, footer and
schema are written once rather than thirteen times. Edit the content module, then:

```sh
python scripts/build_apply_pages.py      # rewrite the HTML, which is committed like any other page
```

`scripts/apply_pages/_shared.py` is the fact register for that content: every number an ApplySarthi page
states must exist there with a note on where it was read from. See [APPLYSARTHI_SEO.md](APPLYSARTHI_SEO.md).

The product homepage `apply/index.html` is maintained directly, with `assets/apply-home.css` and
`assets/apply-home.js`. Its social share image is `assets/og-apply-home.jpg`, rendered at 1200×630
from `assets/og-apply-home.source.html`. Guide share images are separate. Run
`python tests/apply_browser_smoke.py` with Python Playwright and Chromium for responsive and
interaction checks; `BROWSER_EXECUTABLE` optionally selects a locally installed Chromium binary.
External analytics and font requests are blocked during this test. Screenshots go to
`.seo-preview/apply-redesign/`. See [the redesign verification](research/apply-home-redesign-2026-09-25.md).

## Research and reach

- [Current full audit and release plan](SEO_AUDIT_AND_GROWTH_PLAN.md)
- [24 September research](research/seo-growth-research-2026-09-24.md)
- [Public Apply job-site audit](research/seo-apply-public-audit-2026-09-24.md)
- [Page-by-page intent map](research/seo-page-map-2026-09-24.csv)

- [Research findings](research/SEO_GEO_RESEARCH_2026-09-15.md)
- [Benchmark methodology](research/README.md)
- [Monthly query tracking](TRACKING_QUERIES.md)
- [Owner actions and 90-day roadmap](OWNER_ACTIONS_SEO_GEO.md)
- [Implementation report](SEO_GEO_IMPLEMENTATION_REPORT.md)

## Contact

Built by [Abhishek Choudhary](https://github.com/abhishekchoudhary1710). Contact [support@interviewsarthi.com](mailto:support@interviewsarthi.com) or open a repository issue without credentials, license keys or private interview material.

[Privacy](https://interviewsarthi.com/privacy.html) · [Terms](https://interviewsarthi.com/terms.html) · [Refund policy](https://interviewsarthi.com/refunds.html)
