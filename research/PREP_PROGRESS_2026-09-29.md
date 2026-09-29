# Prep Sarthi: progress across the month (logic done, screens to build)

29 September 2026. The owner approved a "My progress" feature for 30-day pass holders. The logic, storage and server are
built and tested. **No screen exists yet.** This note is the contract for whoever builds the screens.

Nothing is visible to users today. Nothing is saved to any account until a screen calls `setEnabled(true)`.

## Modules (all in `prep/app/`)

| File | What it does |
|---|---|
| `history.js` | Saved interviews in the account: switching saving on and off, saving with retry, listing, reading, deleting, exporting and importing old reports |
| `progress.js` | Pure numbers for the progress page: `buildProgress`, report badges (`reportChanges`), `summarize`, `carryFocus` |
| `insights.js` | The month analysis written by Gemini (patterns linked to real answers), weekly and end-of-pass reviews, `monthReportText` |
| `redrill.js` | Answering one question again, then comparing it with the old answer |
| `app.js` | Wires these into the interview flow and exposes `window.prepApp` |

Server: `AI-Helps_SAAS/license-server/src/history.js` (`/mock/history/*`) and `src/prepreview.js` (end-of-pass email, switched off).

Import the modules exactly as `app.js` does. `app.js` imports `history.js`, `progress.js`, `insights.js` and `redrill.js` without a `?v=` tag. A different tag creates a second module instance with its own state.

## What already happens without any screen

- **Every report is saved in this browser.** `ps_last_report` holds the latest full report and `ps_history` holds a summary of each of the last 20.
- **When a signed-in pass holder has saving on, each report also goes to the account.** A failed save is retried from an outbox on the next load, after sign-in, when the browser comes back online, and on a timer.
- **The report carries three new fields:**
  - `next_focus {group, issue, drill}`: one habit to fix.
  - `questions[].answer_turns`: which transcript turns answered each question.
  - `focus_check {status, evidence_turns, note}`: only when the previous report set a focus.
- **The focus is carried into the next full interview (pass holders only).** The interviewer is told privately to give the candidate a chance to show the habit. The next report says whether it is `fixed`, `improved`, `still_open` or `not_tested`.
- **Each new report record gets `record.changes`** (see `reportChanges`), which provides the "+8 since last time" badges.
- **Month analyses are refreshed in the background** after a report and on load, when saving is on and a key is present.

## `window.prepApp`

- `state()` returns `{signedIn, account, pass, expiresAt, hasKey, language, name, phase, redrill}`.
- `openInterview(id)` loads a saved interview and draws it on the existing report screen.
- `startRedrill(interviewId, questionIndex)` sets up a 3-minute call on that question. The live screen opens, and the key screen first if there is no key. It throws if there is no pass or a call is running.
- `cancelRedrill()`
- `refreshAnalyses({force})` brings the saved analyses up to date now.
- `events` is `HISTORY_EVENTS`.

### Window events

- `prep:ready`: the page has finished booting.
- `prep:report`: `detail.record` is the finished report, including `record.changes` and `record.id`.
- `prep:redrill`: `detail.item` is the saved re-answer. It is cancelable: call `preventDefault()` when you draw it. Otherwise `app.js` shows a plain fallback card.

### `HISTORY_EVENTS`

- `status`: `{id, state}`, where `state` is one of `saving | saved | retry | off | signed_out | no_pass | failed`. `statusOf(id)` gives the last state.
- `changed`: something was saved or deleted, so refresh the list.
- `analysis`: `{id, scope, analysis}`, where `scope` is `latest`, `week` or `period`.

## `history.js`

- **The setting:**
  - `getPrefs()` returns `{enabled, consent_version, current_consent_version, retention_days: 365, pass:{live, expires_at}}`, or null when signed out.
  - `setEnabled(on)`. Switching off stops saving and deletes nothing.
- **Listing:**
  - `listSummaries()` returns `{items, periods, prefs, source, more}`. It merges the account with this browser, newest first.
  - Items that exist only in this browser have `local_only: true`.
  - `periods` is `[{start, end, current}]`, one per pass. Show one period at a time.
  - `knownSummaries()` and `knownPeriods()` return the same data from cache, with no network.
- **Reading:**
  - `getInterview(id)` returns the record `{id, at, elapsed, language, model, report, metrics, transcript, focus_carried?, changes?}`.
  - `getItems(ids)` returns full items.
- **Deleting:**
  - `deleteItem(id)` removes the item from the account and from this browser.
  - `deleteAll()` removes every item and leaves the setting as it is.
- **Exporting:** `exportAll()` returns `{json, text}`. Offer both as downloads.
- **Old reports:**
  - `importable()` lists old full reports in this browser that are not in the account. At most one exists.
  - `importLocal()` uploads them. Ask the person first.
- **Save states:**
  - `pending()` lists ids waiting in the outbox.
  - `saveItem(item)` and `saveInterview(record)` are used by `app.js`.

## `progress.js`: `buildProgress(items, {period, track, now})`

Pass the items from `listSummaries()` and the current period. It returns:

