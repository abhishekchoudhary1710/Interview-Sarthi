"""ApplySarthi against the five auto-apply products people compare it with.

Every competitor fact carries the public page it was read from, on the date in REVIEWED. Where a
company does not publish something, the page says so instead of repeating an unverified figure.
"""
from ._shared import (APPLY_URL, ATS_BOARDS, DISCLOSURE, OPEN_JOBS, REVIEWED, SOURCES, TODAY,
                      sarthi_handoff, table)

UP = '../'

TESTING = """
<h2>How to test both properly</h2>
<ol>
<li>Pick five real postings you would genuinely accept, and use the same five in both tools.</li>
<li>Start from the same CV file in each.</li>
<li>Read every tailored CV against your original, line by line. Any figure, date, employer or
qualification that was not in your document is a reason to stop.</li>
<li>Stop before submitting in whichever tool lets you, and compare the two filled forms field by field.</li>
<li>Count fields left blank or filled wrongly, not how impressive the demonstration felt.</li>
</ol>
"""


def page(slug, name, title, description, lead, verified, differ, decide, unverified, faq, siblings):
    return {
        'path': f'apply/vs-{slug}.html',
        'trail': [('ApplySarthi', '/apply/'), ('Auto-apply tools compared', '/apply/best-auto-apply-tools-india.html'),
                  (f'vs {name}', f'/apply/vs-{slug}.html')],
        'title': title,
        'description': description,
        'h1': f'ApplySarthi vs {name}',
        'lead': lead,
        'meta': f'Public sources reviewed {REVIEWED} · Not a hands-on benchmark',
        'published': '2026-09-18', 'modified': TODAY,
        'cta_title': 'Try ApplySarthi on your own CV',
        'cta_text': f'Free in early access, with {OPEN_JOBS} open jobs from {SOURCES} sources and {ATS_BOARDS} company career boards.',
        'body': f"""{DISCLOSURE}
<h2>What we could verify</h2>
{verified}
<h2>Where they genuinely differ</h2>
{differ}
<h2>What should decide it</h2>
{decide}
{TESTING}
<h2>What we could not verify</h2>
{unverified}
<p>A gap here is a gap in public information, not a claim that a feature is missing. Check the
company&rsquo;s current pages before paying for anything.</p>
{sarthi_handoff(UP)}
""",
        'faq': faq,
        'more': siblings,
    }


