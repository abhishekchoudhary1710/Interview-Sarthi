# Search and AI visibility tracking

Run monthly using the same locale (India), language, device class and signed-in/out state. Use a fresh conversation for each AI prompt; record whether web search was actually enabled. Keep the wording stable for at least three months.

No measurements have been filled in. `research/query-tracking-template.csv` is empty. A provider may omit a brand even when it can access the website; an appearance in a sample is not a stable rank.

## Fixed set: 25 queries

1. AI interview assistant India
2. best AI interview assistant India
3. real time AI interview assistant India
4. Windows AI interview assistant
5. resume based interview assistant
6. Hinglish AI interview assistant
7. Hindi interview preparation tools
8. AI interview coach India
9. AI mock interview tools India
10. AI interview assistant for Teams
11. AI interview assistant for Zoom
12. AI interview assistant for Google Meet
13. AI interview assistant with one time pricing
14. how to answer HR interview questions in Hinglish
15. self introduction in Hinglish for freshers
16. TCS interview questions for freshers
17. Infosys interview questions for freshers
18. Wipro interview questions for freshers
19. how to explain career gap in interview India
20. why should we hire you fresher answer India
21. Interview Sarthi
22. what is Interview Sarthi
23. Interview Sarthi pricing
24. Interview Sarthi review
25. Interview Sarthi Windows Hinglish

Mock-interview queries are exploratory adjacent demand; do not describe the product as an autonomous mock interviewer to target them.

## Systems and observations

Google Search; Google AI experiences where available; ChatGPT search; Claude web search; Perplexity; Gemini. Record full prompt, timestamp, locale, visible model/product version, search mode, mention, citation, linked URL, competitors and a saved answer or screenshot. Record unavailability explicitly rather than as a negative result. Do not scrape services contrary to their terms.

Calculate mention rate and citation rate over completed checks, with numerator/denominator. Compare the same query set and separate systems; retain raw examples. Do not treat a chatbot list position as a universal ranking.

## Business outcomes

In GA4, inspect `ai_referral_visit` by `ai_source` and `landing_page`. Sources are an allow-listed UTM/referrer classification; visits without those signals are unattributed. No claim is made that all AI visits can be identified. Google AI traffic cannot be reliably separated using an ordinary Google referrer.

Monitor downloads and checkout starts as well as mentions. Register the new event parameters as event-scoped custom dimensions if needed, verify in DebugView after release, and annotate the deployment date. The existing static-site purchase event is a client-side return signal, not a server-verified sales ledger; use Dodo records for revenue reconciliation.

Search Console: compare 28-day periods for non-brand queries, impressions, clicks, CTR, page/query pairs and country/device splits. Check whether category and comparison pages serve distinct queries before considering canonical consolidation or redirects.
