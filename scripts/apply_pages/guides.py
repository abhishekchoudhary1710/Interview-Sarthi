"""The ApplySarthi guides hub and the guides under it."""
from ._shared import (ATS_BOARDS, BY_SOURCE, OPEN_JOBS, POSTED_7D, REVIEWED, SNAPSHOT, SOURCES,
                      TODAY, sarthi_handoff, table)

UP = '../../'

HUB = {
    'path': 'apply/guides/index.html',
    'trail': [('ApplySarthi', '/apply/'), ('Applying guides', '/apply/guides/')],
    'title': 'Guides to applying for jobs in India',
    'description': 'Practical guides to the applying half of a job search: Naukri automation, ATS resume formatting, and what to change when hundreds of applications produce no interview calls.',
    'h1': 'Guides to applying for jobs in India',
    'lead': 'The applying half of a job search, written for people doing it now. For the interview half, see the interview guides.',
    'meta': f'Maintained by the team that builds ApplySarthi · Last reviewed {REVIEWED}',
    'published': '2026-09-18', 'modified': TODAY,
    'cta_title': 'Stop retyping the same form',
    'cta_text': f'ApplySarthi matches {OPEN_JOBS} open jobs to your CV, rewrites the CV for the one you pick, and fills that employer’s form in your own Chrome.',
    'body': f"""
<h2>Start here</h2>
<ul>
<li><a href="{UP}apply/auto-apply-jobs-india.html"><b>Auto apply for jobs in India</b></a> &mdash; the three
kinds of tool sold under one name, why Naukri and Foundit break most of them, and eight questions to ask
before trusting one.</li>
<li><a href="{UP}apply/is-auto-apply-safe.html"><b>Is auto-applying safe?</b></a> &mdash; five real risks
ranked by how often they bite. The one people worry about is fourth.</li>
<li><a href="{UP}apply/best-auto-apply-tools-india.html"><b>The tools, compared</b></a> &mdash; six
products, published prices, and which reach Indian boards at all.</li>
</ul>

<h2>Applying</h2>
<ul>
<li><a href="naukri-auto-apply.html"><b>Auto-apply on Naukri: what works and what Naukri blocks</b></a>
&mdash; why server-side tools cannot touch it, what a browser extension can do, and the daily numbers
worth keeping to.</li>
<li><a href="ats-resume-format-india.html"><b>ATS resume format for Indian applications</b></a> &mdash;
what parsers actually fail on, the formatting that survives, and the myths worth ignoring.</li>
<li><a href="why-no-interview-calls.html"><b>You applied to 200 jobs and heard nothing</b></a> &mdash; the
five reasons, in the order they usually apply, and what to change first.</li>
</ul>

<h2>Data</h2>
<ul>
<li><a href="{UP}apply/job-application-statistics-india.html"><b>What {OPEN_JOBS} open jobs actually
contain</b></a> &mdash; only 19.9% state a salary and 41.3% name a city. First-party figures, free to
reuse with attribution.</li>
</ul>

<h2>Then the interview</h2>
<p>Applying is the half these guides cover. When the calls start, the
<a href="{UP}guides/">Interview Sarthi guides</a> take over: company-specific question sets for
<a href="{UP}guides/tcs-interview-questions-freshers.html">TCS</a>,
<a href="{UP}guides/infosys-interview-questions-freshers.html">Infosys</a>,
<a href="{UP}guides/wipro-interview-questions-freshers.html">Wipro</a>,
<a href="{UP}guides/accenture-interview-questions-freshers.html">Accenture</a> and others, plus the
answers that decide rounds &mdash; <a href="{UP}guides/why-should-we-hire-you.html">why should we hire
you</a>, <a href="{UP}guides/salary-expectation-answer.html">salary expectations</a> and
<a href="{UP}guides/reason-for-job-change.html">reason for job change</a>.</p>

{sarthi_handoff(UP)}
""",
    'faq': [
        ('What is the difference between ApplySarthi and Interview Sarthi?',
         'They cover the two halves of a job search. ApplySarthi handles applying — it finds open jobs, matches them to your CV, tailors the CV to each one and fills the employer’s application form in your own browser. Interview Sarthi handles what happens after: live, resume-grounded help during the interview itself, in English, Hindi or Hinglish. Both run on the same free Google Gemini key.'),
        ('Do I need to pay for ApplySarthi?',
         'Not during early access. ApplySarthi is free while it is being built out, and you supply your own Google Gemini API key, which Google issues at no cost. Paid plans are planned once early access ends. Interview Sarthi is a separate product with its own passes.'),
    ],
    'more': [
        ('What ApplySarthi does', f'{UP}apply/'),
        ('Auto-apply tools for India, compared', f'{UP}apply/best-auto-apply-tools-india.html'),
        ('Interview guides', f'{UP}guides/'),
        ('Get a free Gemini API key', f'{UP}free-gemini-api-key-guide.html'),
    ],
}

