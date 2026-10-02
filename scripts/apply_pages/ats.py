"""The free ATS resume checker: one page with the tool, and one page per role that the job data supports.

The checker itself is assets/ats-engine.js (the score) and assets/ats-checker.js (reading the file in the
browser). These pages are the text around it. Role figures are the share of open Indian postings in each
role that name a skill, read from the ApplySarthi database on SNAPSHOT (job_skills joined to jobs, role by
public.role_family on the title). Company and industry words that the skill dictionary also counts (SaaS,
B2B, B2C, supply chain) are left out: they describe the employer, not what the candidate needs.

Only eight roles get a page. HR, support, design, sales, marketing, operations and mobile were measured on the
same date and left out: under ~250 postings, or a top-ten list led by words like "supply chain" because the
dictionary is built for technical skills. A page of noise would be the thin content search engines discount.

assets/ats-skills.json carries ROLES to the browser; scripts/export_ats_skills.py writes it and
tests/test_ats_pages.py fails if the two disagree.
"""
import html

from ._shared import table

UP = '../../'
SNAPSHOT = '2 October 2026'
DATE = '2026-10-02'
BASE = '/apply/ats-resume-checker/'
ORIGIN = 'https://interviewsarthi.com'

# slug, role family in Job-Hunt public.ROLE_FAMILIES, open India postings read, skills with share (%)
ROLES = [
    {'slug': 'software-engineer', 'family': 'software', 'postings': 4281,
     'label': 'Software engineer', 'plural': 'software engineers',
     'title': 'Software Engineer Resume ATS Checker (Free, India)',
     'skills': [('Python', 21.2), ('AWS', 19.1), ('Java', 17.4), ('Agile', 16.6), ('CI/CD', 15.7),
                ('System design', 14.4), ('Azure', 11.4), ('SQL', 11.1), ('Microservices', 10.7),
                ('Kubernetes', 10.5)],
     'tips': [
         '<b>Put the stack inside each role, not only in the skills list.</b> &ldquo;Built the order service '
         'in Java and Spring Boot on AWS&rdquo; tells a recruiter who searches for Java where you used it and '
         'for how long. A bare list does not.',
         '<b>Give scale a number.</b> Requests a day, users, data volume, response time before and after. A '
         'figure you can explain in the interview beats an adjective.',
         '<b>Name design work when you did it.</b> System design and microservices come up often in these '
         'postings. If you designed a service or split one apart, say so in those words.']},
    {'slug': 'data-scientist', 'family': 'data_ml', 'postings': 1558,
     'label': 'Data scientist and AI/ML engineer', 'plural': 'data scientists and AI/ML engineers',
     'title': 'Data Scientist and AI/ML Resume ATS Checker (Free)',
     'skills': [('Python', 43.9), ('LLMs', 30.6), ('AWS', 29.2), ('Machine learning', 25.7), ('Azure', 25.0),
                ('SQL', 23.3), ('Generative AI', 22.2), ('CI/CD', 20.8), ('RAG', 17.8), ('GCP', 16.9)],
     'tips': [
         '<b>Say what you built, then what it changed.</b> &ldquo;Built a churn model in Python that the '
         'retention team used to pick which accounts to call&rdquo; beats a list of libraries.',
         '<b>Use the exact words for GenAI work.</b> LLMs, Generative AI and RAG each appear in a large share '
         'of these postings. If you built a RAG pipeline or fine-tuned a model, write those words; &ldquo;worked '
         'on AI&rdquo; matches nothing a recruiter types.',
         '<b>Show how you measured it.</b> The metric, the baseline and the result on data the model had not '
         'seen. Interviewers ask about this first.']},
    {'slug': 'data-analyst', 'family': 'analyst', 'postings': 1442,
     'label': 'Data analyst', 'plural': 'data analysts',
     'title': 'Data Analyst Resume ATS Checker (Free, India)',
     'skills': [('Excel', 26.9), ('SQL', 26.1), ('Python', 18.1), ('Stakeholder management', 15.0),
                ('Tableau', 13.6), ('Power BI', 13.3), ('Accounting', 11.0), ('Agile', 9.8), ('AWS', 7.0),
                ('Azure', 6.1)],
     'tips': [
         '<b>Name the tools exactly as postings do.</b> Excel, SQL, Power BI, Tableau: write the product '
         'names, not &ldquo;data tools&rdquo;. Recruiters search for them one at a time.',
         '<b>Write each bullet as question, analysis, decision.</b> &ldquo;Found why refunds rose in Q2 using '
         'SQL on two million orders; the fix cut them by a third.&rdquo;',
         '<b>Point to work they can see.</b> A public dashboard, a notebook on GitHub or a portfolio page with '
         'anonymised data does more than any adjective.']},
    {'slug': 'devops-engineer', 'family': 'devops', 'postings': 969,
     'label': 'DevOps and cloud engineer', 'plural': 'DevOps and cloud engineers',
     'title': 'DevOps and Cloud Engineer Resume ATS Checker (Free)',
     'skills': [('AWS', 32.8), ('Python', 32.0), ('CI/CD', 26.6), ('Kubernetes', 24.3), ('Azure', 23.1),
                ('Observability', 21.3), ('Terraform', 19.7), ('GCP', 17.8), ('Linux', 16.7), ('Agile', 13.6)],
     'tips': [
         '<b>Name the cloud and the services.</b> &ldquo;AWS (EKS, RDS, Lambda)&rdquo; is what recruiters '
         'search for; &ldquo;cloud&rdquo; is not.',
         '<b>Show reliability in numbers.</b> Deploys a day, uptime, time to recover, the monthly bill you '
         'cut. These are the questions you will be asked.',
         '<b>Say what you turned into code.</b> The Terraform modules you wrote, the CI/CD pipeline you built, '
         'the Kubernetes clusters you ran. The verbs matter as much as the tools.']},
    {'slug': 'qa-engineer', 'family': 'qa', 'postings': 385,
     'label': 'QA and test engineer', 'plural': 'QA and test engineers',
     'title': 'QA and Test Engineer Resume ATS Checker (Free)',
     'skills': [('Test automation', 34.8), ('Python', 28.8), ('CI/CD', 28.8), ('Selenium', 22.9), ('Agile', 22.9),
                ('Java', 21.0), ('Playwright', 19.0), ('SQL', 16.1), ('Jenkins', 16.1), ('Jira', 15.8)],
     'tips': [
         '<b>Name the framework and the language together.</b> &ldquo;Selenium with Java&rdquo; or '
         '&ldquo;Playwright with Python&rdquo;: postings ask for the pair, and recruiters search for both.',
         '<b>Count what your tests did.</b> Regression time cut from two days to three hours, the number of '
         'automated cases, defects caught before release.',
         '<b>Say where the tests ran.</b> Tests that run in a CI/CD pipeline such as Jenkins on every commit '
         'read as engineering. A folder of scripts does not.']},
    {'slug': 'frontend-developer', 'family': 'frontend', 'postings': 128,
     'label': 'Front-end developer', 'plural': 'front-end developers',
     'title': 'Front-end Developer Resume ATS Checker (Free)',
     'skills': [('React', 57.0), ('JavaScript', 46.9), ('CSS', 44.5), ('HTML', 40.6), ('Agile', 35.9),
                ('TypeScript', 34.4), ('Git', 31.2), ('REST APIs', 28.1), ('CI/CD', 23.4), ('Angular', 22.7)],
     'tips': [
         '<b>Lead with the framework and the language.</b> React with JavaScript or TypeScript leads these '
         'postings, with CSS and HTML close behind. Put them in your first lines, not only in a skills list.',
         '<b>Measure speed and quality.</b> Page load time, Lighthouse score, bundle size, accessibility fixes. '
         'Front-end interviews ask how you know a page is fast.',
         '<b>Link work that runs.</b> A live site or a GitHub repository with a readme gets opened by hiring '
         'managers more often than a description gets read.']},
    {'slug': 'product-manager', 'family': 'product', 'postings': 638,
     'label': 'Product and project manager', 'plural': 'product and project managers',
     'title': 'Product and Project Manager Resume ATS Checker',
     'skills': [('Product management', 30.9), ('Stakeholder management', 29.8), ('Agile', 21.0), ('SQL', 16.0),
                ('Excel', 11.3), ('Jira', 11.0), ('Customer success', 6.6), ('AWS', 6.1), ('Generative AI', 6.0),
                ('Azure', 5.6)],
     'tips': [
         '<b>Write outcomes, not activities.</b> &ldquo;Launched UPI autopay; failed renewals fell 22%&rdquo; '
         'rather than &ldquo;managed the payments roadmap&rdquo;.',
         '<b>Show the people side in plain words.</b> Stakeholder management comes up in close to a third of '
         'these postings. Say who you brought together (engineering, sales, a regulator) and on what.',
         '<b>Say how you used data.</b> SQL and Excel come up often for product roles in India. If you wrote '
         'your own queries or defined the metric, say so.']},
    {'slug': 'finance-accounts', 'family': 'finance', 'postings': 536,
     'label': 'Finance and accounts', 'plural': 'finance and accounts professionals',
     'title': 'Accountant and Finance Resume ATS Checker (Free)',
     'skills': [('Accounting', 46.5), ('Excel', 25.6), ('Stakeholder management', 19.4), ('ERP', 15.5),
                ('SAP', 12.5), ('SQL', 5.8), ('Financial modelling', 5.8), ('Workday', 5.4)],
     'tips': [
         '<b>Put qualifications at the top.</b> CA, CMA, ACCA or CFA, with the year or the level cleared, '
         'belong in the first lines, where a recruiter and a parser both look first.',
         '<b>Name the ERP and the module.</b> SAP FICO, Oracle, Tally or Workday, written out. &ldquo;ERP '
         'experience&rdquo; on its own is not what recruiters search for.',
         '<b>Count the work.</b> Entities consolidated, invoices a month, a close cut from eight days to five, '
         'audit points resolved.']},
]


