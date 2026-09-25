# Interview Sarthi: maintained product facts

Website evidence reviewed: 2026-09-15. Baseline: `e942363`.
Product navigation and naming updated: 2026-09-24.
This records the current advertised offer, not a certification of the desktop binary or billing backend.

## Identity and positioning

InterviewSarthi is the shared brand. Its root homepage explains three products and links to their existing websites:

- `/apply/`: Apply Sarthi brings together jobs from multiple portals, with CV matching and application autofill.
- `/prep/`: Prep Sarthi runs spoken AI mock interviews, follow-up questions and feedback. The browser app is at `/prep/app/`. Free 7-minute demo with no sign-up, then one pass only: ₹99 ($9.99 outside India) for 30 days of unlimited mock interviews, paid once, never renews (since 25 September 2026; the 7-Day Pass is withdrawn).
- `/live/`: Live Sarthi is the existing Windows AI interview assistant, with CV-based suggestions during a call.

The platform details and passes below describe **Live Sarthi**, previously presented on the root homepage as Interview Sarthi. It can support mock calls and permitted live use; Prep is the separate AI mock interviewer. Moving the product page does not change the desktop app's name or access terms.

| Fact | Value | Evidence |
| --- | --- | --- |
| Brand/domain | Interview Sarthi; https://interviewsarthi.com/ | `CNAME`, homepage canonical |
| Founder/developer | Abhishek Choudhary | Existing `about.html` identity and GitHub link |
| Live product page | https://interviewsarthi.com/live/ | `live/index.html` canonical |
| Support | support@interviewsarthi.com | Live page, About, help |
| Windows | Windows 10 version 2004 or later; Windows 11 | Live page systems FAQ |
| Languages | English, Hindi, Hinglish | Live page feature section |
| AI setup | User supplies a Google Gemini API key | Live page, help, privacy |
| Data path | Audio/resume context sent from PC to Google; local transcripts | Privacy policy; app not independently inspected |
| Distribution | Microsoft Store link and GitHub release installer | Existing Live page destinations |

## Live Sarthi advertised offer

- Trial: **30 minutes free per computer**, all features, no card or Interview Sarthi account. FAQ says answers stop after the trial; transcripts remain available. Reinstallation does not reset the trial.
- 2-Day Pass: ₹99 once, 2 days, 1 device; checkout product `pdt_0Nn41S0EP7d5UNAJZNPAL`.
- 1-Month Pass: ₹299 once ($29.99 outside India), 30 days, 2 devices; `pdt_0NmHQqaKlKiZ57ISIRzdn`.
- Outside India the 2-Day Pass is $9.99. Since 25 September 2026 these are the only two passes; the 7-Day and 3-Month passes are withdrawn and must not be offered or linked (`plan=7d`, `plan=90d`).
- Paid passes advertise unlimited sessions during validity, without automatic renewal. Google API quotas/billing are separate.
- Evidence: `live/index.html` pricing cards, JSON-LD offers, FAQ and matching checkout URLs. Older About/guide session-count copy is stale.
- Refund claims remain governed by `refunds.html`; do not change commercial policy as an SEO edit.

## Entity identifiers

- Organization: `https://interviewsarthi.com/#organization`
- Website: `https://interviewsarthi.com/#website`
- Live software: `https://interviewsarthi.com/#software` (stable identifier retained; product URL is `/live/`)
- Apply software: `https://interviewsarthi.com/apply/#software`
- Prep software: `https://interviewsarthi.com/prep/#software`
- Founder: `https://interviewsarthi.com/about.html#founder`

## Official identity links

- Public website repository: https://github.com/abhishekchoudhary1710/Interview-Sarthi (successfully cloned).
- Founder GitHub: https://github.com/abhishekchoudhary1710 (already identified by About; owns repository).
- Distribution destination: https://apps.microsoft.com/detail/9NMKQPSQ1KS8 (linked consistently by site; Store content could not be fetched during audit). Keep as a download link; do not claim Store rating, publisher verification or add it as a verified Organization profile.
- LinkedIn, YouTube, Product Hunt: no verified owner-controlled URLs available; omit from schema.

## Maintenance

When the offer changes, update this file, visible pricing/trial copy, JSON-LD, `assets/analytics.js` pass labels and the Facts page together. Run `python scripts/seo_audit.py` and the regression tests. Update only meaningful page dates in `scripts/seo_pages.json`, then regenerate the sitemap.

Owner verification pending: actual installed trial enforcement, billing product durations/device caps/tax presentation, Store description, and current app compatibility. Do not infer these from a marketing page alone.