LAZYAPPLY = page(
    'lazyapply', 'LazyApply',
    'ApplySarthi vs LazyApply: volume against aim',
    'LazyApply submits up to 1,500 applications a day across four job sites for $99–$999 a year. ApplySarthi matches jobs to your CV across 21 sources and stops at the submit button. Which suits you.',
    'One sends as many applications as possible. The other sends fewer, aimed. The choice is really about which failure you can live with.',
    verified=f"""
<p><b>LazyApply</b> publishes its plans openly: <b>$99 a year</b> for 15 applications a day and one resume
profile, <b>$149 a year</b> for 150 a day and five profiles, and <b>$999 a year</b> for 1,500 a day and
twenty profiles. It describes applying automatically across <b>Greenhouse, Dice, Indeed and
ZipRecruiter</b>, with referral emails and a tracking dashboard.
(<a href="https://lazyapply.com/pricing" rel="nofollow">Official pricing page</a>, read {REVIEWED}.)</p>
<p><b>ApplySarthi</b> is free in early access. It collects open jobs from {SOURCES} sources and
{ATS_BOARDS} company career boards, ranks them against your CV, rewrites the CV for the job you pick and
fills that employer&rsquo;s form in your own Chrome. You press submit. You supply a free Google Gemini
key, so your usage is not rationed against other users. See the
<a href="{UP}facts.html">product facts</a>.</p>""",
    differ="""
""" + table(['', 'ApplySarthi', 'LazyApply'], [
        ('Price', 'Free in early access', '$99 / $149 / $999 per year'),
        ('Daily applications', 'As many as genuinely fit', '15 / 150 / 1,500 by plan'),
        ('Presses submit', 'No, unless you switch Autopilot on', 'Yes &mdash; that is the product'),
        ('Indian job boards', 'Naukri, Foundit, Shine, Internshala, Wellfound, LinkedIn, Indeed',
         'Greenhouse, Dice, Indeed, ZipRecruiter'),
        ('CV per job', 'Rewritten per job, figures never invented', 'Resume profiles you set up in advance'),
        ('You see it before it goes', 'Always, by default', 'No &mdash; submission is automatic'),
    ]),
    decide="""
<p>If your search is mostly United States postings on Greenhouse, Dice, Indeed and ZipRecruiter, and you
want reach above all, LazyApply is built for exactly that and states its limits plainly.</p>
<p>If you are applying in India, the board list is the problem before price is. Naukri, Shine and
Internshala together hold more open postings in our current snapshot than Greenhouse does, and none of
them appear on LazyApply&rsquo;s list. The technical reason is covered in the
<a href="auto-apply-jobs-india.html">category guide</a>.</p>
<p>The second question is what a high daily rate does to you. Applicant tracking systems deduplicate by
email, so twenty applications to one employer arrive on one screen. Platform limits exist on any site
needing a login. The <a href="is-auto-apply-safe.html">safety page</a> covers both in detail.</p>""",
    unverified="""
<p>We have not run LazyApply, measured its fill accuracy, tested its behaviour on Indian sites, or
compared response rates between the two products. We have not verified whether its daily limits interact
with each platform&rsquo;s own caps. Its pricing page was legible and current when we read it; everything
above comes from that page.</p>""",
    faq=[
        ('Is LazyApply worth it?',
         'It depends entirely on where you are applying. LazyApply publishes clear plans at $99, $149 and $999 a year for 15, 150 and 1,500 applications a day, and it delivers reach on Greenhouse, Dice, Indeed and ZipRecruiter. For a search centred on Indian job boards it does not list Naukri, Foundit, Shine or Internshala, which is a coverage gap no price fixes.'),
        ('Does LazyApply work on Naukri?',
         'Its pricing page lists Greenhouse, Dice, Indeed and ZipRecruiter, and does not mention Naukri. Naukri blocks plain HTTP requests and headless browsers, so reaching it requires driving a real browser window — an approach that does not fit a product built around high-volume server-side submission.'),
        ('What is the cheapest way to auto-apply to jobs in India?',
         'ApplySarthi is free during early access, with the qualification that you supply your own Google Gemini API key, which Google issues at no cost. Among paid products, LoopCV publishes plans from €9.99 a month and LazyApply from $99 a year, though neither states coverage of the main Indian job boards.'),
    ],
    siblings=[
        ('Auto-apply tools for India, compared', 'best-auto-apply-tools-india.html'),
        ('ApplySarthi vs Simplify', 'vs-simplify-jobs.html'),
        ('ApplySarthi vs LoopCV', 'vs-loopcv.html'),
        ('Is auto-applying safe?', 'is-auto-apply-safe.html'),
    ])