def in_sentence(label):
    """"Data analyst" -> "data analyst"; names with capitals inside (DevOps, QA, AI/ML) keep them."""
    return ' '.join(w if any(c.isupper() for c in w[1:]) else w.lower() for w in label.split(' '))


def roles_json():
    """What assets/ats-skills.json carries for the role picker: the same figures the pages print."""
    return {r['slug']: {'label': r['label'], 'postings': r['postings'], 'skills': [list(s) for s in r['skills']]}
            for r in ROLES}


def tool_html(role=''):
    options = ''.join(
        f'<option value="{r["slug"]}"{" selected" if r["slug"] == role else ""}>{html.escape(r["label"])}</option>'
        for r in ROLES)
    return f"""
<section class="ats" id="checker" data-role="{role}" aria-label="ATS resume checker">
<div class="ats-toolbar"><div><span class="ats-eyebrow">RESUME WORKSPACE</span><h2>Make your next application stronger</h2></div><span class="ats-private">● Private on your device</span></div>
<div class="ats-workspace"><aside class="ats-inputs" aria-label="Resume and job inputs">
<div class="ats-step">
<h2 class="ats-h">1. Your CV</h2>
<label class="ats-drop" id="ats-drop">
<input type="file" id="ats-file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document">
<span class="ats-drop-main">Choose your CV</span>
<span class="ats-drop-sub">PDF or Word (.docx), up to 5 MB. Read in this browser, never uploaded.</span>
</label>
<p class="ats-file" id="ats-filename" hidden></p>
<details class="ats-paste"><summary>Or paste your CV&rsquo;s text</summary>
<textarea id="ats-text" rows="5" aria-label="Your CV's text" placeholder="Paste the whole CV here"></textarea>
</details>
</div>
<div class="ats-step">
<h2 class="ats-h">2. The job <span>(optional)</span></h2>
<p class="ats-from" id="ats-from" hidden></p>
<textarea id="ats-jd" rows="4" aria-label="Job description" placeholder="Paste the job description to see which of its skills your CV is missing"></textarea>
<label class="ats-role">No job description? Compare with a role:
<select id="ats-role"><option value="">Choose a role</option>{options}</select>
</label>
</div>
<button type="button" class="cta ats-go" id="ats-go">Check my CV</button>
<p class="ats-status" id="ats-status" role="status" aria-live="polite"></p>
</aside><div class="ats-output">
<div id="ats-empty" class="ats-empty"><span class="ats-empty-icon" aria-hidden="true">◎</span><h3>Your resume, at a glance</h3><p>Add your CV to see your score, priority fixes and skill gaps in one place.</p><div class="ats-preview"><span>Readability</span><span>Contact &amp; sections</span><span>Job match</span></div><p class="note">Free checks · No sign-up · No uploads</p></div>
<div class="ats-result" id="ats-result" hidden></div>
</div></div>
<noscript><p class="box warn">The checker runs inside your browser, so it needs JavaScript switched on.</p></noscript>
</section>
"""


