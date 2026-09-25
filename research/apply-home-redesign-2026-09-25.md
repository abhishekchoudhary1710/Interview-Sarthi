# ApplySarthi homepage redesign — 25 September 2026

Redesign for `/apply/`, approved for publication on 25 September 2026. The live page could not be retrieved through the
initial browser fetch, so the review used this checkout's existing page, product fact register,
recent public-site audit and existing app screenshot. No current rankings or keyword volumes were measured.

## Design and content

- Green and warm white product layout, responsive header and a focused hero.
- Separate links to personalised matches and the public job browser.
- Existing app screenshot with keyboard-accessible enlargement and a clear snapshot caption.
- Three feature cards, setup steps, review controls, application guides and native FAQ disclosures.
- Free access, Gemini requirements, desktop Chrome requirement and optional submission behaviour
  remain explicit. No invented testimonials, usage totals or outcome statistics.
- Existing conversion analytics retained; no extra tracking library added.
- Dedicated matching social share image, with an editable HTML source.

## Search foundations

The title and description now describe free job search, CV matching and autofill. The page retains
its canonical URL, indexability, software offer and breadcrumbs. A WebPage node connects the page
to the application; FAQ schema matches visible copy. Crawlable links connect relevant application
guides and the public job browser. Only this page's sitemap modification date advances.

The implementation follows Google's guidance on clear titles, useful organised content and
descriptive internal links: [Google Search Central SEO starter guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide).
These are technical and content improvements, not evidence of increased rankings or traffic.
FAQ markup is not a promise of a special search result appearance.

## Verification

- Site SEO audit: 67 pages, 60 indexable, zero errors and warnings.
- Generated Apply articles: all 13 match their source.
- Sitemap matches the reviewed page manifest.
- Python regression tests: 16 pass. Existing Node test suites: all four pass.
- Browser checks at 320, 360, 390, 768, 1024 and 1440 pixels: no horizontal overflow or script errors.
- Mobile menu, Escape dismissal, screenshot dialog and focus return pass.
- FAQ disclosures and visible/schema answer equality pass.
- Image loading, JavaScript-disabled navigation and FAQ fallback pass.
- External requests blocked in browser QA to avoid sending test analytics; local font fallback was
  therefore also exercised. No measured production Core Web Vitals or accessibility certification is claimed.

Preview: `http://localhost:8938/apply/` while the local server is running. Forward port 8938 when
connecting over SSH. Screenshots and machine-readable checks are in ignored
`.seo-preview/apply-redesign/`. The backend job application is a separate repository and deployment.
