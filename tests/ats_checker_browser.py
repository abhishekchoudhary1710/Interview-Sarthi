"""The ATS resume checker in a real browser: real PDFs and a real .docx, read by the real libraries.

Builds its own sample CVs (one column, two columns, an image-only scan, a Word file with a table), serves the
site locally and checks what the page reports for each. Analytics and the chat widget are blocked so no test
event reaches a provider; PDF.js and Mammoth load from cdnjs, as they do for visitors. Needs Playwright (or
the patchright fork) with Chromium. Screenshots go to the ignored .seo-preview/.

    python tests/ats_checker_browser.py
"""
import base64
import functools
import http.server
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import zipfile

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    from patchright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.seo-preview'
BLOCK = ('googletagmanager.com', 'google-analytics.com', 'clarity.ms', '/chat/', 'wa.me')

CV_LINES = [
    ('h1', 'Priya Sharma'),
    ('p', 'Bengaluru · priya.sharma@example.com · +91 98765 43210 · linkedin.com/in/priya-sharma'),
    ('h2', 'Summary'),
    ('p', 'Data analyst with four years in e-commerce reporting, SQL and Power BI.'),
    ('h2', 'Experience'),
    ('h3', 'Data Analyst, Flipkart · Mar 2022 – Present'),
    ('li', 'Built 14 Power BI dashboards used by 120 category managers every week'),
    ('li', 'Cut the monthly reporting cycle from 5 days to 2 by automating SQL extracts'),
    ('li', 'Found why refunds rose 18% in Q2 using SQL on 2 million orders'),
    ('li', 'Led a pricing analysis that lifted conversion by 3.1% in two categories'),
    ('h3', 'Junior Analyst, Swiggy · Jun 2020 – Feb 2022'),
    ('li', 'Automated 6 Excel reports with Python, saving 10 hours a week'),
    ('li', 'Analysed delivery delays across 40 cities and presented fixes to operations'),
    ('h2', 'Education'),
    ('p', 'B.Tech, Computer Science, VIT Vellore · Jul 2016 – May 2020'),
    ('h2', 'Skills'),
    ('p', 'SQL, Python, Excel, Power BI, Tableau, Stakeholder management'),
]


def html_one_column():
    body = ''.join(f'<{t}>{x}</{t}>' for t, x in CV_LINES)
    return f'<html><body style="font:12pt Arial;margin:40px">{body}</body></html>'


def html_two_columns():
    side = ''.join(f'<{t}>{x}</{t}>' for t, x in CV_LINES[:2] + CV_LINES[-4:])
    main = ''.join(f'<{t}>{x}</{t}>' for t, x in CV_LINES[2:-4])
    return ('<html><body style="font:11pt Arial;margin:30px;display:grid;grid-template-columns:32% 1fr;gap:28px">'
            f'<div>{side}</div><div>{main}</div></body></html>')


def docx_bytes():
    """A small real .docx: the CV in paragraphs, plus the education in a table."""
    def para(text, style=None):
        ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
        return f'<w:p>{ppr}<w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'
    paras = []
    for tag, text in CV_LINES:
        if text.startswith('B.Tech'):
            paras.append('<w:tbl><w:tr><w:tc>' + para('B.Tech, Computer Science') + '</w:tc><w:tc>' +
                         para('VIT Vellore · Jul 2016 – May 2020') + '</w:tc></w:tr></w:tbl>')
        else:
            paras.append(para(('• ' if tag == 'li' else '') + text,
                              {'h1': 'Title', 'h2': 'Heading1', 'h3': 'Heading2'}.get(tag)))
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
           + ''.join(paras) + '</w:body></w:document>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('[Content_Types].xml',
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                   '</Types>')
        z.writestr('_rels/.rels',
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                   '</Relationships>')
        z.writestr('word/document.xml', doc)
    return buf.getvalue()


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Quiet, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{server.server_address[1]}'


def statuses(page):
    return page.evaluate("""() => Object.fromEntries([...document.querySelectorAll('.ats-group li')].map(li =>
        [li.querySelector('b').textContent, li.className.replace('ats-', '')]))""")


def score(page):
    return int(page.text_content('.ats-num b'))


def check(cond, message):
    if not cond:
        raise AssertionError(message)
    print('ok  ', message)