HEAD = (f'<link rel="stylesheet" href="{UP}assets/ats-checker.css">'
        f'<script defer src="{UP}assets/ats-engine.js"></script>'
        f'<script defer src="{UP}assets/ats-checker.js"></script>')

PRIVACY = """
<h2>Your CV stays on your device</h2>
<p>The page reads your file inside this browser tab, with PDF.js (Mozilla&rsquo;s PDF reader) for PDFs and
Mammoth for Word files, and scores it there. Your CV is not uploaded, stored or sent anywhere, and this page
does not record your screen. Close the tab and it is gone.</p>
<p>If you arrive from a job on ApplySarthi, the page fetches that job&rsquo;s public description by its id so
you do not have to paste it. Nothing about you goes with that request.</p>
"""

HONEST = """
<div class="box"><p><b>No applicant tracking system gives your CV a score.</b> It parses your CV into fields and
stores it, and recruiters search what it stored. The real failure is quieter than a rejection: a CV the parser
half-reads comes back in nobody&rsquo;s search. This score adds up the things that cause that, and the job
match shows which of the job&rsquo;s words a recruiter&rsquo;s search would not find in your CV. The
<a href="../guides/ats-resume-format-india.html">ATS format guide</a> explains each one.</p></div>
"""

SCORE_TABLE = table(['What it checks', 'Points', 'Why it matters'], [
    ('Can an ATS read it?', '35', 'Real text rather than a scan, one column, no icon characters, a sensible length.'),
    ('Contact details', '15', 'Email, phone and your LinkedIn address, in the body where every parser reads.'),
    ('Sections', '20', 'Experience, Education and Skills under headings a parser recognises, and a summary.'),
    ('What your lines say', '20', 'Bullets that carry numbers, start with what you did, and dates in one format.'),
    ('Indian CV habits', '10', 'Date of birth, marital status, father&rsquo;s name, a declaration, &ldquo;Resume&rdquo; as the title.'),
])

