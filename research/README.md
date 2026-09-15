# Interview assistant benchmark methodology

Status: protocol and empty data template only. No participants recruited, app runs measured or comparative results published.

## Research question

How accurately do assistants preserve meaning in English/Hinglish questions and ground suggested answers in a supplied resume, under a documented Windows mock-call setup?

## Proposed pilot

Use 20 consented or synthetic spoken prompts: English, Hindi, mixed Hinglish, names/numbers, technical terms, resume follow-ups and questions whose answers are absent from the resume. These are planned sample sizes, not completed measurements. Use fictional resumes, never an applicant's private history without informed permission.

Publish the exact prompts, audio files, transcripts and resume fixtures only when you own or have permission to distribute them. Include speaker/accent coverage and avoid describing a small convenience sample as representative of India.

## Reproducible setup

Record OS build, CPU/RAM, app version, model and settings, billing tier, meeting platform/version, input route, headset, connection quality, region and UTC timestamp. Use the same audio files and resume fixtures where the products support them. Disclose differences such as live microphone versus file input; do not disguise them as controlled comparisons.

Run each test at least five times per product in the proposed pilot. Randomize product order. Keep errors, timeouts and retries in the dataset. Predetermine a timeout and retry policy before collection. Record warm/cold starts separately. Use a monotonic clock or frame timestamps from a consented recording.

## Metrics

- Transcription latency: question end to final transcript; milliseconds. Distinguish partial and final text.
- Answer latency: question end to first useful answer text and separately to final answer. Report median, p95, sample count and timeout rate; do not average away failures.
- English word error rate: `(substitutions + deletions + insertions) / reference words`. Keep the reference transcript and alignment method.
- Hinglish quality: predeclare romanization normalization. Report token errors separately from meaning preservation and critical entities (names, numbers, negation, technical terms). WER alone can penalize valid spelling variants.
- Resume grounding: reviewers mark every personal assertion supported, contradicted or absent from the fixture. Report unsupported assertions / all personal assertions. State how zero-assertion answers are handled.
- Answer usefulness: two reviewers score relevance and technical correctness using a published rubric; blind product names where possible and report disagreements.
- Compatibility: distinguish observed runs from a vendor's documented claim. A platform logo is not a successful test.
- Pricing: report currency, actual upfront total, term, quotas, renewal and date; do not equate annualized rates with monthly checkout totals.

## Dataset and quality controls

`benchmark-template.csv` contains column names only. One row per metric per run; use a shared run ID to associate multiple metrics. For failures, leave `value` blank and record `status`, error and timeout. Do not use zero latency for a failed run. Use ISO dates and explicit units. Retain raw observations separately from cleaned data.

Publish eligibility/exclusion rules, planned versus achieved sample counts and missingness. A second reviewer should verify calculations from raw rows. Include a source ledger for documentation-only observations, with review date and archived evidence where redistribution permits it.

## Publication gate

Before a public results page: confirm consent and redistribution rights, remove personal information, collect the planned data, verify calculations, disclose ownership of Interview Sarthi, publish limitations and allow corrections. Do not claim independent research, national representativeness, success in hiring, or guaranteed answer accuracy.

Publish a methods version, CSV, reproducible analysis code and change history alongside real results. Keep methodological updates separate from new observations. Until then, link readers to the public practice checklist and source-review page without pretending they are benchmark findings.
