# Conversational mock interview design

Research reviewed: 23 September 2026.

## Evidence and limits

There is no universal interview script. A recruiter screen, hiring-manager
conversation and dedicated coding round assess different things. Prep Sarthi's
voice mock is best treated as a general role-focused conversation, not a complete
replacement for a coding exercise or a company's entire interview loop.

- [Indeed's interview template](https://www.indeed.com/career-advice/interviewing/interview-template)
  starts with interviewer introductions, an explanation of the process and a
  candidate introduction, then general and main questions, and candidate questions
  at the end. This supports making the opening explicit instead of letting CV
  details dominate the first turn.
- [Atlassian's engineering interview handbook](https://www.atlassian.com/company/careers/resources/interviewing/engineering)
  describes discussing past projects, collaboration, technical challenges and
  business purpose. Its design questions grow more or less challenging through
  follow-ups. This supports exploring an actual example before testing depth and
  adapting difficulty to the answer rather than to impressive resume keywords.
- [Microsoft's technical interviewing guidance](https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing)
  includes past experience, applied skills, role-related scenarios and problem
  solving. It encourages clarifying ambiguities and explaining a plan. Its coding
  assessment uses a coding tool, which this voice-only app does not provide.
- [Amazon's software development interview topics](https://www.amazon.jobs/content/en-gb/how-we-hire/interview-prep/software-development-topics)
  emphasizes applying knowledge rather than memorizing details, and distinguishes
  coding, design and behavioural preparation. This supports relevant practical
  questions rather than a rapid quiz across every technology on a CV.

## Product decisions

The order below and approximate proportions are our design synthesis, not a
claim that these employers all follow this exact sequence or timing.

1. Welcome, explain the flow, ask for a brief introduction, and wait (~15%).
2. Invite one project/work example, hear its purpose, then explore ownership
   in a separate turn if not already explained (~25%). Academic work, coursework
   and other responsibilities are valid alternatives.
3. Bridge to relevant fundamentals, then reasoning and trade-offs (~40%).
   Escalate only after demonstrated understanding; simplify when needed.
4. Discuss a challenge or collaboration if not already covered (~10%).
5. Reserve the final portion for candidate questions and a courteous close.

Short sessions cover fewer topics. Silence and audio checks do not count as an
introduction. Candidates may explicitly skip a stage. Reconnects preserve the
conversation. Timer notes take priority and stop new assessment topics near the
end. Missing CV/JD information is clarified rather than invented. Nontechnical
roles must not receive a forced software interview.

## Implementation and verification

`prep/app/interviewer.js` defines the ordered interview brief and shared opening,
reconnect and wrap-up notes. `prep/app/live.js` sends the explicit opening note
on fresh calls and the continuation note after transcript-based recovery;
native session resumption adds no new user turn. `prep/app/report.js` assesses
answers against their question type and flags limited evidence in short mocks.

`tests/mock_engine.test.mjs` covers opening-note delivery, retry before any speech,
reconnect and native resumption, closing-note delivery, and brief requirements
across short/long sessions and empty/student/senior CVs. These checks verify the
application contract; they do not establish that a generative voice model always
follows it. A live audio evaluation is still needed to judge model compliance.

Suggested live acceptance cases: a fresher with a college project; an experienced
candidate with advanced technologies on the CV; no project experience; a
nontechnical role; a brief answer or "I don't know"; Hinglish; an audio check before
the introduction; reconnect during the project; and a session ending early.
Check that each starts accessibly, follows the actual answers, asks one question
at a time and does not claim assessment of untested skills.