ROLE_LIST = '<ul>' + ''.join(
    f'<li><a href="{r["slug"]}.html"><b>{html.escape(r["label"])}</b></a> &mdash; the skills '
    f'{r["postings"]:,} open postings in India name most</li>' for r in ROLES) + '</ul>'

MAIN = {
    'path': 'apply/ats-resume-checker/index.html',
    'trail': [('ApplySarthi', '/apply/'), ('ATS resume checker', BASE)],
    'title': 'Free ATS Resume Checker for India: No Sign-up, No Upload',
    'description': 'Check whether an applicant tracking system can read your CV and which skills from the job '
                   'it is missing. Runs in your browser, so your CV is never uploaded. Free, no sign-up.',
    'h1': 'Free ATS resume checker',
    'lead': 'See what an applicant tracking system can read in your CV, what it loses, and which words from '
            'the job your CV is missing. Your file is read inside this browser tab and never uploaded.',
    'meta': f'Updated {SNAPSHOT} · Free, no sign-up · Made by the team that builds ApplySarthi',
    'published': DATE, 'modified': DATE,
    'head': HEAD,
    'cta_title': 'Missing skills? Tailor your CV for the job',
    'cta_text': 'ApplySarthi rewrites your CV for one job using only what your CV already says, and gives you '
                'a clean one-column PDF. Always free.',
    'schema': [{
        '@type': 'WebApplication', '@id': ORIGIN + BASE + '#app', 'name': 'ATS Resume Checker',
        'url': ORIGIN + BASE, 'applicationCategory': 'BusinessApplication',
        'operatingSystem': 'Any (runs in a web browser)', 'isAccessibleForFree': True,
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'INR'},
        'publisher': {'@id': ORIGIN + '/#organization'},
    }],
    'body': tool_html() + f"""
<h2>How the score works</h2>
{SCORE_TABLE}
{HONEST}

<h2>Check against your role</h2>
<p>No job description to hand? Each page below compares your CV with the skills that open postings for the
role name most, read from ApplySarthi&rsquo;s job data on {SNAPSHOT}.</p>
{ROLE_LIST}
{PRIVACY}""",
    'faq': [
        ('Is this ATS resume checker free?',
         'Yes. There is no sign-up, no limit on checks and nothing to pay. It is part of ApplySarthi, which is always free.'),
        ('Is my resume uploaded anywhere?',
         'No. The page reads your file inside your browser tab, using PDF.js for PDFs and Mammoth for Word files, and scores it there. Your CV is not uploaded, stored or recorded, and closing the tab forgets it.'),
        ('What is a good ATS score?',
         'Above 85 means a parser can read your CV and it carries what recruiters look for; 70 to 84 is good with a few fixes; below 50, parts of your CV are likely to be lost. The score is our own measure: real applicant tracking systems do not score CVs, they parse and store them for recruiters to search.'),
        ('Does a high score guarantee interview calls?',
         'No. It means the parts of your CV that a system and a recruiter need are readable and present. Whether you are called depends on your experience, the role and how many people applied. Tailoring your CV to each job you apply for helps most.'),
        ('Can it check a Word file?',
         'Yes, .docx files work. Older .doc files do not: save them as .docx or PDF first, or paste the text. Contact details in a Word page header are not read here, which is also how some parsers behave, so keep them in the body.'),
    ],
    'more': [
        ('ATS resume format for Indian job applications', f'{UP}apply/guides/ats-resume-format-india.html'),
        ('You applied to 200 jobs and heard nothing', f'{UP}apply/guides/why-no-interview-calls.html'),
        ('Applying guides', f'{UP}apply/guides/'),
    ],
}


