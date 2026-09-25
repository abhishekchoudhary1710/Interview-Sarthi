"""The four ApplySarthi pages that stand on their own: the category page, the comparison hub,
the safety page and the dataset."""
from ._shared import (APPLY_URL, ATS_BOARDS, BY_CITY, BY_SOURCE, COVERAGE, DISCLOSURE, METHOD,
                      OPEN_JOBS, POSTED_7D, REVIEWED, SNAPSHOT, SOURCES, TODAY, sarthi_handoff, table)

CATEGORY = {
    'path': 'apply/auto-apply-jobs-india.html',
    'trail': [('ApplySarthi', '/apply/'), ('Auto apply for jobs in India', '/apply/auto-apply-jobs-india.html')],
    'title': 'Auto apply for jobs in India: how the tools actually work',
    'description': 'The three kinds of auto-apply tool, why Naukri and Foundit break most of them, what a 1,500-a-day claim really costs you, and eight questions to ask before trusting one with your name.',
    'h1': 'Auto apply for jobs in India',
    'lead': 'Three different things are sold under one name. Knowing which one you are buying decides whether it helps you or quietly damages your reputation.',
    'meta': f'Reviewed {REVIEWED} · Written by the team that builds ApplySarthi',
    'published': '2026-09-18', 'modified': TODAY,
    'cta_title': 'See what is open right now',
    'cta_text': f'ApplySarthi is tracking {OPEN_JOBS} open jobs from {SOURCES} sources, {POSTED_7D} of them posted in the last seven days. Always free.',
    'body': f"""
<h2>The three kinds of tool</h2>
<p>Search for auto-apply and you will find products that do quite different things. They are not
competitors so much as different answers to different problems.</p>

{table(['Kind', 'What it does', 'What it costs you'], [
  ('<b>Autofill</b>', 'Fills the form on a page you opened, then stops. You read it and press submit.',
   'Nothing but the reading. The safest kind, and the least impressive in a demo.'),
  ('<b>Bulk auto-submit</b>', 'Opens listings and submits without you seeing them, at a set daily rate.',
   'Volume with no aim. Every application carries your name whether or not it made sense.'),
  ('<b>Match, then fill</b>', 'Ranks open jobs against your CV first, tailors the CV, then fills the form for that job.',
   'Slower per application. The work moves from clicking to choosing.'),
])}

<p>The middle kind is what most people picture when they hear &ldquo;auto apply&rdquo;, and it is the
kind that produces the complaints. A tool that submits 150 applications a day on your behalf is not
applying for 150 jobs; it is putting your name on 150 forms. Recruiters at the receiving end see the
difference before you do.</p>

<h2>Why Indian job boards break most of these tools</h2>
<p>Almost every auto-apply product sold internationally covers the same four places: Greenhouse, Indeed,
ZipRecruiter and Dice. Those are reasonable defaults in the United States. In India they miss where the
jobs actually are.</p>
<p>There is an engineering reason as well as a market one. <b>Naukri and Foundit block plain HTTP
requests and headless browsers.</b> A tool that fetches pages on a server cannot read them at all. The
only way in is a real browser window, driven like a person would drive it, reading the page&rsquo;s own
API responses as they arrive. Most products are not built that way, so they quietly leave the two
largest Indian boards out and do not mention it on the pricing page.</p>
<p>For scale, here is where the {OPEN_JOBS} jobs ApplySarthi currently has open actually came from:</p>
{table(['Source', 'Open jobs'], [(s, n) for s, n in BY_SOURCE])}
<p class="note">Snapshot taken {SNAPSHOT}. Full field-level breakdown on the
<a href="job-application-statistics-india.html">open-jobs dataset page</a>.</p>
<p>Naukri, Shine and Internshala together account for more open postings than Greenhouse. A tool that
cannot reach them is not covering the Indian market, whatever its homepage says.</p>

<h2>What &ldquo;1,500 applications a day&rdquo; actually buys</h2>
<p>Daily-limit numbers are the headline feature of the bulk tools, and they are real limits &mdash; the
products do submit that many forms. Three things are left out.</p>
<ul>
<li><b>The platforms have their own limits.</b> LinkedIn caps how many applications an account may send
in a day, and the cap is far below the numbers advertised. Hitting it repeatedly is not a neutral event
for your account.</li>
<li><b>One employer, many applications.</b> Applicant tracking systems deduplicate by email. Twenty
applications to twenty roles at one company do not read as enthusiasm at the other end; they read as a
script, and most systems show the recruiter all twenty on one screen.</li>
<li><b>The same CV every time.</b> Volume tools reuse one file. That is what makes the volume possible,
and it is also why the response rate per application falls as the count rises.</li>
</ul>
<p>The honest way to read a daily limit is as a measure of how little the tool looks at each job.</p>

<h2>Eight questions worth asking before you trust one</h2>
<ol>
<li><b>Does it press submit?</b> If yes, find the setting that turns that off and check it exists.</li>
<li><b>Where does it run?</b> In your own browser with your own logins, or on someone else&rsquo;s server
with your password?</li>
<li><b>Does your job-board password reach the vendor?</b> It should never need to.</li>
<li><b>Which Indian boards does it actually cover?</b> Ask for the list. &ldquo;30+ boards&rdquo; is not a
list.</li>
<li><b>What does it do to your CV?</b> Rewording is fine. Inventing a number, a date or an employer is
not, and it is the failure mode that ends interviews badly.</li>
<li><b>Can you see every application before it goes?</b> If not, you cannot correct anything.</li>
<li><b>Whose AI quota is it using?</b> A shared quota means your throughput depends on other users.</li>
<li><b>What happens to your data if you stop paying?</b> Ask before you start, not after.</li>
</ol>

<h2>Where ApplySarthi sits</h2>
<p>ApplySarthi is the third kind. It collects open jobs from {SOURCES} sources and {ATS_BOARDS} company
career boards, ranks them against your CV, rewrites the CV for the job you picked, and fills that
employer&rsquo;s form in your own Chrome. Then it stops and waits for you. You read the form and press
the site&rsquo;s own submit button.</p>
<p>Two design choices follow from that, and both are checkable rather than promised:</p>
<ul>
<li><b>Nothing is invented on your CV.</b> Names, employers, dates, degrees and figures are copied from
your document. If a rewritten line introduces a number your CV does not contain, that line is thrown away
and your original wording is kept.</li>
<li><b>Your passwords stay with you.</b> Sites that need an account &mdash; LinkedIn, Naukri, Indeed,
Shine &mdash; you sign in to once yourself, in your own browser, the ordinary way. ApplySarthi works
through the session already sitting there.</li>
</ul>
<p>There is an Autopilot switch that will press submit for you, off by default, and only when the form
has nothing left needing a human. We would rather explain that honestly than pretend the option does not
exist.</p>
<p>It is always free. You bring your own Google Gemini API key, which Google issues free,
so your usage is never rationed against anyone else&rsquo;s. There is a
<a href="../free-gemini-api-key-guide.html">step-by-step guide to getting one</a>.</p>

{sarthi_handoff()}
""",
    'faq': [
        ('Is auto-applying to jobs allowed in India?',
         'No Indian law prevents you from using software to help you fill in a job application. What binds you is each site’s own terms of use, and those differ: some job boards permit browser extensions that assist you, and most prohibit scripted bulk submission from their servers. The safe position is a tool that fills the form in your own browser and leaves the submit button to you, because that is you applying, with help.'),
        ('Which job sites can actually be automated in India?',
         'Company career pages built on Greenhouse, Lever, Ashby, Workday, SmartRecruiters and Oracle HCM are the most reliable, because their forms are public and stable. Naukri, Foundit, LinkedIn, Indeed and Shine need you to be signed in, and Naukri and Foundit additionally refuse plain HTTP requests and headless browsers, so they only work through a real browser window.'),
        ('Do recruiters reject applications they think were automated?',
         'They reject applications that do not match the role, which is what most bulk tools produce. There is no reliable way for a recruiter to detect that a form was filled by software. What they can see is a CV that does not fit the job, the same generic file across several roles, or twenty applications from one candidate in a single day.'),
        ('How many jobs should I apply to in a day?',
         'Fewer than the tools advertise. A smaller number of applications to roles that genuinely match your CV, each with a CV rewritten for that job, outperforms hundreds of identical submissions. The limit worth respecting is your own ability to answer for every application you sent.'),
    ],
    'more': [
        ('Auto-apply tools for India, compared', 'best-auto-apply-tools-india.html'),
        ('Is auto-applying safe? What can actually go wrong', 'is-auto-apply-safe.html'),
        ('What 60,975 open jobs in India actually contain', 'job-application-statistics-india.html'),
        ('Auto-apply on Naukri: what works and what it blocks', 'guides/naukri-auto-apply.html'),
        ('You applied to 200 jobs and heard nothing', 'guides/why-no-interview-calls.html'),
    ],
}


