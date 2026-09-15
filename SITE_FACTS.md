# Interview Sarthi: maintained product facts

Website evidence reviewed: 2026-09-15. Baseline: `e942363`.
This records the current advertised offer, not a certification of the desktop binary or billing backend.

## Identity and positioning

Interview Sarthi is a Windows AI interview assistant for Indian job seekers, with resume-grounded assistance and English, Hindi and Hinglish support.
It can support mock calls and permitted live interview use. It is not advertised here as an autonomous mock interviewer or resume builder.

| Fact | Value | Evidence |
| --- | --- | --- |
| Brand/domain | Interview Sarthi; https://interviewsarthi.com/ | `CNAME`, homepage canonical |
| Founder/developer | Abhishek Choudhary | Existing `about.html` identity and GitHub link |
| Support | support@interviewsarthi.com | Homepage, About, help |
| Windows | Windows 10 version 2004 or later; Windows 11 | Homepage systems FAQ |
| Languages | English, Hindi, Hinglish | Homepage feature section |
| AI setup | User supplies a Google Gemini API key | Homepage, help, privacy |
| Data path | Audio/resume context sent from PC to Google; local transcripts | Privacy policy; app not independently inspected |
| Distribution | Microsoft Store link and GitHub release installer | Existing homepage destinations |

## Canonical advertised offer

- Trial: **30 minutes free per computer**, all features, no card or Interview Sarthi account. FAQ says answers stop after the trial; transcripts remain available. Reinstallation does not reset the trial.
- 2-Day Pass: ₹99 once, 2 days, 1 device; checkout product `pdt_0Nn41S0EP7d5UNAJZNPAL`.
- 7-Day Pass: ₹399 once, 7 days, 1 device; `pdt_0NmLzNTWbybTsXtpmtmaH`.
- 1-Month Pass: ₹999 once, 30 days, 2 devices; `pdt_0NmHQqaKlKiZ57ISIRzdn`.
- 3-Month Pass: ₹1,999 once, 90 days, 2 devices; `pdt_0NmHNZ2I6qiJg6CrzInBg`.
- Paid passes advertise unlimited sessions during validity, without automatic renewal. Google API quotas/billing are separate.
- Evidence: current homepage pricing cards, JSON-LD offers, FAQ and matching checkout URLs. Older About/guide session-count copy is stale.
- Refund claims remain governed by `refunds.html`; do not change commercial policy as an SEO edit.

## Entity identifiers

- Organization: `https://interviewsarthi.com/#organization`
- Website: `https://interviewsarthi.com/#website`
- Software: `https://interviewsarthi.com/#software`
- Founder: `https://interviewsarthi.com/about.html#founder`

## Official identity links

- Public website repository: https://github.com/abhishekchoudhary1710/Interview-Sarthi (successfully cloned).
- Founder GitHub: https://github.com/abhishekchoudhary1710 (already identified by About; owns repository).
- Distribution destination: https://apps.microsoft.com/detail/9NMKQPSQ1KS8 (linked consistently by site; Store content could not be fetched during audit). Keep as a download link; do not claim Store rating, publisher verification or add it as a verified Organization profile.
- LinkedIn, YouTube, Product Hunt: no verified owner-controlled URLs available; omit from schema.

## Maintenance

When the offer changes, update this file, visible pricing/trial copy, JSON-LD, `assets/analytics.js` pass labels and the Facts page together. Run `python scripts/seo_audit.py` and the regression tests. Update only meaningful page dates in `scripts/seo_pages.json`, then regenerate the sitemap.

Owner verification pending: actual installed trial enforcement, billing product durations/device caps/tax presentation, Store description, and current app compatibility. Do not infer these from a marketing page alone.
