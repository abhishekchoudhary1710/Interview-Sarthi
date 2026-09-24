"""Facts every ApplySarthi page is allowed to state, and the snippets that repeat.

Every number here was read from the running ApplySarthi database on the date in SNAPSHOT, or from the
source list in the Job-Hunt README. Nothing here is estimated. If a figure is not in this file, a page
may not assert it -- link to the source that has it instead.
"""

SNAPSHOT = '18 September 2026'
REVIEWED = '18 September 2026'
TODAY = '2026-09-18'

# Read from the live database on SNAPSHOT: SELECT count(*) FROM jobs WHERE status='open'.
OPEN_JOBS = '60,975'
POSTED_7D = '26,700'
SOURCES = 21
ATS_BOARDS = 754

# Open jobs by source, same snapshot, descending.
BY_SOURCE = [
    ('Indeed', '12,708'), ('Greenhouse', '9,796'), ('LinkedIn', '8,110'), ('Naukri', '6,293'),
    ('Lever', '4,837'), ('Shine', '3,452'), ('Ashby', '3,053'), ('Workday', '2,871'),
    ('Amazon', '2,333'), ('Oracle HCM', '1,651'), ('IBM', '1,113'), ('Internshala', '1,093'),
]

# Open jobs by city, where a city could be resolved at all (41.3% of postings).
BY_CITY = [
    ('Bengaluru', '10,632'), ('Delhi NCR', '3,474'), ('Hyderabad', '3,254'), ('Mumbai', '2,163'),
    ('Pune', '2,040'), ('Chennai', '1,662'), ('Ahmedabad', '398'), ('Kolkata', '309'),
    ('Kochi', '198'), ('Chandigarh', '186'),
]

# Share of open postings carrying each field at all.
COVERAGE = [
    ('Company name', '99.0%', 'Almost always present, though ATS-sourced rows carry the hiring entity, not the brand.'),
    ('Posting date', '99.5%', 'Reliable enough to filter on. Freshness is the one filter worth trusting.'),
    ('Description text', '96.7%', 'The body a matcher can actually read.'),
    ('Location string', '96.3%', 'Present, but often "India" or "Remote" rather than a city.'),
    ('A resolvable city', '41.3%', 'Fewer than half of postings name a city a filter can use.'),
    ('Company size', '20.9%', 'Mostly from Wellfound, which publishes it.'),
    ('Salary', '19.9%', 'Four postings in five say nothing about pay.'),
    ('Years of experience', '19.3%', 'Stated as a number far less often than job seekers expect.'),
    ('Skills list', '18.3%', 'Structured skills are the exception, not the rule.'),
    ('Closing date', '5.7%', 'Almost nobody publishes one; a job is open until it disappears.'),
]

APPLY_URL = 'https://apply.interviewsarthi.com/'

DISCLOSURE = (
    '<p><b>Disclosure:</b> we build ApplySarthi. Competitor information below was read from each '
    'product’s own public pages on {reviewed}, and is linked so you can check it. Where a price '
    'is not published publicly we say so rather than repeat a figure we could not verify. This page '
    'is not a hands-on benchmark of the other products.</p>'
).format(reviewed=REVIEWED)

METHOD = (
    '<p class="note">Figures come from the ApplySarthi database on {snapshot}: every posting it had '
    'collected from {sources} sources and {boards} company career boards and still believed to be '
    'open. It is a large sample of the Indian online job market, not a census of it.</p>'
).format(snapshot=SNAPSHOT, sources=SOURCES, boards=ATS_BOARDS)


def table(headers, rows, classes=''):
    head = ''.join(f'<th>{h}</th>' for h in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>' for row in rows)
    cls = f' class="{classes}"' if classes else ''
    return f'<table{cls}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def sarthi_handoff(prefix='../'):
    """Every applying page ends where applying ends: the interview."""
    return (
        '<div class="box"><p><b>When the calls start.</b> Applying is only the first half. Once an '
        'interview is booked, <a href="{p}live/">Live Sarthi</a> helps you through the call itself — '
        'resume-grounded answers in English, Hindi or Hinglish, on the same Gemini key ApplySarthi '
        'uses. See the <a href="{p}guides/">interview guides</a> for the questions that keep '
        'coming up.</p></div>'
    ).format(p=prefix)