NAUKRI = {
    'path': 'apply/guides/naukri-auto-apply.html',
    'trail': [('ApplySarthi', '/apply/'), ('Applying guides', '/apply/guides/'),
              ('Auto-apply on Naukri', '/apply/guides/naukri-auto-apply.html')],
    'title': 'Auto-apply on Naukri: what works and what Naukri blocks',
    'description': 'Why server-side auto-apply tools cannot reach Naukri at all, what a browser-based tool can do instead, the daily numbers worth keeping to, and how Naukri’s own recommendations differ from applying.',
    'h1': 'Auto-apply on Naukri: what works and what it blocks',
    'lead': 'Naukri is the largest source of jobs in India and the one most auto-apply products quietly skip. Here is the technical reason, and what is actually possible.',
    'meta': f'Reviewed {REVIEWED} · Written by the team that builds ApplySarthi',
    'published': '2026-09-18', 'modified': TODAY,
    'cta_title': 'Naukri, Foundit and Shine included',
    'cta_text': f'ApplySarthi reaches the Indian boards most tools skip, alongside {ATS_BOARDS} company career pages. Free in early access.',
    'body': f"""
<h2>Why most tools cannot reach Naukri</h2>
<p>Naukri blocks two things that nearly every automation product depends on: <b>plain HTTP requests</b> and
<b>headless browsers</b>. A tool that runs on a vendor&rsquo;s server and fetches pages the ordinary way
gets nothing usable back. A tool that runs a browser with no visible window gets detected and refused.</p>
<p>The only approach that works is driving a real Chromium window the way a person drives one, and reading
the responses the page&rsquo;s own scripts request as they arrive. That is slower, needs a display, and
cannot be run cheaply at scale on a server &mdash; which is precisely why products marketed on volume
leave Naukri out.</p>
<div class="box"><p>When a product advertises &ldquo;30+ job boards&rdquo; without listing them, assume
Naukri is not among them until the company names it. The same applies to Foundit, which blocks in the same
way.</p></div>

<h2>What is actually possible</h2>
<p>Three different things get called auto-apply on Naukri, and only two of them exist.</p>
<ul>
<li><b>Reading open jobs.</b> Entirely workable through a real browser session. ApplySarthi currently holds
6,293 open Naukri postings, collected this way.</li>
<li><b>Filling the application form.</b> Workable, in your own browser, using the Naukri session you are
already signed in to. Your password never has to leave your computer.</li>
<li><b>Bulk submission from a server.</b> Not workable, and not something to buy from anyone claiming
otherwise.</li>
</ul>

<h2>Naukri&rsquo;s recommended jobs are not the same as matching</h2>
<p>Naukri suggests roles based on the profile you filled in on Naukri &mdash; your stated title, your
stated skills, your stated experience. That is a good keyword match against what you typed, which is not
the same as a match against what your CV actually says.</p>
<p>The gap shows up most for people changing function or returning after a break, where the profile
fields describe the last job rather than the next one. Matching against the CV text itself, as a whole
document, tends to surface roles the profile-based suggestions miss.</p>

<h2>The daily number worth keeping to</h2>
<p>Sites that need a login are the ones with something to lose. Naukri, LinkedIn, Indeed and Shine all cap
how much activity an account may generate, and a restriction lands on the account you need during the
search itself.</p>
<p>The practical split: keep the count modest on login-gated boards, and put volume into company career
pages, which have no account attached and no limit to trip. Of the {OPEN_JOBS} open jobs ApplySarthi
tracks, company ATS boards hold the largest share precisely because they can be collected without an
account at all.</p>
{table(['Where', 'Account needed?', 'Sensible daily volume'], [
  ('Company career pages (Greenhouse, Lever, Ashby, Workday&hellip;)', 'No', 'As many as genuinely fit'),
  ('Naukri, Shine, Indeed', 'Yes', 'Modest; these are accounts you need'),
  ('LinkedIn', 'Yes', 'Smallest of all; the strictest limits of the group'),
])}

<h2>Applying on Naukri without retyping everything</h2>
<ol>
<li>Sign in to Naukri yourself, in your own Chrome, the ordinary way. Once.</li>
<li>Keep your Naukri profile current anyway &mdash; recruiters search it directly, independently of your
applications.</li>
<li>Use a tool that fills the form on the page in front of you, so you can read it before it goes.</li>
<li>Tailor the CV per role. A Naukri application carries whichever CV you attach, and the attached file is
what a recruiter opens.</li>
<li>Check the first three applications by hand before trusting the fourth.</li>
</ol>

{sarthi_handoff(UP)}
""",
    'faq': [
        ('Can you auto-apply on Naukri?',
         'You can automate filling the application form, in your own browser, using a Naukri session you signed in to yourself. You cannot run bulk submission from a server: Naukri blocks plain HTTP requests and headless browsers, so vendor-hosted tools cannot reach it at all. Any product promising server-side bulk applying on Naukri is describing something that does not work.'),
        ('Will Naukri ban my account for using an extension?',
         'Naukri limits account activity rather than banning outright for form-filling help, and a browser extension that fills the form in front of you is much closer to you typing than to a bot. The behaviour that attracts restrictions is high-volume automated submission. Keep your daily numbers modest on any site where you hold an account.'),
        ('Why do auto-apply tools not list Naukri?',
         'Because reaching it requires driving a real browser window with a visible display, which cannot be run cheaply at scale on a server. Products built around a high daily submission rate depend on server-side automation, so Naukri and Foundit are excluded by their architecture, not by choice. Most simply do not mention it.'),
        ('Is Naukri or LinkedIn better for applying in India?',
         'Both, for different reasons. In the current ApplySarthi snapshot Naukri held 6,293 open postings and LinkedIn 8,110, but the overlap is small and the employer mix differs, with Naukri stronger in Indian services firms and LinkedIn stronger in multinationals and startups. Company career pages outweigh either individually.'),
    ],
    'more': [
        ('Auto apply for jobs in India: how the tools work', f'{UP}apply/auto-apply-jobs-india.html'),
        ('Is auto-applying safe?', f'{UP}apply/is-auto-apply-safe.html'),
        ('ATS resume format for Indian applications', 'ats-resume-format-india.html'),
        ('You applied to 200 jobs and heard nothing', 'why-no-interview-calls.html'),
    ],
}