- **`period`**: `{start, end, day, days, days_left, ended}`
- **`totals`**: `{interviews, practice_days, minutes, streak}`
- **`calendar`**: `[{date, interviews:[ids], minutes, best, future}]`, one entry per day of the pass. Empty days stay empty.
- **`tracks`**: `[{key, role, level, count}]`, plus `track`. Offer a role filter only when there is more than one track.
- **`score`**:
  - `{points:[{id, at, score, comparable, reason, writer, demo, minutes}], enough, first, latest, best, average, recent, change_since_first, change_since_last, different_roles, message}`.
  - Draw a line only when `enough` is true; otherwise show `message`.
  - Show non-comparable points greyed out, with the text from `REASONS[reason]`.
- **`groups`**: eight skill groups, each `{id, label, n, points, first, latest, best, start, recent, change, trend, status}`.
  - `trend` is one of `up | down | flat | not_enough`.
  - `status` is one of `strong | developing | weak | not_tested`.
  - Scores are out of 10.
- **`delivery`**: `[{id, label, unit, target, points, latest, average, recent, latest_in_target, trend, approximate: true}]`.
  - `trend` is one of `better | worse | flat | in_range | not_enough`.
  - `talk_share` is a fraction; show it as a percentage.
- **`coverage`**: `{strong, developing, weak, thin, never_tested, planned_not_scored}`
- **`readiness`**:
  - `{level: not_enough | not_yet | getting_there | ready, reasons:[{code, text, group?, value?}]}`.
  - Always show the reasons.
- **`focus`**: `{current:{group, issue, drill, from_id}, checks:[{id, at, focus, status, note}], fixed, open}`
- **`warnings`**: `[{code, text, ids?}]`, covering mixed report writers, changed rules and excluded interviews. Show these.

`reportChanges(summary, items, period)` gives the badges for one report:

- `{comparable, reason, score:{since_last, since_first, same_role_as_last, …} | null, groups:[{id, label, score, since_last, since_first, first_time}]}`.
- `score` is null for the first comparable interview.

## `insights.js`

- **Saved analyses** appear in `listSummaries().items` with `kind: "analysis"`. Their ids come from `analysisId(period, scope, week)`:
  - `an-<period>-latest`
  - `an-<period>-w1`, `-w2`, …
  - `an-<period>-period`
- **Shape:** `{enough, message?, scope, window, based_on:[ids], model, summary, patterns, strong_answers, next_priorities, facts}`.
  - Each pattern is `{type: recurring_weakness | improved | inconsistent | strength, group, group_label, title, detail, evidence:[{interview_id, turn}], interviews, drill}`.
  - Every piece of evidence is a real candidate turn. Link it: `openInterview(interview_id)`, then scroll to `transcript[turn - 1]`.
- **`dueAnalyses(...)`** says what is missing or stale, so the page can show "your week 2 review is ready".
- **`monthReportText(progress, analysis)`** returns the downloadable end-of-pass report.

## `redrill.js`

- **Choosing a question:** after `startRedrill`, the page shows the live screen. The question is in `prepApp.state().redrill.question`.
- **The result** arrives as `prep:redrill` with `detail.item`:
  - `summary`: `{interview_id, question_index, question, score_before, score_after, change, verdict, improved[], still_missing[]}`
  - `body`: `{source:{before:{text, gist, better, missing, score}}, after:{text, turns}, result, transcript}`
- **Keep what they said apart from the AI's suggestion.** `before.text` and `after.text` are their own words. `before.better` is the AI-written stronger answer, so label it that way.
- **Saved re-answers** are listed with `kind: "redrill"`.

## Rules for the screens

1. **Consent copy must match `privacy.html` → "Saved interviews".**
   - It saves the report, the transcript, the delivery numbers and short cited quotes.
   - It never saves the CV, the job description or the voice.
   - Items are deleted after 12 months, can be deleted at any time, and remain readable after the pass ends.
   - If the wording changes, change `HISTORY.CONSENT_VERSION` in the server's `src/history.js` too.
2. **Escape every string.** Summaries, patterns and transcripts contain the candidate's words and AI text. `app.js` has `escapeHtml`.
3. **Say plainly when there is too little data.** Show `message` or "not enough" rather than an empty chart. Missing scores are "Not tested", never 0.
4. **Label delivery numbers as estimates.** Say "outside the usual range", never "wrong".
5. **Readiness is practice feedback, not a hiring prediction.** No percentiles and no leaderboards.
6. **Demo users have no history.** A locked "Your 30-day progress" preview on the demo report and on `/prep/` is approved.
7. **Two copy lines were adjusted and should stay true:**
   - `prep/index.html`: "Reports stay in your browser unless you choose to keep them in your account."
   - The `prep/app/index.html` lede.

## Launch checklist

1. **Screens:** build them and test locally. `python3 -m http.server 8765 --bind 127.0.0.1` makes the app use the TEST worker. `id_token "test:<email>"` signs in there, and a sandbox Cashfree purchase gives a pass.
2. **Production worker:** deploy from a clean export of AI-Helps_SAAS. No dashboard database change is needed, because the worker creates `mock_history`, `mock_history_prefs` and `mock_history_mail` itself.
3. **End-of-pass email:** set `PREP_REVIEW_EMAILS = "1"` in `wrangler.toml` production vars and deploy again, once the screens are live.

## Tests

- `node --test tests/*.test.mjs tests/*.test.cjs` in Interview-Sarthi: 124 tests, including `progress.test.mjs` and `history_client.test.mjs`.
- `node --test test/*.test.js` in license-server: 143 tests, including `history.test.js`.