def role_page(r):
    others = ' · '.join(f'<a href="{o["slug"]}.html">{html.escape(o["label"])}</a>' for o in ROLES if o is not r)
    rows = [(html.escape(name), f'{share:.1f}%') for name, share in r['skills']]
    tips = ''.join(f'<li>{t}</li>' for t in r['tips'])
    small = (' That is a small sample, so read the order as a guide rather than a ranking.'
             if r['postings'] < 300 else '')
    return {
        'path': f'apply/ats-resume-checker/{r["slug"]}.html',
        'trail': [('ApplySarthi', '/apply/'), ('ATS resume checker', BASE), (r['label'], f'{BASE}{r["slug"]}.html')],
        'title': r['title'],
        'description': f'Check your {in_sentence(r["label"])} CV against the skills {r["postings"]:,} open postings in '
                       f'India name most, or against a job description. Runs in your browser: no upload, no sign-up.',
        'h1': f'ATS resume checker for {r["plural"]}',
        'lead': f'Check your CV against the skills that open {in_sentence(r["label"])} postings in India name most, '
                f'or paste a job description. Free, and your file never leaves this browser.',
        'meta': f'Updated {SNAPSHOT} · Free, no sign-up · Made by the team that builds ApplySarthi',
        'published': DATE, 'modified': DATE,
        'head': HEAD,
        'cta_title': 'Missing skills? Tailor your CV for the job',
        'cta_text': 'ApplySarthi rewrites your CV for one job using only what your CV already says, and gives you '
                    'a clean one-column PDF. Always free.',
        'body': tool_html(r['slug']) + f"""
<h2>What {html.escape(in_sentence(r['label']))} postings in India ask for</h2>
{table(['Skill', 'Share of postings naming it'], rows)}
<p class="note">Share of the {r['postings']:,} open {html.escape(in_sentence(r['label']))} postings in India on
ApplySarthi that name each skill, read on {SNAPSHOT}. Words that describe the employer rather than the work,
such as SaaS or supply chain, are left out.{small}</p>
<p>With no job description pasted, the checker compares your CV with the skills above that at least one
posting in ten names.</p>

<h2>Three fixes that matter for {html.escape(r['plural'])}</h2>
<ul>{tips}</ul>
<p>Add a skill to your CV only if you have used it. A recruiter will ask about every line.</p>
{PRIVACY}
<p class="tools">Other roles: {others} · <a href="./">The general checker</a></p>""",
        'more': [
            ('The free ATS resume checker', './'),
            ('ATS resume format for Indian job applications', f'{UP}apply/guides/ats-resume-format-india.html'),
            ('Browse open jobs on ApplySarthi', 'https://apply.interviewsarthi.com/jobs'),
        ],
    }


PAGES = [MAIN] + [role_page(r) for r in ROLES]