SIMPLIFY = page(
    'simplify-jobs', 'Simplify',
    'ApplySarthi vs Simplify: the closest match, different coverage',
    'Simplify autofills applications on 100,000+ company career sites and stops at submit — the same philosophy as ApplySarthi. Where they differ is which job sources they reach and what happens to your CV.',
    'The two products that agree on the important thing: software fills the form, you press submit. They disagree about where the jobs come from.',
    verified=f"""
<p><b>Simplify</b> describes its Copilot extension as autofilling &ldquo;job applications on 100,000+
company career sites in one click&rdquo; and saving every application to a tracker. The page describes
autofill, and does not describe automatic submission. Copilot is presented as free.
(<a href="https://simplify.jobs/copilot" rel="nofollow">Official Copilot page</a>, read {REVIEWED}.)</p>
<p>Simplify does not publish a public pricing page for its paid tier, so we are not quoting a figure for
it. Third-party reviews cite monthly and weekly prices; we could not confirm those from Simplify itself
and have left them out rather than repeat them.</p>
<p><b>ApplySarthi</b> is free in early access, covers {SOURCES} sources including Naukri, Foundit, Shine,
Internshala, Wellfound, LinkedIn and Indeed alongside {ATS_BOARDS} company career boards, ranks them
against your CV and rewrites the CV per job. It also stops at the submit button.</p>""",
    differ="""
""" + table(['', 'ApplySarthi', 'Simplify'], [
        ('Presses submit', 'No, unless you switch Autopilot on', 'No &mdash; autofill only'),
        ('Price', 'Free in early access', 'Free tier; paid tier price not published publicly'),
        ('Finds jobs for you', 'Yes &mdash; ranked against your CV', 'Job board and matches within the product'),
        ('Indian job boards', 'Naukri, Foundit, Shine, Internshala, Wellfound, LinkedIn, Indeed',
         'Not stated; positioned around company career sites'),
        ('CV rewritten per job', 'Yes, with invented figures discarded', 'AI resume and cover letter on the paid tier'),
        ('Whose AI quota', 'Your own free Google Gemini key', 'The vendor&rsquo;s, within your plan'),
    ]),
    decide="""
<p>These two are philosophically the same product and it is worth saying so plainly: both believe the
person applying should read the form before it is sent. Simplify&rsquo;s extension is mature, widely used
and free, and if your applications are mostly on company career sites it will serve you well.</p>
<p>The difference that matters is where the jobs come from. Simplify is built around company career sites,
which in India is roughly the share our snapshot attributes to Greenhouse, Lever, Ashby and Workday
combined &mdash; substantial, but it leaves out the Indian boards where a large part of the market
advertises.</p>
<p>The second difference is whose AI quota is being spent. ApplySarthi runs on a Google Gemini key you
obtain yourself and free, which is why CV tailoring is not held behind a paid tier. The trade is that you
do a one-time setup; there is a
<a href="../free-gemini-api-key-guide.html">guide with pictures</a>.</p>""",
    unverified="""
<p>We have not verified Simplify&rsquo;s paid pricing, because it is not on a public page. We have not
tested its autofill accuracy, its coverage of Indian job boards, or how its resume tailoring treats figures
that do not appear in your source CV. Its free tier is straightforward to try alongside ApplySarthi, and
we would encourage that over taking either of our words for it.</p>""",
    faq=[
        ('Is Simplify Jobs free?',
         'The Copilot autofill extension is presented as free on Simplify’s own page, and that is the part most people use. Simplify also has a paid tier for AI resume and cover letter generation, but the company does not publish its price on a public page, so any figure you see quoted elsewhere is second-hand.'),
        ('Does Simplify auto-submit applications?',
         'No. Its own page describes autofilling applications in one click and saving them to a tracker; it does not describe automatic submission. That is the same position ApplySarthi takes by default — the software fills the form, you read it and press the site’s own submit button.'),
        ('What is the best Simplify alternative for India?',
         'The gap to close is Indian job board coverage, since Simplify is built around company career sites. ApplySarthi covers Naukri, Foundit, Shine, Internshala, Wellfound, LinkedIn and Indeed alongside 754 company career boards, and is free during early access. The two work the same way at the form itself, so switching costs little.'),
    ],
    siblings=[
        ('Auto-apply tools for India, compared', 'best-auto-apply-tools-india.html'),
        ('ApplySarthi vs LazyApply', 'vs-lazyapply.html'),
        ('ApplySarthi vs Jobright AI', 'vs-jobright-ai.html'),
        ('ATS resume format for Indian applications', 'guides/ats-resume-format-india.html'),
    ])