COMPARE = {
    'path': 'apply/best-auto-apply-tools-india.html',
    'trail': [('ApplySarthi', '/apply/'), ('Auto-apply tools compared', '/apply/best-auto-apply-tools-india.html')],
    'title': 'Auto-apply job tools for India, compared (September 2026)',
    'description': 'ApplySarthi, LazyApply, Simplify, LoopCV, Jobright and AIApply side by side: published prices, whether each one presses submit, and which actually reach Naukri, Shine and Internshala.',
    'h1': 'Auto-apply job tools for India, compared',
    'lead': 'Six products, what each one publishes about itself, and the question the pricing pages avoid: which Indian job boards does it really reach?',
    'meta': f'Public sources reviewed {REVIEWED} · Prices that are not published are marked unknown',
    'published': '2026-09-18', 'modified': TODAY,
    'cta_title': 'Try the one built for Indian boards',
    'cta_text': f'ApplySarthi covers Naukri, Foundit, Shine, Internshala, Wellfound, LinkedIn and Indeed alongside {ATS_BOARDS} company career boards. Always free.',
    'body': f"""
{DISCLOSURE}

<h2>The comparison</h2>
{table(['Product', 'Published price', 'Presses submit?', 'Reaches Naukri / Shine / Internshala?'], [
  ('<b>ApplySarthi</b>', 'Always free; you bring your own Gemini key',
   'No, unless you switch Autopilot on', '<b>Yes</b> &mdash; plus Foundit, Wellfound, LinkedIn, Indeed'),
  ('<a href="vs-lazyapply.html">LazyApply</a>', '$99, $149 or $999 a year',
   'Yes, by design', 'No &mdash; Greenhouse, Dice, Indeed, ZipRecruiter'),
  ('<a href="vs-simplify-jobs.html">Simplify</a>', 'Free tier; Simplify+ price not published publicly',
   'No &mdash; autofill only', 'Not stated; positions itself around company career sites'),
  ('<a href="vs-loopcv.html">LoopCV</a>', 'From &euro;9.99 a month',
   'Yes, and sends follow-up email', 'Not stated; &ldquo;30+ job boards&rdquo; is not itemised'),
  ('<a href="vs-jobright-ai.html">Jobright AI</a>', 'Not published on a public page',
   'Autofill, with an agent on paid tiers', 'No &mdash; United States focus'),
  ('<a href="vs-aiapply.html">AIApply</a>', 'Not published; auto-apply sold as credit packs',
   'Yes, on credits', 'Not stated'),
])}
<p class="note">Every figure above was read from the product&rsquo;s own site on {REVIEWED} and is linked
on that product&rsquo;s page below. Where a company does not publish prices publicly we have written
&ldquo;not published&rdquo; rather than repeat a third-party number we could not confirm. Features change;
check the current page before paying.</p>

<h2>The column that decides it for most people in India</h2>
<p>Price is the column everyone reads first and the one that matters least here, because the products are
not covering the same market. Of the {OPEN_JOBS} open jobs ApplySarthi is currently tracking, Naukri,
Shine and Internshala together hold more than Greenhouse does. A tool whose board list is Greenhouse,
Dice, Indeed and ZipRecruiter is a good tool aimed somewhere else.</p>
<p>The reason is technical rather than commercial, and it is covered in the
<a href="auto-apply-jobs-india.html">category guide</a>: Naukri and Foundit refuse plain HTTP requests and
headless browsers, so reaching them requires driving a real browser window. Products built to run on a
server cannot do it at all.</p>

<h2>The other column worth reading twice</h2>
<p>&ldquo;Presses submit&rdquo; splits the six into two genuinely different products. LazyApply, LoopCV and
AIApply send applications for you; that is the feature. Simplify and ApplySarthi fill the form and stop.
Jobright sits in between.</p>
<p>Neither is wrong, but they fail differently. A tool that submits for you fails by sending something you
would not have sent. A tool that stops fails by being slower. Decide which failure you can live with before
you compare prices, because after that the choice makes itself.</p>

<h2>Read each one in full</h2>
<ul>
<li><a href="vs-lazyapply.html">ApplySarthi vs LazyApply</a> &mdash; the volume case, and what 1,500 a day means</li>
<li><a href="vs-simplify-jobs.html">ApplySarthi vs Simplify</a> &mdash; the closest in philosophy; different coverage</li>
<li><a href="vs-loopcv.html">ApplySarthi vs LoopCV</a> &mdash; auto-apply plus employer follow-up email</li>
<li><a href="vs-jobright-ai.html">ApplySarthi vs Jobright AI</a> &mdash; strong matching, United States market</li>
<li><a href="vs-aiapply.html">ApplySarthi vs AIApply</a> &mdash; a whole suite, sold on credits</li>
</ul>

<h2>What we did not test</h2>
<p>We have not run the other five products against a controlled set of applications, measured their
response rates, or verified their behaviour on Indian sites ourselves. Everything above is what each
company publishes. A blank in a row means we could not confirm it from a public page, not that the
feature is missing. If you are choosing between two of these, sign up for both free tiers and apply to
the same five jobs through each.</p>

{sarthi_handoff()}
""",
    'faq': [
        ('Which auto-apply tool is best for jobs in India?',
         'For Indian job boards specifically, the deciding question is whether the tool reaches Naukri, Foundit, Shine and Internshala, and most of the internationally marketed tools do not. ApplySarthi covers those alongside 754 company career boards and is always free. If you are applying mainly to United States roles, the comparison changes entirely and Jobright or Simplify may suit you better.'),
        ('Is there a free auto-apply tool?',
         'Simplify’s autofill tier is free and LoopCV has a free plan. ApplySarthi is always free, and there is no paid plan. Browsing jobs and your first tailored CV need no key; further tailoring uses your own Google Gemini API key, which Google issues at no cost.'),
        ('Do any of these work on Naukri?',
         'Of the six compared here, ApplySarthi is the one that states Naukri coverage explicitly. Naukri blocks plain HTTP requests and headless browsers, so a product has to drive a real browser window to reach it, and most do not. Treat an unitemised claim of "30+ job boards" as not including Naukri unless the company names it.'),
        ('Will paying more get me more interviews?',
         'Nothing in these products changes whether you fit a role. What they change is how many roles you reach and how well each application is aimed. Spending more on a higher daily submission limit buys volume, which is the part of the equation least connected to getting a call back.'),
    ],
    'more': [
        ('Auto apply for jobs in India: how the tools work', 'auto-apply-jobs-india.html'),
        ('Is auto-applying safe? What can actually go wrong', 'is-auto-apply-safe.html'),
        ('What 60,975 open jobs in India actually contain', 'job-application-statistics-india.html'),
        ('ATS resume format for Indian applications', 'guides/ats-resume-format-india.html'),
    ],
}


