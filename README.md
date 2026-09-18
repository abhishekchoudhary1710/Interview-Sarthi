# Interview Sarthi

Interview Sarthi is a Windows AI interview assistant for Indian job seekers, with resume-grounded assistance and English, Hindi and Hinglish support.

[Official website](https://interviewsarthi.com/) · [Product facts](https://interviewsarthi.com/facts.html) · [Microsoft Store](https://apps.microsoft.com/detail/9NMKQPSQ1KS8) · [Releases](https://github.com/abhishekchoudhary1710/Interview-Sarthi/releases)

## What this repository contains

The public static website, product information, interview guides and website analytics. It does not contain the desktop application's source code. Public availability of this repository does not establish an open-source license.

## Product and access

- Windows 10 version 2004 or later, or Windows 11.
- Transcription and resume-grounded suggestions for mock calls and permitted live use.
- English, Hindi and Hinglish support; bring your own Google Gemini key.
- 30 minutes free per computer, with all features and no card.
- One-time passes: ₹99 / 2 days, ₹399 / 7 days, ₹999 / 30 days, ₹1,999 / 90 days. No automatic renewal. Google API quotas and billing are separate.

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
node --test tests/analytics.test.cjs
```

Optional browser checks require Python Playwright and Microsoft Edge:

```sh
python tests/browser_smoke.py
```

This checks desktop/mobile layouts, receipt rendering, weekly checkout destinations and analytics behavior without purchasing anything. Screenshots and results go to ignored `.seo-preview/`.

## Maintain sitemap dates

After a meaningful content change, record its actual date:

```sh
python scripts/generate_sitemap.py --record facts.html --date YYYY-MM-DD
python scripts/seo_audit.py
```

The reviewed allow-list in `scripts/seo_pages.json` controls inclusion and dates. Formatting edits and builds do not advance dates. Add new canonical pages deliberately; noindex receipt/error pages are excluded. Existing IndexNow behavior remains in its separate workflow.

## ApplySarthi pages

The pages under `apply/` are generated from `scripts/apply_pages/`, so the shared header, footer and
schema are written once rather than thirteen times. Edit the content module, then:

```sh
python scripts/build_apply_pages.py      # rewrite the HTML, which is committed like any other page
```

`scripts/apply_pages/_shared.py` is the fact register for that content: every number an ApplySarthi page
states must exist there with a note on where it was read from. See [APPLYSARTHI_SEO.md](APPLYSARTHI_SEO.md).

## Research and reach

- [Research findings](research/SEO_GEO_RESEARCH_2026-09-15.md)
- [Benchmark methodology](research/README.md)
- [Monthly query tracking](TRACKING_QUERIES.md)
- [Owner actions and 90-day roadmap](OWNER_ACTIONS_SEO_GEO.md)
- [Implementation report](SEO_GEO_IMPLEMENTATION_REPORT.md)

## Contact

Built by [Abhishek Choudhary](https://github.com/abhishekchoudhary1710). Contact [support@interviewsarthi.com](mailto:support@interviewsarthi.com) or open a repository issue without credentials, license keys or private interview material.

[Privacy](https://interviewsarthi.com/privacy.html) · [Terms](https://interviewsarthi.com/terms.html) · [Refund policy](https://interviewsarthi.com/refunds.html)