def main():
    OUT.mkdir(exist_ok=True)
    server, base = serve()
    errors = []
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        browser = pw.chromium.launch(headless=True)
        maker = browser.new_page()
        maker.set_content(html_one_column()); maker.pdf(path=str(tmp / 'one-column.pdf'))
        maker.set_content(html_two_columns()); maker.pdf(path=str(tmp / 'two-columns.pdf'))
        maker.set_content(html_one_column())
        png = base64.b64encode(maker.screenshot(full_page=True)).decode()
        maker.set_content(f'<html><body style="margin:0"><img src="data:image/png;base64,{png}" style="width:100%"></body></html>')
        maker.pdf(path=str(tmp / 'scan.pdf'))
        (tmp / 'cv.docx').write_bytes(docx_bytes())

        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        ctx.route('**/*', lambda route: route.abort() if any(b in route.request.url for b in BLOCK) else route.continue_())
        ctx.route('https://apply.interviewsarthi.com/api/jd**', lambda route: route.fulfill(
            status=200, headers={'access-control-allow-origin': '*', 'content-type': 'application/json'},
            body=json.dumps({'title': 'Data Analyst', 'company': 'Acme Retail', 'location': 'Bengaluru',
                             'text': 'Acme Retail needs a Data Analyst. Build dashboards in Power BI and Tableau, '
                                     'write SQL, and use Python. Experience with Snowflake and Airflow. You will own '
                                     'merchandising reporting and forecasting; forecasting experience preferred. '
                                     'Merchandising teams rely on your dashboards.'})))
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' and 'ERR_FAILED' not in m.text
                and 'net::' not in m.text else None)

        page.goto(base + '/apply/ats-resume-checker/')
        page.set_input_files('#ats-file', str(tmp / 'one-column.pdf'))
        page.wait_for_selector('#ats-result:not([hidden]) .ats-num', timeout=30000)
        s, st = score(page), statuses(page)
        check(s >= 85, f'one-column PDF scores {s}')
        check(st['One column'] == 'pass', 'one-column PDF reads as one column')
        check(st['Phone number'] == 'pass' and st['Email address'] == 'pass', 'contact details found in the PDF')
        check('Paste a job description' in page.text_content('.ats-match'), 'no job given: the match asks for one')
        nxt = lambda: (page.get_attribute('.ats-next', 'data-next'), page.get_attribute('.ats-next a.cta', 'href'))
        check(nxt() == ('all', 'https://apply.interviewsarthi.com/jobs-in/india'),
              f'no job and no role: Next opens all jobs in India {nxt()}')
        page.click('#ats-tab-1')
        page.select_option('#ats-role', 'devops-engineer')
        page.wait_for_function("document.querySelector('.ats-match h3').textContent.includes('%')")
        check('DevOps and cloud engineer postings' in page.text_content('.ats-match h3'), 'role match follows the picker')
        # The top card shows the fit beside the health score, so changing the role visibly changes the result.
        health = score(page)
        fit = page.text_content('.ats-summary .ats-fit')
        check('DevOps and cloud engineer postings' in fit and '%' in fit, f'top card shows the DevOps fit: {fit.strip()[:80]}')
        page.select_option('#ats-role', 'qa-engineer')
        page.wait_for_function("document.querySelector('.ats-summary .ats-fit').textContent.includes('QA and test engineer')")
        fit_qa = page.text_content('.ats-summary .ats-fit')
        check(score(page) == health and 'Weak fit' in fit_qa and 'Selenium' in fit_qa,
              f'switching to QA keeps health at {health} and shows a weak QA fit: {fit_qa.strip()[:90]}')
        check(nxt() == ('role', 'https://apply.interviewsarthi.com/jobs-in/india/qa-engineer')
              and 'See QA and test engineer jobs in India' in page.text_content('.ats-next a.cta'),
              f'a role: Next opens that role\'s jobs in India {nxt()}')
        page.select_option('#ats-role', '')
        page.fill('#ats-jd', 'We are hiring a QA engineer to own test automation. You will write Selenium and '
                             'Playwright suites in Java and Python, run them from Jenkins in our CI/CD pipeline, '
                             'and log defects in Jira.')
        page.wait_for_function("document.querySelector('.ats-next') && document.querySelector('.ats-next').dataset.next === 'role'")
        check(nxt()[1].endswith('/jobs-in/india/qa-engineer'), f'a pasted QA description: Next opens QA jobs {nxt()}')
        page.fill('#ats-jd', '')
        page.select_option('#ats-role', 'qa-engineer')
        page.wait_for_function("document.querySelector('.ats-next').dataset.next === 'role'")
        page.select_option('#ats-role', 'data-analyst')
        page.wait_for_function("document.querySelector('.ats-summary .ats-fit').textContent.includes('data analyst')")
        check('Strong fit' in page.text_content('.ats-summary .ats-fit'), 'a data analyst CV is a strong data analyst fit')
        page.click('#ats-tab-0')
        page.click('.ats-summary [data-tab="1"]')
        check(page.get_attribute('#ats-tab-1', 'aria-selected') == 'true' and not page.is_hidden('#ats-panel-1'),
              '"See the job match" opens the Job match tab')
        page.screenshot(path=str(OUT / 'ats-desktop.png'), full_page=True)

        page.set_input_files('#ats-file', str(tmp / 'two-columns.pdf'))
        page.wait_for_function("document.getElementById('ats-filename').textContent.includes('two-columns')")
        page.wait_for_function("[...document.querySelectorAll('.ats-group li b')].some(b => b.textContent === 'One column' && b.parentElement.className === 'ats-warn')", timeout=30000)
        check(score(page) <= 79, f'two-column PDF is flagged and never "Ready to send" ({score(page)})')

        page.set_input_files('#ats-file', str(tmp / 'scan.pdf'))
        page.wait_for_function("document.querySelector('.ats-verdict') && document.querySelector('.ats-verdict').textContent.includes(\"can't read\")", timeout=30000)
        check(score(page) == 0, 'image-only PDF scores 0 and says an ATS cannot read it')

        page.set_input_files('#ats-file', str(tmp / 'cv.docx'))
        page.wait_for_function("[...document.querySelectorAll('.ats-group li b')].some(b => b.textContent === 'No layout tables')", timeout=30000)
        st = statuses(page)
        check(st['No layout tables'] == 'warn', 'Word file with a table is flagged')
        check(st['Email address'] == 'pass' and st['Experience section'] == 'pass', 'Word file text and headings read')

        page.goto(base + '/apply/ats-resume-checker/data-analyst.html?job=greenhouse:4321')
        page.wait_for_selector('#ats-from:not([hidden])')
        check('Data Analyst at Acme Retail' in page.text_content('#ats-from'), 'job from ApplySarthi is loaded by id')
        check(page.eval_on_selector('#ats-role', 'e => e.value') == 'data-analyst', 'role page presets its role')
        page.set_input_files('#ats-file', str(tmp / 'one-column.pdf'))
        page.wait_for_selector('#ats-result:not([hidden]) .ats-num')
        page.click('#ats-tab-1')
        page.wait_for_selector('#ats-result:not([hidden]) .ats-match h3')
        match = page.text_content('.ats-match')
        check('Match with this job' in match and 'Snowflake' in match and 'Airflow' in match,
              'job match lists the skills the CV lacks')
        check('acme' not in page.eval_on_selector('.ats-match', 'e => e.textContent.toLowerCase().replace("acme retail needs", "")'),
              "the employer's own name is never a missing word")
        page.click('#ats-tab-0')
        href = page.get_attribute('.ats-next a.cta', 'href')
        check(href.startswith('https://apply.interviewsarthi.com/go/apply?slot=ats_result&source=greenhouse&id=4321')
              and page.text_content('.ats-next a.cta') == 'Tailor my CV for this job, free'
              and 'Data Analyst at Acme Retail' in page.text_content('.ats-next'),
              'a job from ApplySarthi: Tailor opens its sign-in for that job, with the slot')
        check(page.get_attribute('.ats-next .alsotry a', 'href') == '/prep/app/?job=greenhouse%3A4321',
              'Prep link opens this job in the app')

        page.goto(base + '/apply/ats-resume-checker/')
        page.click('.ats-paste summary')
        page.fill('#ats-text', '\n'.join(x for _, x in CV_LINES))
        page.click('#ats-go')
        page.wait_for_selector('#ats-result:not([hidden]) .ats-num')
        check(statuses(page)['Layout'] == 'na', 'pasted text runs every check except layout')

        mobile = browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True)
        mobile.route('**/*', lambda route: route.abort() if any(b in route.request.url for b in BLOCK) else route.continue_())
        m = mobile.new_page()
        m.goto(base + '/apply/ats-resume-checker/')
        m.set_input_files('#ats-file', str(tmp / 'one-column.pdf'))
        m.wait_for_selector('#ats-result:not([hidden]) .ats-num', timeout=30000)
        wide = m.evaluate('document.scrollingElement.scrollWidth - window.innerWidth')
        check(wide <= 0, f'no sideways scrolling on a phone ({wide}px)')
        m.screenshot(path=str(OUT / 'ats-mobile.png'), full_page=True)
        browser.close()
    server.shutdown()
    check(not errors, 'no script errors' + (': ' + '; '.join(errors) if errors else ''))


if __name__ == '__main__':
    try:
        main()
    except AssertionError as e:
        print('FAIL', e)
        sys.exit(1)