LOOPCV = page(
    'loopcv', 'LoopCV',
    'ApplySarthi vs LoopCV: auto-apply and outbound email',
    'LoopCV scans 30+ job boards, applies automatically and emails employers follow-ups, from €9.99 a month. ApplySarthi matches against 21 sources including Naukri and stops at the submit button.',
    'LoopCV will apply and then email the employer on your behalf. Whether that helps you depends a great deal on what it sends.',
    verified=f"""
<p><b>LoopCV</b> states that paid plans start from <b>&euro;9.99 a month</b>, that it scans
<b>30+ job boards daily</b>, and that it uploads your CV, sets preferences and then automatically finds
and applies to relevant jobs, sends follow-up emails and tracks results. For sites requiring a login it
offers a browser extension so credentials are not shared.
(<a href="https://www.loopcv.pro/pricing" rel="nofollow">Official pricing page</a>, read {REVIEWED}.)</p>
<p>The 30+ boards are not itemised on that page, so we cannot tell you whether Naukri, Foundit, Shine or
Internshala are among them.</p>
<p><b>ApplySarthi</b> is free in early access and names its {SOURCES} sources openly, including all four of
those, plus {ATS_BOARDS} company career boards.</p>""",
    differ="""
""" + table(['', 'ApplySarthi', 'LoopCV'], [
        ('Price', 'Free in early access', 'From &euro;9.99 a month'),
        ('Presses submit', 'No, unless you switch Autopilot on', 'Yes'),
        ('Emails employers for you', 'No', 'Yes &mdash; follow-up emails are a stated feature'),
        ('Job sources named publicly', f'Yes &mdash; all {SOURCES} listed', '&ldquo;30+ job boards&rdquo;, not itemised'),
        ('Login-gated sites', 'Your own browser session; password never leaves it', 'Browser extension, credentials not shared'),
        ('CV per job', 'Rewritten per job, invented figures discarded', 'CV uploaded and used across applications'),
    ]),
    decide="""
<p>The outbound email is the real difference, and it cuts both ways. A well-judged follow-up to a hiring
manager genuinely helps. An automated one, sent at volume, in a template, to an employer who did not ask,
is the sort of thing that gets a domain marked as spam and your name with it. Before enabling that feature
anywhere, read exactly what it sends and to whom.</p>
<p>On coverage, LoopCV is credible on international boards and does the sensible thing for login-gated
sites by keeping credentials out of its servers. What we cannot tell you from its public pages is whether
its 30+ boards include the Indian ones. If you are applying in India, ask them to name the list before
paying, and treat an unitemised claim as excluding Naukri and Foundit, which block the kind of automation
a server-side product depends on.</p>
<p>On price, &euro;9.99 a month is about &#8377;950 at the time of writing, recurring. ApplySarthi is free
during early access, with paid plans planned afterwards.</p>""",
    unverified="""
<p>We have not verified which specific job boards LoopCV covers, its fill accuracy, the content of its
follow-up emails, or how its free plan differs in practice from the paid ones. Currency conversions move;
check the current price in your own currency. We have not tested its browser extension.</p>""",
    faq=[
        ('Does LoopCV work for jobs in India?',
         'LoopCV states that it scans 30+ job boards daily but does not itemise them on its pricing page, so we cannot confirm whether Indian boards are included. Naukri and Foundit block the plain HTTP requests and headless browsers that server-side automation relies on, so treat them as excluded unless LoopCV names them explicitly.'),
        ('Is it a good idea to let software email employers for me?',
         'A judged, specific follow-up helps. An automated template sent at volume to employers who did not ask for it risks your email being marked as spam, which damages every later application from that address. If you use a tool with this feature, read exactly what it sends before switching it on.'),
        ('How much does LoopCV cost?',
         'Its pricing page states that paid plans start from €9.99 a month, which is roughly ₹950 at the time of writing, billed recurrently. It also offers a free plan. Check the current page for the tier that includes the features you need, since what each tier covers is where the real difference sits.'),
    ],
    siblings=[
        ('Auto-apply tools for India, compared', 'best-auto-apply-tools-india.html'),
        ('ApplySarthi vs LazyApply', 'vs-lazyapply.html'),
        ('Is auto-applying safe?', 'is-auto-apply-safe.html'),
        ('Auto-apply on Naukri', 'guides/naukri-auto-apply.html'),
    ])