SAFETY = {
    'path': 'apply/is-auto-apply-safe.html',
    'trail': [('ApplySarthi', '/apply/'), ('Is auto-applying safe?', '/apply/is-auto-apply-safe.html')],
    'title': 'Is auto-applying to jobs safe? What can actually go wrong',
    'description': 'Account limits, recruiter perception, duplicate applications inside one ATS, where your job-board password goes, and the CV-fabrication risk nobody warns you about.',
    'h1': 'Is auto-applying to jobs safe?',
    'lead': 'Five real risks, ranked by how often they actually bite. The one most people worry about is not the one that hurts them.',
    'meta': f'Reviewed {REVIEWED} · Written by the team that builds ApplySarthi',
    'published': '2026-09-18', 'modified': TODAY,
    'cta_title': 'Apply with the submit button still yours',
    'cta_text': 'ApplySarthi fills the employer’s form in your own Chrome and stops. You read it and press submit. Always free.',
    'body': f"""
<p>&ldquo;Will I get banned?&rdquo; is the question people ask. It is a reasonable worry and it is fourth
on this list. The risks that actually cost people interviews are duller and further up.</p>

<h2>1. A CV that quietly invents things</h2>
<p>This is the one that ends badly, and almost nobody warns you about it. Any tool that rewrites your CV
for each job is running a language model over your work history, and language models fill gaps. A tool
that turns &ldquo;improved reporting turnaround&rdquo; into &ldquo;reduced reporting turnaround by
40%&rdquo; has handed you a number you cannot defend. You will not notice, because it reads well. You
will notice in the interview.</p>
<div class="box warn"><p><b>What to check:</b> take one CV, run it through the tool for three different
jobs, and compare the three outputs against your original line by line. Every figure, date, employer,
job title and degree must be traceable to something you actually wrote. If a number appeared from
nowhere, stop using the tool.</p></div>
<p>ApplySarthi handles this by construction: a rewritten line that introduces a figure the source CV does
not contain is discarded and your original wording is kept. That is a rule in the code rather than an
instruction to the model, because instructions to a model are advisory.</p>

<h2>2. Twenty applications landing on one recruiter&rsquo;s screen</h2>
<p>Applicant tracking systems deduplicate candidates by email address. Apply to twenty roles at one
company and the recruiter opens one profile with twenty applications attached, timestamped within a few
minutes of each other. Nothing is banned, nothing is flagged, and you have told them exactly how much
thought went into each one.</p>
<p>This is the normal output of a bulk tool set to a high daily rate, and it is invisible from your side.
You see twenty applications sent. They see one candidate who did not read anything.</p>

<h2>3. A generic CV against a specific job</h2>
<p>Volume tools reuse one file, because reusing one file is what makes the volume possible. The trade is
rarely stated: response rate per application falls as the count rises, and the total number of interviews
can fall with it. Sending more can get you fewer calls.</p>

<h2>4. Platform limits and account restrictions</h2>
<p>Now the ban question. Job boards cap how many applications an account may send in a day. LinkedIn is
the strictest of the ones most people use. The caps sit well below the daily numbers auto-apply products
advertise, so a tool configured at its maximum will hit them.</p>
<p>What follows is usually a temporary restriction rather than a deleted account, but it lands on the
account you need, at the time you need it. The practical rule: keep the number small on sites that need a
login, and spend your volume on company career pages, which have no such limit and no account to lose.</p>

<h2>5. Where your password ends up</h2>
<p>Ranked last because it is the easiest to avoid entirely, and the most serious when it goes wrong. Some
services ask for your job-board username and password so their servers can log in as you. That hands a
third party durable access to an account holding your full employment history and contact details.</p>
<div class="box"><p><b>The safe shape:</b> a tool that runs in your own browser and uses the session you
already signed in to. You log in to Naukri or LinkedIn yourself, once, the ordinary way. The tool never
sees the password because it never needs to. ApplySarthi works this way; so does any browser extension
that fills forms on the page in front of you.</p></div>

<h2>A short checklist</h2>
<ol>
<li>Compare the tailored CV against your original, line by line, at least once.</li>
<li>Keep applications to any one employer to the roles you would genuinely take.</li>
<li>Keep the daily count low on sites that need a login; use career pages for volume.</li>
<li>Never give a job-application service your job-board password.</li>
<li>Read the form before it is submitted &mdash; which requires a tool that lets you.</li>
</ol>

{sarthi_handoff()}
""",
    'faq': [
        ('Can I get banned from LinkedIn for auto-applying?',
         'LinkedIn limits how many applications an account can send per day and restricts accounts that repeatedly exceed it. In practice that means a temporary restriction rather than permanent removal, but it applies to the account you need for your search. Keep the daily number small on LinkedIn specifically, and put your volume into company career pages, which have no equivalent limit.'),
        ('Can recruiters tell an application was filled in by AI?',
         'Not from the form itself. There is no marker in a submitted application that identifies the software that filled it. What recruiters do notice is a CV that does not match the role, the same generic document across several different jobs, or many applications from one person arriving at once — all of which are consequences of high-volume tools rather than of automation as such.'),
        ('Is it safe to give an auto-apply tool my Naukri password?',
         'No, and you should not need to. A tool that fills forms in your own browser uses the session you are already signed in to, so the password never leaves your computer. Treat a request for your job-board credentials as a reason to choose something else, because it gives a third party lasting access to an account holding your full employment history.'),
        ('Does ApplySarthi submit applications by itself?',
         'No, not unless you deliberately switch Autopilot on. By default it fills the employer’s form in your own Chrome and stops, so you read it, complete anything it left, solve any CAPTCHA and press the site’s own submit button. Autopilot is off by default and, when enabled, only acts when the form has nothing left that needs a person.'),
    ],
    'more': [
        ('Auto apply for jobs in India: how the tools work', 'auto-apply-jobs-india.html'),
        ('Auto-apply tools for India, compared', 'best-auto-apply-tools-india.html'),
        ('Auto-apply on Naukri: what works and what it blocks', 'guides/naukri-auto-apply.html'),
        ('You applied to 200 jobs and heard nothing', 'guides/why-no-interview-calls.html'),
    ],
}


