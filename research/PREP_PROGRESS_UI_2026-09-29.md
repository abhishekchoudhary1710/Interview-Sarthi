# Prep progress UI handover

29 September 2026. The UI is implemented locally on top of the uncommitted logic described in
`PREP_PROGRESS_2026-09-29.md`. Nothing was committed, pushed, deployed or emailed by Codex.
No server files were modified for the UI.

## Entry points and design

- App navigation: **My progress**. Direct link: `/prep/app/#progress`.
- Overview: practice counts, score chart, eight skill trends, next focus, calendar, readiness reasons,
  estimated delivery metrics, and recent interviews.
- Interviews: reopen full reports, open saved question retakes, delete, or export text/JSON.
- Reviews: latest cited analysis, strong answers, priorities, weekly reviews and month report download.
- Manage history: explicit account-saving switch, matching the existing consent policy, with import
  of the one browser report as a separate action. Turning saving off deletes nothing.
- Reports: saving/retry state, progress badges, focus check, question-retake buttons and readable
  transcript. Analysis citations open the report and focus the exact original turn.
- Retakes: earlier and current answer side by side, with suggestions clearly labelled as AI-written.
- Signed-out/demo users see a feature preview, without invented scores or private history.
- `/prep/` includes an account-progress section and the monthly plan's feature list mentions history.

The UI uses the existing Paper & Ink tokens, serif typography and restrained blue accents. It widens
only the progress/comparison screens. On phones, the practice focus appears immediately after the
score card. No new package dependency or chart library was introduced.

## Files

- `prep/app/progress-view.js`: rendering, account controls and events. Imports the logic modules
  without query strings to preserve their singleton state.
- `prep/app/progress-view.css`: responsive presentation, charts, dialog and report additions.
- `prep/app/index.html`: module/style loading, navigation and screen/dialog containers.
- `prep/app/app.js`: small integration additions to Claude's existing changes:
  - `prep:screen`, `prep:account`, `prep:report-rendered` events;
  - guarded `prepApp.navigate(id)` and `prepApp.openPasses()`;
  - reopening a saved report hides the report-writing indicator and any stale purchase offer.
- `prep/index.html`: public feature preview and monthly-plan copy.
- `tests/progress_ui_browser.py`: network-isolated browser integration tests against the real app.

## Comparison and presentation decisions

- With more than one role/level track, a compact selector appears. One track is selected by default,
  preventing unlike jobs from being joined into the same overall score line. Counts/calendar cover
  the pass period; skill and delivery trends follow the selected track.
- Excluded score points are muted; exclusion reasons, scoring-version warnings and model warnings
  are visible. Fewer than two eligible interviews produces an explanation instead of a chart.
- `ready` is displayed as **Strong recent practice**, and `fixed` as **Demonstrated in this attempt**.
  The underlying logic and stored values are unchanged.
- Missing skills are unscored. Delivery values are estimates and guide ranges are contextual.
- Retake scores are labelled out of 10; full interview scores are out of 100.
- A month download covers the whole selected pass, matching its saved month analysis, rather than
  mixing a single-role numeric summary with an all-role analysis.
- If a cited turn was trimmed from storage, the UI explicitly says it is unavailable.
- If the list endpoint reports more records, the UI discloses the partial list and offers a full export.

## Validation

- Existing app suite: **125 tests passed** (`node --test tests/*.test.mjs tests/*.test.cjs`).
- Browser integration suite passed with **zero JavaScript errors**, checking widths 320, 390, 768,
  and 1440 px with no horizontal overflow.
- Browser checks cover real module integration: account opt-in/off, explicit legacy import,
  failed-save retry, JSON download, cancelable deletion and deletion failure, calendar filtering,
  role filtering, insufficient evidence, cited transcript focus, escaped transcript HTML, retake
  setup through the existing key screen, saved before/after comparison, expired-pass report access,
  signed-out privacy, demo preview and the marketing entry point.
- Browser API responses are fixtures: no live payments, Gemini usage or production account writes.
  Claude's separately reported test-server checks cover the actual backend; these UI checks do not
  claim a second live backend end-to-end verification.
- `git diff --check` and JS syntax validation passed.

Run the browser suite with a Python environment containing Playwright and installed Chromium:

```sh
python tests/progress_ui_browser.py
```

`PREP_BROWSER=/path/to/chrome` optionally supplies an existing browser. In this workspace the run used
`/tmp/apply-design-venv/bin/python` and `/data/ms-playwright/chromium-1234/chrome-linux64/chrome`.
Chromium needs execution outside the restricted sandbox in this environment.

Screenshots (gitignored) are in `.seo-preview/prep-progress-*.png`: desktop, mobile, report,
comparison, reviews, settings and landing. All depicted scores and answers are test fixtures.

## Launch remains pending

Follow the existing backend handover: deploy the server before publishing the app and only enable
`PREP_REVIEW_EMAILS` after the screens are live. The email link currently opens `/prep/app/`;
optionally point its progress-specific link at `/prep/app/#progress` when preparing release.
The new feature depends on Claude's untracked logic modules, so include those alongside the UI files.

## Follow-up: heading focus

Removed the default outline only from programmatically focused progress/comparison headings.
Heading focus remains available for screen-reader orientation; buttons, links and transcript citations
retain visible focus indicators. The browser suite now verifies heading focus and the visible ring
after pressing Tab, alongside the corrected question-card retake regression. The full browser suite
passed at all four widths with no JavaScript errors. Preview-gallery screenshots were refreshed.
No commit or deployment was performed.
