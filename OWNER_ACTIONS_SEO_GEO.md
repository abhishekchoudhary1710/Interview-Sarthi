# Owner actions and 90-day reach roadmap

The website changes are on a review branch until you merge and publish them. No social outreach or customer review requests were sent. Priority is based on verified site issues and public search samples, not private analytics.

## Release checks

1. Confirm desktop trial enforcement is 30 minutes per computer and Dodo product durations/device caps match `SITE_FACTS.md`. Check the weekly CTA correction against Dodo before release. Do not use a real paid order solely to test the website.
2. Confirm the Store listing is active and aligns on name, trial, Windows requirements, languages, support and privacy. Its existing URL is preserved, but Store contents were inaccessible during research.
3. Test current Google authorization-key compatibility in the installed app. The website repository cannot repair a desktop API incompatibility.
4. Review the branch and publish through the existing website deployment process. Inspect `facts.html`, sitemap responses and HTTP headers afterward.
5. Confirm Google Search Console sitemap submission; inspect the homepage, Facts and category/comparison URLs. Check Rich Results Test and rendered HTML. Keep existing verification and IndexNow configuration.
6. In GA4, verify `ai_referral_visit` and register `ai_source` / `landing_page` dimensions if needed. Check that receipt query values are absent. Reconcile purchases against Dodo; browser events are not a payment ledger.

## GitHub profile settings

README is provided. The repository description, official homepage and eight topics were updated after administrator access was verified. Applied description:

> Windows AI interview assistant for Indian job seekers, with resume-grounded assistance and English, Hindi and Hinglish support.

Homepage: `https://interviewsarthi.com/`

Topics: `ai-interview`, `interview-assistant`, `interview-copilot`, `hinglish`, `job-interview`, `windows`, `gemini`, `india`.

Only add a software license if you intend to grant its rights. The public marketing repository is not the desktop source.

## Days 1–14: establish a baseline

- Export Search Console query/page/country/device data for the previous 28 and 90 days. Separate branded from candidate-side category queries.
- Run the fixed 25-query sample in `TRACKING_QUERIES.md`, recording search mode and evidence. Do not cherry-pick favorable answers.
- Verify existing founder/company profiles. Link real, maintained profiles to the domain and add them to schema only after ownership is confirmed.
- Audit official employer sources for salary/process claims in the company guides before advertising them as current hiring information.
- Record the release date and any concurrent pricing or promotion changes so later attribution is interpretable.

## Days 15–45: create something worth referencing

- Run the pilot in `research/README.md` using consented or synthetic interview material. Publish no results before collection and review.
- Create one captioned, authentic Windows mock-call demonstration: setup, language switch, resume grounding, an error and its correction. Include a transcript and test conditions. Obtain permission from every visible/audible participant.
- Turn common support questions into improvements to existing help content. Add new pages only when Search Console or support evidence shows a distinct unanswered need.
- Offer interested reviewers a factual kit: Facts URL, official download, test protocol, limitations and contact. Let them choose conclusions; disclose any free access or sponsorship. Do not request a positive rating.

## Days 46–90: earn independent recognition and iterate

- Seek a small number of relevant career creators, placement communities and Windows/productivity reviewers. Tailor the relevance; avoid bulk link campaigns or unsolicited community spam.
- Publish one real benchmark report when data and permissions are ready, with raw data, method, limitations and correction history. Invite replication.
- Use a maintained LinkedIn/Product Hunt/YouTube presence if those channels fit your audience. Keep the same product definition and link to the canonical domain.
- Compare monthly mention/citation samples, non-brand impressions, qualified downloads and checkout starts. Investigate high-impression/low-CTR pages with their actual queries before changing titles again.
- If two URLs repeatedly serve the same intent, evaluate consolidation using traffic and backlink evidence. Do not redirect based on similar keywords alone.

## Decision rules

No numeric growth promise is set before a baseline exists. Prefer changes that improve successful setup and qualified downloads as well as reach. Stop a content experiment when it attracts the wrong audience or implies a capability the app lacks. Preserve useful Hinglish/company guidance; avoid multiplying generic company × city × role pages.

Outstanding access: Search Console, GA4 reporting, Microsoft Store publishing, installed desktop app, Dodo administration and owner-controlled social profiles. GitHub authentication was subsequently verified outside the network sandbox, with repository administrator access. See the implementation report for the final branch, review and metadata status.