JOBRIGHT = page(
    'jobright-ai', 'Jobright AI',
    'ApplySarthi vs Jobright AI: strong matching, different market',
    'Jobright matches jobs, autofills applications and suggests insider connections, with a clear United States focus. ApplySarthi does the matching and filling for the Indian market. The deciding factor is geography.',
    'Both are matching engines with an autofill attached. They are pointed at different countries, and that settles most of it.',
    verified=f"""
<p><b>Jobright</b> describes itself as delivering &ldquo;matched jobs, autofill applications, tailored
resume, and recommended insider connections in less than 1 min&rdquo;, with a 24/7 AI career assistant.
Its site surfaces categories such as H1B jobs and top United States remote roles, and its location
selector centres on the United States.
(<a href="https://jobright.ai/" rel="nofollow">Official site</a>, read {REVIEWED}.)</p>
<p>Jobright does not publish a candidate pricing page at a public URL that we could read, so we are not
quoting plan prices. Third-party reviews report a paid Turbo tier; we could not confirm the figure from
Jobright and have not repeated it.</p>
<p><b>ApplySarthi</b> is free in early access, and its sources are Indian and international boards plus
{ATS_BOARDS} company career boards, with {OPEN_JOBS} postings open in the current snapshot.</p>""",
    differ="""
""" + table(['', 'ApplySarthi', 'Jobright AI'], [
        ('Primary market', 'India', 'United States, including H1B categories'),
        ('Price', 'Free in early access', 'Not published on a public page'),
        ('Matching', 'Your CV text against the full job description', 'Matching plus insider connections'),
        ('Presses submit', 'No, unless you switch Autopilot on', 'Autofill; an agent on paid tiers'),
        ('Indian job boards', 'Naukri, Foundit, Shine, Internshala, Wellfound, LinkedIn, Indeed', 'Not a stated focus'),
        ('Whose AI quota', 'Your own free Google Gemini key', 'The vendor&rsquo;s, within your plan'),
    ]),
    decide="""
<p>If you are applying for roles in the United States, Jobright is aimed at you and this comparison is not
the one to read; its matching and its connection suggestions are built for that market and its H1B
categories are genuinely useful there.</p>
<p>If you are applying in India, the question answers itself on coverage. A matching engine is only as good
as the postings it can see, and the Indian market advertises heavily on boards that a United States-focused
product has no reason to collect.</p>
<p>The insider-connections idea is worth taking seriously whichever tool you use. A referral outperforms a
cold application almost everywhere. Nothing stops you using ApplySarthi to find and file the application
and then looking for a connection at that company yourself.</p>""",
    unverified="""
<p>We could not read Jobright&rsquo;s candidate pricing from a public page, so no prices are quoted here.
We have not tested its matching quality, its autofill, the scope of its agent feature, or whether it
returns Indian postings in practice. Its geographic focus is inferred from the categories and location
options its own site presents, not from a statement of coverage.</p>""",
    faq=[
        ('Does Jobright AI work in India?',
         'Jobright’s own site centres on the United States — its location selector, its H1B job categories and its remote-role listings are all United States oriented — and it does not state Indian job board coverage. We have not tested whether Indian postings appear in practice. For an India-focused search, coverage is the first thing to check rather than features.'),
        ('How much does Jobright AI cost?',
         'We could not find a candidate pricing page at a public URL when we checked, so we are not quoting a figure. Third-party reviews report a paid Turbo tier at a monthly price, but since we could not confirm that from Jobright itself we have left it out. Check inside the product for current pricing.'),
        ('What is a good Jobright alternative for Indian job seekers?',
         'The requirement is a matcher that can actually see Indian postings. ApplySarthi ranks your CV against 60,975 open jobs from 21 sources including Naukri, Foundit, Shine and Internshala, plus 754 company career boards, and fills the application form in your own Chrome. It is free during early access.'),
    ],
    siblings=[
        ('Auto-apply tools for India, compared', 'best-auto-apply-tools-india.html'),
        ('ApplySarthi vs Simplify', 'vs-simplify-jobs.html'),
        ('ApplySarthi vs AIApply', 'vs-aiapply.html'),
        ('What 60,975 open jobs actually contain', 'job-application-statistics-india.html'),
    ])

