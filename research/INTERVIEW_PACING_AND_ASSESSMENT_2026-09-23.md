# Interview duration and assessment coverage

## Research

Reviewed 23 September 2026. This supplements the earlier conversational-flow
research; it does not claim that a short mock can replace an employer's assessment.

- [OPM, Structured Interviews: A Practical Guide](https://www.opm.gov/policy-data-oversight/assessment-and-selection/structured-interviews/guide.pdf),
  pages 5–14: derive competencies from the job, typically select four to six,
  combine past-behaviour and situational questions where appropriate, define
  scoring criteria and probes, and pilot the interview. Implication: coverage
  should mean relevant answer evidence, not the number of questions asked.
- [UK Government, structured interview techniques](https://www.gov.uk/government/publications/use-fair-and-structured-interview-techniques/use-fair-and-structured-interview-techniques):
  use job-relevant questions, consistent scoring criteria and concise wording,
  while allowing clarification. Implication: question type and role should drive
  scoring rather than how polished or fast a candidate sounds.
- [Google, Live API tool use](https://ai.google.dev/gemini-api/docs/live-api/tools)
  and [WebSocket reference](https://ai.google.dev/api/live): function calls use
  tool responses matched by call ID. Client-content messages can interrupt
  generation. Implication: provide clock information through a read-only tool
  at conversational decision points instead of periodically injecting a new
  user utterance into a candidate's answer.

The app remains an adaptive practice conversation, not a fully standardized or
validated hiring test: questions vary with the CV and answers. Numerical scores
are coaching feedback on the observed session, not hiring predictions.

## Root cause and implementation

Previously, the prompt described a sequence and approximate percentages, but the
model had no running clock. The app sent a wrap-up message at 60 seconds remaining,
yet nothing told the model not to complete its sequence earlier. That message
could also arrive while a candidate was answering.

The new `get_interview_progress` tool reads the same active-time calculation used
by the UI. Instructions require checking it before every spoken turn. The model
cannot set the remaining time through tool arguments. Closing is permitted only
in the last 10%, capped at 60 seconds, unless the candidate explicitly wants to
stop. The app still enforces the hard deadline. Reconnection time is excluded;
pass expiration remains a wall-clock limit. Entitlement caps can shorten a session.

The former unsolicited one-minute wrap-up text is removed. A late candidate answer
may leave less time for closing; do not interrupt it just to satisfy a schedule.
The tool's clock is deterministic; the model's compliance with calling it and
following its instructions still requires live evaluation.

## Ten-minute pacing example

These are our flexible product targets, not externally prescribed timings:

| Active time | Focus |
| --- | --- |
| 0:00–1:12 | Welcome and introduction |
| 1:12–3:12 | Project/work walkthrough and ownership |
| 3:12–6:48 | Role knowledge and practical problem-solving |
| 6:48–8:30 | Collaboration, judgment and lessons learned |
| 8:30–9:00 | Fill gaps in assessment evidence |
| 9:00–10:00 | Candidate questions and closing |

The stages are guidance at natural turn boundaries. Short answers create time for
additional relevant questions; longer answers can provide evidence in several
areas. Do not repeat answered questions or finish early because a list ran out.
The duration picker now explicitly offers ten minutes alongside existing options.

## Scoring and evidence

Six shared areas: communication, ownership, role knowledge, problem solving,
collaboration, judgment/learning. The report uses anchored 0–10 scores, with
`assessed`, `limited` and `not_assessed` states. Each scored area must cite existing,
nonempty candidate transcript turns. Invalid, interviewer-only or interrupted
evidence cannot support a score. Relevance of the evidence is judged by the model;
the client validates references, not semantic correctness.

Unassessed areas are null, not zero. The app computes the overall practice score
from scored areas only and displays coverage beside it. Scores with different
coverage should not be treated as interchangeable rankings. With no valid evidence
the app shows no numerical score. The report and text download both show the
areas, explanations and evidence references. Important skills beyond the voice
format should be recommended for later practice rather than claimed as assessed.

## Verification

Automated tests cover the full 600-second closing boundary, short entitlements,
pass expiry, clock reads after reconnects, cancelled requests, quiet-audio
preservation, evidence validation, averaging, partial coverage, report rendering
and escaping. Existing connection, transcript, audio and report tests also run.

Live acceptance cases still needed: short answers throughout a ten-minute session;
a long answer crossing 9:00; reconnect at mid-session; a fresher or nontechnical CV;
an early stop request; and an introduction-only session. Check that the model calls
the clock, continues meaningful assessment before 9:00, gives time to answer,
and does not assign role-knowledge scores without relevant evidence. No live
Gemini evaluation or new candidate recordings were used for automated validation.