_cov_rows = [(f, pct, note) for f, pct, note in COVERAGE]

DATA = {
    'path': 'apply/job-application-statistics-india.html',
    'trail': [('ApplySarthi', '/apply/'), ('Open-jobs dataset', '/apply/job-application-statistics-india.html')],
    'title': f'What {OPEN_JOBS} open jobs in India actually contain',
    'description': f'A field-level look at {OPEN_JOBS} open Indian job postings collected from {SOURCES} sources on {SNAPSHOT}: only 19.9% state a salary, 41.3% name a city, and Bengaluru holds more than the next three cities together.',
    'h1': f'What {OPEN_JOBS} open jobs in India actually contain',
    'lead': 'Job-market reports usually count postings. This one counts what is written inside them, because that is what decides whether you can search properly.',
    'meta': f'First-party dataset · Snapshot taken {SNAPSHOT} · Free to reuse with attribution',
    'published': '2026-09-18', 'modified': TODAY,
    'cta_title': 'Search the same jobs yourself',
    'cta_text': f'The dataset on this page is the live one ApplySarthi matches against: {OPEN_JOBS} open jobs, {POSTED_7D} posted in the last week.',
    'body': f"""
<p>Everyone publishes counts of how many jobs are open. Very little is published about what those
postings actually say, which is the part that decides whether a filter works, whether a matcher can read
the role, and whether you can tell what a job pays before you apply.</p>
<p>This is a snapshot of every posting ApplySarthi held open on {SNAPSHOT}, taken from its own database.
It is published because we have not found the equivalent anywhere else.</p>

<h2>The headline finding: four postings in five say nothing about pay</h2>
<p>Salary appears in <b>19.9%</b> of open postings. Not a range, not a band &mdash; any mention of pay at
all. Years of experience fares barely better at 19.3%, and a structured skills list appears on 18.3%.</p>
<p>The practical consequence is that salary and experience are useless as primary search filters in India.
Filtering on either silently discards about 80% of what is open, including most of the jobs you would
have wanted. Any product that offers them as headline filters is hiding most of the market from you.</p>

<h2>Field coverage across {OPEN_JOBS} open postings</h2>
{table(['Field', 'Present on', 'Notes'], _cov_rows)}

<h2>Where the jobs come from</h2>
<p>By source, the same snapshot. Company career boards &mdash; Greenhouse, Lever, Ashby, Workday, Oracle
HCM and the large in-house boards &mdash; together outweigh any single job board.</p>
{table(['Source', 'Open jobs'], [(s, n) for s, n in BY_SOURCE])}

<h2>Where the jobs are</h2>
<p>Among the 41.3% of postings where a city could be resolved at all, the concentration is steeper than
most people expect. <b>Bengaluru alone holds more open roles than Delhi NCR, Hyderabad and Mumbai
combined.</b></p>
{table(['City', 'Open jobs'], [(c, n) for c, n in BY_CITY])}
<p>Read the long tail carefully before drawing conclusions about it. Ahmedabad, Kolkata, Kochi and
Chandigarh look small here partly because they are smaller markets and partly because postings outside
the big six more often carry a state or a bare &ldquo;India&rdquo; instead of a city, and so fall into the
58.7% with no resolvable city at all.</p>

<h2>Freshness</h2>
<p><b>{POSTED_7D} of the {OPEN_JOBS} open postings &mdash; about 44% &mdash; were posted within the last
seven days.</b> Posting date is present on 99.5% of rows, which makes it the one field reliable enough to
filter on hard. A closing date, by contrast, appears on 5.7%: in practice an Indian job posting is open
until it disappears, and nobody tells you when that will be.</p>

<h2>Method, and what this is not</h2>
{METHOD}
<p>Counts are of open postings, not of vacancies or hires; one vacancy advertised on three sites appears
once after deduplication but a genuinely duplicated posting may survive. Coverage percentages measure
whether a field was present and non-empty, not whether it was accurate. Sources are weighted by what is
technically reachable, so this over-represents employers using public ATS boards and under-represents
those advertising only on sites that block collection. It is a large sample of the Indian online job
market, not a census of it, and it describes one day.</p>

<div class="box"><p><b>Reusing these figures.</b> You are welcome to quote or chart anything on this page,
including in commercial work, with attribution to
&ldquo;ApplySarthi, {SNAPSHOT}&rdquo; and a link to this page. If you want a cut we have not published
&mdash; by function, seniority, or over time &mdash; write to us and we will see whether the data supports
it.</p></div>

{sarthi_handoff()}
""",
    'faq': [
        ('What percentage of Indian job postings mention salary?',
         f'19.9% of the {OPEN_JOBS} open postings in this snapshot mention pay in any form, taken on {SNAPSHOT} across {SOURCES} sources and {ATS_BOARDS} company career boards. Four postings in five say nothing about salary at all, which is why filtering a job search by salary in India discards most of what is actually open.'),
        ('Which Indian city has the most open jobs?',
         'Bengaluru, by a wide margin. In this snapshot it held 10,632 open postings with a resolvable city, more than Delhi NCR (3,474), Hyderabad (3,254) and Mumbai (2,163) combined. Note that a city could only be resolved for 41.3% of postings overall.'),
        ('How many job postings are fresh at any one time?',
         f'About 44%. Of {OPEN_JOBS} postings open on {SNAPSHOT}, {POSTED_7D} had been posted within the previous seven days. Posting date is available on 99.5% of rows, making freshness the most dependable filter available on Indian job data.'),
        ('Can I cite this data?',
         'Yes, including commercially. Attribute it to "ApplySarthi, ' + SNAPSHOT + '" with a link to this page. The underlying figures were read directly from the database that ApplySarthi matches CVs against, and the method and limitations are described above so you can judge whether the sample suits your purpose.'),
    ],
    'more': [
        ('Auto apply for jobs in India: how the tools work', 'auto-apply-jobs-india.html'),
        ('ATS resume format for Indian applications', 'guides/ats-resume-format-india.html'),
        ('You applied to 200 jobs and heard nothing', 'guides/why-no-interview-calls.html'),
        ('Auto-apply tools for India, compared', 'best-auto-apply-tools-india.html'),
    ],
}

PAGES = [CATEGORY, COMPARE, SAFETY, DATA]
