# Dynamic CV/JD assessment and interviewing without a JD

Research reviewed 23 September 2026. This extends the existing pacing design.

## Research and product interpretation

- [OPM job analysis](https://www.opm.gov/policy-data-oversight/assessment-and-selection/job-analysis/)
  connects job tasks to the competencies needed to perform them. We therefore
  derive assessment targets from the JD, using the CV to select examples rather
  than treating every CV keyword as a job requirement.
- [OPM structured interview guide](https://www.opm.gov/policy-data-oversight/assessment-and-selection/structured-interviews/guide.pdf)
  describes preparing competencies, questions, rating criteria and follow-ups,
  and piloting the process. Our criteria are prepared before answers arrive.
- [CIPD selection methods](https://www.cipd.org/uk/knowledge/factsheets/selection-factsheet/)
  supports relevant, consistent assessment criteria and complementary assessment
  methods. Our adaptive practice interview is not a validated standardized hiring
  test; it does not claim comparability between candidates who receive different
  questions or have different coverage.
- [Greenhouse scorecards](https://support.greenhouse.io/hc/en-us/articles/360003500291-Best-practices-Creating-a-scorecard)
  connects role outcomes to testable attributes and distributes coverage across
  interviews. We expose unresolved essentials and deferred requirements rather
  than hiding them in a single average.
- [Atlassian engineering interviews](https://www.atlassian.com/company/careers/resources/interviewing/engineering)
  describes follow-ups that become more or less challenging as answers develop.
  Our model chooses the next question dynamically from current evidence and time;
  the planned questions are examples, not a mandatory script or order.
- [O*NET content model](https://www.onetcenter.org/content.html)
  distinguishes occupational tasks, knowledge, skills and experience. It informs
  how we organize a role baseline when there is no JD. We do not call the O*NET
  API or claim the model's inferred criteria are an official O*NET standard.
- [OPM work samples](https://www.opm.gov/policy-data-oversight/assessment-and-selection/other-assessment-methods/work-samples-and-simulations/)
  distinguishes discussion from performing representative work. Requirements
  needing executed code, artifacts or observable tasks remain limited in a
  voice-only interview, with a next practical assessment identified.

## Three supported modes

1. **CV plus JD.** The LLM creates job-specific requirements, JD source quotes,
   CV matches/gaps, priority, sample questions, optional follow-ups and concrete
   weak/adequate/strong criteria. The client validates source excerpts. Unsupported
   JD priorities become explicitly inferred; missing CV evidence becomes unknown.
2. **CV plus a chosen role, without a JD.** The user names the target role and
   selects its level before preparation. The LLM uses common role tasks and
   transferable skills as provisional targets. For career changers, the chosen
   future role takes precedence over the old occupation. All requirements are
   inferred, not employer-confirmed. A planner response changing the chosen role
   or level is rejected. Freshers can use coursework/personal/volunteer examples.
3. **General CV practice.** The user explicitly chooses this when there is no
   target role. Questions explore actual background, contributions, relevant
   fundamentals, reasoning and learning. Sparse/mixed CVs call for clarification
   after the introduction. The model must not invent an occupation, seniority or
   missing job skills to penalize. Reports do not claim employer suitability.

Pasting/uploading a JD hides the no-JD controls. Removing it restores them.
Returning users retain their chosen practice mode, role and level. Role/level
validation also runs on the Start path so returning visitors cannot bypass it.

## Preparation, dynamic interviewing and scoring

Preparation uses an additional text-generation request on the candidate's Gemini
key, before the live socket and practice clock start. A visible preparation state
can be cancelled. Invalid model output can use the existing fallback model;
failure offers retry instead of silently substituting an unrelated interview.
The entitlement is refreshed after preparation. Microphone frames are not sent
to the interviewer until the call starts.

The prepared plan has at most twelve nonduplicative requirements, with any
omissions explicitly listed. The LLM chooses questions, follow-ups, clarification,
difficulty and transitions from actual answers and remaining time. Timing phases
are guides, not fixed locks after the introduction/project overview are complete.
The closing window and hard stop still follow the user-selected duration.

The clock tool accepts optional requirement/answer-quote coverage updates. The
client accepts only known requirement IDs with quotes present in candidate
transcript turns, excluding interrupted answers and interviewer speech. Covered
means enough evidence to assess, not necessarily a strong answer. Duplicate tool
calls do not manufacture extra turns. Gaps and permitted follow-ups are returned
as options, not an enforced next question. Coverage survives reconnects.

The report independently scores actual transcript evidence against the prepared
criteria. It cannot change requirement priorities after seeing the answers.
Our product weighting is essential=2, preferred/inferred=1, disclosed in reports;
this is not an externally validated hiring formula. Unassessed requirements have
null scores. Missing essential evidence and practical assessments stay visible
even when other scores are high. The UI and download show target, coverage,
uncertainties, explanations, source requirements and supporting answer references.

## Verification and remaining limits

Automated tests exercise plan validation, source references, malformed/fallback
responses, both no-JD modes, chosen-role protection, career-change context,
coverage updates, repeated follow-ups, cancellation, preparation timing, transport
tool calls, weighted scoring, practical-task limits and report schema integration.
Backend, sales and accounting fixtures check data routing, not live model quality.

The LLM still judges semantic relevance, priority interpretation and answer
quality. Exact-source/quote checks establish that text exists; they do not prove
an achievement happened or an answer demonstrates the claimed skill. No live
Gemini session or candidate credentials were used in automated tests.

Live acceptance evaluation remains necessary for a fresher, a senior candidate,
a career changer without a JD, a mixed/sparse CV in general mode, a nontechnical
JD, a weak but fluent answer, and a candidate giving short answers. Check model
adherence, coverage, end timing and scores against a human-reviewed rubric.
