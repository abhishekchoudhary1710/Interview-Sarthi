# Search and AI visibility tracking

Query-set version: **24 September 2026**. See [the audit and growth plan](SEO_AUDIT_AND_GROWTH_PLAN.md) and [owner actions](OWNER_ACTIONS_SEO_GEO.md). This replaces the older Live-focused set because Apply and Prep are now distinct products. Preserve old observations under their original version; do not compare changed query sets as though they were identical.

No search volumes, current rankings or completed visibility measurements are claimed. The phrases are practical intent samples, not verified trending terms. `research/query-tracking-template.csv` remains the recording template.

## Fixed sample: 24 queries

### Brand and product choice

1. Interview Sarthi
2. InterviewSarthi products
3. Interview Sarthi pricing
4. Interview Sarthi review

Primary destination: the umbrella homepage. Record whether the result explains all three apps and directs people to the appropriate product.

### Apply: find jobs and fill applications

5. AI job search India
6. jobs matched to my resume India
7. jobs from multiple portals in one place
8. autofill job applications India
9. Naukri application autofill
10. why am I not getting interview calls

Destinations: `/apply/`, relevant applying guides, and public jobs/company/role pages on `apply.interviewsarthi.com`. The subdomain is publicly browsable; private CV and application operations remain separate. Check whether vacancy results are relevant and current instead of treating catalogue size as success.

### Prep: spoken practice and useful feedback

11. AI mock interview India
12. mock interview from resume and job description
13. voice interview practice with feedback
14. free AI mock interview
15. AI mock interview price India
16. TCS mock interview practice
17. how to improve weak interview answers

Destinations: `/prep/`, the CV/JD walkthrough, pricing comparison and relevant company practice pages. Prep actually conducts spoken mock interviews; these are core product queries. When a result mentions free use, check whether the 20-minute allowance and setup requirements are accurately explained.

### Live: answers during the interview

18. AI interview assistant India
19. real time AI interview answers
20. interview copilot for Windows
21. AI interview assistant screen sharing
22. AI interview assistant with one time pricing
23. Hinglish interview assistant
24. can interviewer see my screen

Destinations: `/live/` and existing category, compatibility or comparison guides. Record practice-versus-live confusion. A relevant answer must preserve supported Windows/capture scope and approximate response timing; universal invisibility is not a success criterion.

## How to collect observations

Run monthly with the same India locale, language, device class and signed-in/out state. Keep this wording stable for three months. Use a fresh conversation for each AI prompt and record whether web search was enabled. Treat mobile and desktop checks as separate series.

Sample Google Search and available Google AI experiences; optionally repeat in ChatGPT search, Claude web search, Perplexity and Gemini. Record timestamp, full query, visible product/model version, mode, mention, citation, exact linked URL, competitors and saved evidence. Mark access failures and unavailable features explicitly. Do not present a sparse `site:` search as proof of deindexing.

Calculate mention/citation rates only across completed comparable checks, showing numerator and denominator. A chatbot's list position is not a stable search ranking. This small manual sample does not measure total demand or replace owner reports.

## Connect visibility to outcomes

Use a 90-day Search Console baseline and compare equivalent 28-day periods by page/query, host, country and device. Separate brand traffic from new-user discovery. Investigate high-impression pages using their actual queries before changing titles or consolidating URLs. Similar wording alone does not establish cannibalization.

In GA4, inspect `product_click` by `product` (`apply`, `prep`, `live`), `placement` and `destination_kind` (`product_page`, `application`). This measures a handoff, not activation or purchase. Review app completion separately and reconcile revenue with payment records. The full event values and setup steps are in [owner actions](OWNER_ACTIONS_SEO_GEO.md).

`ai_referral_visit` provides limited `ai_source`/`landing_page` attribution; absent signals remain unknown. An ordinary Google referrer cannot reliably identify an AI experience. Use the available Google generative-AI impressions report and Bing citation reports as distinct visibility measures, not conversion counts.

No ranking benefit is assumed from FAQ markup, `llms.txt` or successful IndexNow submission. Measure useful discovery and actual product outcomes after verified deployment.