AIAPPLY = page(
    'aiapply', 'AIApply',
    'ApplySarthi vs AIApply: a suite against a specialist',
    'AIApply bundles resume building, cover letters, an ATS scanner, credit-based auto-apply and mock interviews. ApplySarthi does applying, and hands interviews to Interview Sarthi. How the two stacks compare.',
    'One product tries to cover the whole job search. We split it in two on purpose. Here is the honest case for each shape.',
    verified=f"""
<p><b>AIApply</b> presents an integrated suite: an AI resume builder, a cover letter generator, a resume
scanner that checks against ATS criteria, an auto-apply feature that finds and applies to high-match jobs,
and mock interview tools. Its site cites a job board aggregating 20M+ jobs and reports more than two
million users. Auto-apply is sold as credit packs rather than unlimited use.
(<a href="https://aiapply.co/" rel="nofollow">Official site</a>, read {REVIEWED}.)</p>
<p>AIApply does not publish plan prices on the page we read, so none are quoted here.</p>
<p><b>ApplySarthi</b> covers applying only: collection from {SOURCES} sources and {ATS_BOARDS} career
boards, CV matching, per-job CV tailoring, cover letters and form filling in your own Chrome. Interviews
are a separate product, <a href="{UP}">Interview Sarthi</a>, with its own passes.</p>""",
    differ="""
""" + table(['', 'ApplySarthi', 'AIApply'], [
        ('Shape', 'Applying only; interviews are a separate product', 'One suite across the whole search'),
        ('Price', 'Free in early access', 'Not published; auto-apply sold as credit packs'),
        ('Presses submit', 'No, unless you switch Autopilot on', 'Yes, spending credits'),
        ('Indian job boards', 'Naukri, Foundit, Shine, Internshala, Wellfound, LinkedIn, Indeed', 'Not stated'),
        ('Interview help', 'Interview Sarthi &mdash; live help during the real call', 'Mock interview tools in the suite'),
        ('Whose AI quota', 'Your own free Google Gemini key', 'The vendor&rsquo;s, plus credits'),
    ]),
    decide="""
<p>The honest case for a suite is that one subscription and one login covers everything, and you are not
reconciling two products. If that is what you want, AIApply is a reasonable place to look, and its resume
scanner and mock interview tools are real features.</p>
<p>The case for splitting, which is the choice we made, is that applying and interviewing are different
problems. Applying is a data problem: find what is open, judge fit, fill forms accurately. Interviewing is
a live problem: hearing a question and having something grounded to say in the next few seconds. A mock
interview generator and live help on a real call are not the same product, and we would rather build each
one properly.</p>
<p>On credits: a credit model prices each application, which quietly discourages applying to a role you are
unsure about. That is worth noticing, because the roles people hesitate over are often the ones worth
applying for.</p>
<p>On coverage, the same question as everywhere on this site: we could not confirm Indian board coverage
from AIApply&rsquo;s public pages.</p>""",
    unverified="""
<p>We have not verified AIApply&rsquo;s prices, credit pack sizes, Indian job board coverage, resume
scanner accuracy, or the user and outcome statistics quoted on its own marketing pages. We have not tested
its auto-apply. Outcome percentages published by any vendor about its own users, ours included, should be
read as marketing until the method behind them is published.</p>""",
    faq=[
        ('Is an all-in-one job search tool better than separate ones?',
         'It depends on whether the parts are equally good. A suite gives you one login and one bill. The risk is that applying and interviewing are genuinely different problems — one is about finding and filling accurately, the other about having something grounded to say within seconds on a live call — and a single product rarely does both well. Try the part you need most before committing to the bundle.'),
        ('How much does AIApply cost?',
         'The pages we read do not publish plan prices, so we are not quoting any. Its auto-apply feature is described as sold in credit packs rather than as unlimited use, which means each application has a price attached. Check inside the product for current figures.'),
        ('Does ApplySarthi help with interviews too?',
         'Not directly — that is Interview Sarthi, a separate product from the same team, which gives resume-grounded help during the actual interview in English, Hindi or Hinglish. Both run on the same free Google Gemini key, so setting one up covers the other. ApplySarthi flags upcoming interviews in its tracker and hands you across.'),
    ],
    siblings=[
        ('Auto-apply tools for India, compared', 'best-auto-apply-tools-india.html'),
        ('ApplySarthi vs Jobright AI', 'vs-jobright-ai.html'),
        ('ApplySarthi vs Simplify', 'vs-simplify-jobs.html'),
        ('You applied to 200 jobs and heard nothing', 'guides/why-no-interview-calls.html'),
    ])

PAGES = [LAZYAPPLY, SIMPLIFY, LOOPCV, JOBRIGHT, AIAPPLY]