NOCALLS = {
    'path': 'apply/guides/why-no-interview-calls.html',
    'trail': [('ApplySarthi', '/apply/'), ('Applying guides', '/apply/guides/'),
              ('No interview calls', '/apply/guides/why-no-interview-calls.html')],
    'title': 'You applied to 200 jobs and heard nothing. What to change',
    'description': 'Five reasons applications go unanswered, in the order they usually apply: stale postings, one generic CV, roles that never fit, an unparseable file, and applying only where competition is highest.',
    'h1': 'You applied to 200 jobs and heard nothing',
    'lead': 'Almost always one of five things, and they are not equally likely. Work down this list in order rather than sending another hundred.',
    'meta': f'Reviewed {REVIEWED} · Written by the team that builds ApplySarthi',
    'published': '2026-09-18', 'modified': TODAY,
    'cta_title': 'Aim the next twenty instead of sending another two hundred',
    'cta_text': f'ApplySarthi ranks {OPEN_JOBS} open jobs against your actual CV and rewrites it for the ones that fit. {POSTED_7D} of them were posted this week.',
    'body': f"""
<p>Two hundred applications and silence feels like a verdict on you. It is usually a verdict on the
applications. Here are the five causes in the order we see them, with the check for each.</p>

<h2>1. A large share of them were already closed</h2>
<p>This is the most common and the least suspected. Job postings stay visible long after hiring stops.
Only <b>5.7%</b> of Indian postings carry a closing date at all &mdash; a job is open until it silently
disappears, and aggregator sites keep showing it for weeks afterwards.</p>
<p>Applying into a closed posting produces exactly the silence you are seeing, and no feedback that
anything was wrong.</p>
<div class="box"><p><b>The check:</b> take ten applications you sent more than a fortnight ago and look for
the posting on the employer&rsquo;s own careers page, not the aggregator. If several are gone, freshness
is your problem, not your CV. <b>The fix:</b> filter hard on posting date. It is present on 99.5% of
postings, which makes it the one filter that can be trusted. {POSTED_7D} of the {OPEN_JOBS} jobs currently
open were posted within seven days &mdash; there is no shortage of fresh ones.</p></div>

<h2>2. The same CV went to all two hundred</h2>
<p>A single CV is written for the average of every job you want, which means it is aimed at none of them.
The first pass on an application &mdash; whether a parser or a person &mdash; is looking for the words in
the posting. A CV that uses your words rather than theirs reads as a near miss.</p>
<p>This does not mean lying, and it does not mean a fresh CV from scratch each time. It means the same
experience described in the vocabulary of the role in front of you.</p>
<div class="box"><p><b>The check:</b> put your CV and one posting you were rejected for side by side.
Underline every skill and responsibility in the posting, then find each one in your CV. If you are hunting,
so was the recruiter, and they stopped sooner.</p></div>

<h2>3. The roles did not actually fit</h2>
<p>Applying to everything with a familiar job title produces a pile of applications for roles wanting five
years when you have one, or a specialisation you do not have. Volume tools make this worse, because their
matching is usually title-and-keyword based.</p>
<p>The hard part is that <b>19.3%</b> of postings state years of experience and <b>18.3%</b> list skills in
any structured way, so you often cannot filter for fit &mdash; you have to read the description, which is
present on 96.7% of postings and is where the real requirements live.</p>

<h2>4. The file could not be read</h2>
<p>Less common than the internet suggests, but real. A CV laid out in columns, or with the contact details
in a header, or exported as an image, can arrive at the other end scrambled or half-empty. You will never
be told.</p>
<p>The <a href="ats-resume-format-india.html">ATS formatting guide</a> covers what actually breaks. The
short version: single column, real text, ordinary section headings, PDF exported from a text document.</p>

<h2>5. Everything went to the three most crowded places</h2>
<p>Most people apply where applying is easiest, which is where every other applicant already is. Of the
{OPEN_JOBS} jobs ApplySarthi currently tracks, company career boards hold the largest share &mdash;
Greenhouse, Lever, Ashby, Workday and the large in-house boards together outweigh any single job board.
Those applications go directly into the employer&rsquo;s own system, usually with far fewer applicants per
posting.</p>
{table(['Source', 'Open jobs'], [(s, n) for s, n in BY_SOURCE[:8]])}
<p class="note">Snapshot {SNAPSHOT}. Full breakdown on the
<a href="{UP}apply/job-application-statistics-india.html">open-jobs dataset page</a>.</p>

<h2>What to do this week</h2>
<ol>
<li>Stop sending. Nothing improves while the current approach continues.</li>
<li>Filter to postings from the last seven days only.</li>
<li>Pick twenty that genuinely fit, judged from the description rather than the title.</li>
<li>Rewrite your CV for each one &mdash; same facts, their vocabulary.</li>
<li>Send those twenty. Compare the reply rate against your last two hundred.</li>
</ol>
<p>Twenty aimed applications beating two hundred generic ones is the ordinary result, not the optimistic
one.</p>

{sarthi_handoff(UP)}
""",
    'faq': [
        ('Why am I not getting interview calls after applying to many jobs?',
         'The most common cause is applying into postings that had already closed — only 5.7% of Indian job postings carry a closing date, so listings stay visible long after hiring stops. After that, in order: one generic CV sent everywhere, roles that did not genuinely fit, a CV file the employer’s system could not parse, and applying only through the most crowded channels.'),
        ('How many job applications is normal before getting an interview?',
         'There is no dependable published figure, and any specific ratio you see quoted is usually someone’s sample presented as a law. What is measurable is the direction: applications aimed at roles that fit, with a CV using the posting’s own vocabulary, are answered at a far higher rate than generic ones. Twenty aimed applications commonly outperform two hundred identical ones.'),
        ('Should I apply on the job board or the company website?',
         'The company’s own careers page, where you have the choice. It goes straight into the employer’s applicant tracking system, and those postings typically attract fewer applicants than the same role on a large aggregator. In the current ApplySarthi snapshot, company career boards collectively hold more open roles than any single job board.'),
        ('Does rewriting my CV for each job really matter?',
         'Yes, and it is the highest-value change after filtering for freshness. The first pass on an application looks for the language of the posting. Describing the same real experience in the role’s own vocabulary is the difference between a near miss and a match — which is rewording, not inventing, and the distinction matters at interview.'),
    ],
    'more': [
        ('ATS resume format for Indian applications', 'ats-resume-format-india.html'),
        ('What 60,975 open jobs actually contain', f'{UP}apply/job-application-statistics-india.html'),
        ('Auto-apply on Naukri', 'naukri-auto-apply.html'),
        ('Interview guides, for when the calls start', f'{UP}guides/'),
    ],
}

ATS = {
    'path': 'apply/guides/ats-resume-format-india.html',
    'trail': [('ApplySarthi', '/apply/'), ('Applying guides', '/apply/guides/'),
              ('ATS resume format', '/apply/guides/ats-resume-format-india.html')],
    'title': 'ATS resume format for Indian job applications',
    'description': 'What applicant tracking systems actually fail to read, the formatting that survives every parser, the Indian CV conventions worth dropping, and the ATS myths that waste your time.',
    'h1': 'ATS resume format for Indian job applications',
    'lead': 'Applicant tracking systems are parsers, not judges. Most advice about them is about the wrong thing.',
    'meta': f'Reviewed {REVIEWED} · Written by the team that builds ApplySarthi',
    'published': '2026-09-18', 'modified': TODAY,
    'cta_title': 'One CV in, a version per job out',
    'cta_text': 'ApplySarthi rewrites your CV for each job using only what your CV already says, and renders it as a clean single-column PDF.',
    'body': f"""
<h2>What an ATS actually does</h2>
<p>An applicant tracking system stores applications and lets a recruiter search them. When your CV
arrives it is parsed into fields &mdash; name, contact details, employers, dates, education, skills. If
parsing works, a human reads your CV. If it half-works, you exist in the system as a partial record that
does not match the searches a recruiter runs.</p>
<p>There is no score being computed, and nothing is auto-rejecting you for lacking a keyword. The realistic
failure is quieter: you are in the database, and you do not come back in the search.</p>

<h2>What genuinely breaks parsing</h2>
{table(['Problem', 'What happens', 'Do this instead'], [
  ('Two-column layouts', 'Text is read across the columns, interleaving two sections into nonsense.',
   'One column, top to bottom. This is the single biggest fix.'),
  ('Contact details in a page header or footer', 'Some parsers never read that region, so you arrive with no phone number.',
   'Put name, phone and email in the body of the first page.'),
  ('A CV exported as an image, or scanned', 'No text at all to extract.',
   'Export to PDF from a text document. Selectable text is the test.'),
  ('Tables used for layout', 'Cell order decides reading order, which rarely matches visual order.',
   'Plain paragraphs and bullet lists.'),
  ('Icons or symbols instead of labels', 'A telephone glyph is not the word "Phone" to a parser.',
   'Label fields in words.'),
  ('Invented section headings', '"My Journey" is not recognised as work history.',
   'Experience, Education, Skills, Projects. Ordinary words.'),
  ('Dates written inconsistently', 'Employment gaps are computed wrongly or the role is dropped.',
   'One format throughout, e.g. "Mar 2023 &ndash; Present".'),
])}

<h2>Indian CV conventions worth reconsidering</h2>
<p>Several habits standard on Indian CVs are neutral for parsing but cost you space on the first page,
which is the part anyone reads.</p>
<ul>
<li><b>A photograph.</b> Not required for most roles and takes first-page space. Some multinational
employers prefer CVs without one.</li>
<li><b>Date of birth, marital status, father&rsquo;s name, nationality.</b> Conventional here, unnecessary
for nearly every private-sector role, and they push your actual experience down the page.</li>
<li><b>A declaration and signature line.</b> A convention from paper applications; parsers ignore it and
recruiters do not look for it.</li>
<li><b>&ldquo;Curriculum Vitae&rdquo; as the title.</b> The document is evidently a CV. Use your name.</li>
<li><b>Percentage and class for every exam back to Class 10.</b> Keep it for freshers where it is asked
for; trim it once you have work experience.</li>
</ul>
<p>None of this is about pleasing a machine. It is about what occupies the first screen a person sees.</p>

<h2>Myths worth ignoring</h2>
<ul>
<li><b>&ldquo;ATS rejects 75% of CVs automatically.&rdquo;</b> Widely repeated, not supported by anything
checkable. Systems store and search; recruiters reject.</li>
<li><b>&ldquo;Use white text to hide keywords.&rdquo;</b> Parsers read hidden text, recruiters see it in the
extracted view, and it reads as deception.</li>
<li><b>&ldquo;.docx always beats PDF.&rdquo;</b> Both parse well when generated from text. An image-based PDF
fails; a text-based one does not.</li>
<li><b>&ldquo;There is one ATS-friendly template.&rdquo;</b> Any clean single-column layout with ordinary
headings works. Templates sold on this promise are selling formatting you can do yourself.</li>
</ul>

<h2>Matching the posting without inventing anything</h2>
<p>Tailoring means describing your real work in the posting&rsquo;s vocabulary. If a posting says
&ldquo;stakeholder management&rdquo; and your CV says &ldquo;coordinated with clients and internal
teams&rdquo;, those are the same experience and the posting&rsquo;s phrasing is the one being searched
for.</p>
<div class="box warn"><p>The line not to cross: a tool that adds a figure, a date, an employer or a
qualification your CV does not contain has created something you cannot defend in an interview. Check the
first few tailored versions against your original line by line. ApplySarthi discards any rewritten line
that introduces a number absent from your source CV and keeps your original wording instead.</p></div>

<h2>A five-minute check before you send</h2>
<ol>
<li>Open the PDF and try to select the text. If you cannot, it is an image.</li>
<li>Copy the whole document and paste it into a plain text editor. Read what comes out &mdash; that is
roughly what the parser sees.</li>
<li>Confirm your phone number and email are in that pasted text.</li>
<li>Check the section headings survived, and in order.</li>
<li>Check that dates read consistently and no role lost its dates.</li>
</ol>
<p>That paste test catches nearly every real parsing failure, and takes less time than reading another
article about templates.</p>

{sarthi_handoff(UP)}
""",
    'faq': [
        ('What resume format is best for ATS in India?',
         'A single-column layout, in PDF exported from a text document, with ordinary section headings (Experience, Education, Skills), contact details in the body rather than a page header, and one consistent date format. Two-column layouts are the most common real cause of parsing failure, because the text is read across the columns rather than down them.'),
        ('Should an Indian resume include a photo and date of birth?',
         'Usually not for private-sector roles. Neither harms parsing, but both consume space on the first page, which is the part a recruiter actually reads. The same applies to marital status, father’s name and the declaration line — conventional on Indian CVs, and rarely of use to the person deciding whether to call you.'),
        ('Is PDF or Word better for job applications?',
         'Either works, provided the file contains real text. A PDF exported from a word processor parses as well as a .docx. What fails is a PDF made from an image or a scan, because there is no text to extract. Test by opening the PDF and trying to select the text with your cursor.'),
        ('Do applicant tracking systems really reject 75% of resumes?',
         'No, and the figure has no checkable source behind it. An ATS stores applications and lets recruiters search them; it does not score or reject. The realistic failure is that a badly parsed CV becomes a partial record that does not come back in the searches a recruiter runs, so no human ever sees it.'),
    ],
    'more': [
        ('You applied to 200 jobs and heard nothing', 'why-no-interview-calls.html'),
        ('What 60,975 open jobs actually contain', f'{UP}apply/job-application-statistics-india.html'),
        ('Auto-apply on Naukri', 'naukri-auto-apply.html'),
        ('Auto apply for jobs in India', f'{UP}apply/auto-apply-jobs-india.html'),
    ],
}

PAGES = [HUB, NAUKRI, NOCALLS, ATS]
