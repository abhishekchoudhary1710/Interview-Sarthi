"""The report screen while a free demo's report is written, and after it fails: the two 30 Sep 2026 incidents.
Fake audio, a fake licence server and a fake Gemini Live socket: no request leaves this process.

1. The first report model answers 504 ("Gemini too slow"): the app moves on to the second model.
2. While the report is written, Practise again is hidden and Start refuses a new interview.
3. Both models failing shows "Write my report again", which writes it from the same answers.
4. Once the demo's report has arrived, Start opens the passes instead of a call Google would refuse.

Run with Playwright; PREP_BROWSER may select the installed Chromium binary.
"""
import json
import mimetypes
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
AUDIO = '''export class AudioIO {
  constructor() { this.sampleRate=48000; this.micLabel='fake'; }
  async start() { this.timer=setInterval(()=>this.onChunk?.(new Int16Array(100),.04),100); }
  async stop() { clearInterval(this.timer); }
  clear() {} play() {} async microphones() { return []; }
}'''
REQ = {"label": "Data pipelines", "category": "problem_solving", "priority": "essential", "source_quote": "",
       "cv_evidence": "built reliable data processing systems", "cv_match": "direct", "assessment_method": "interview",
       "question": "How did you make a pipeline reliable?", "followups": [], "next_assessment": "",
       "criteria": {"weak": "Names tools only.", "adequate": "Explains one safeguard.", "strong": "Justifies safeguards and how they were checked."}}
PLAN = {"role": "General CV practice", "level": "No target seniority", "uncertainties": [], "deferred_requirements": [], "requirements": [REQ]}
REPORT = {"overall_score": 64, "requirements": [{"id": "r1", "status": "assessed", "score": 6, "evidence_turns": [2], "explanation": "Named retries and a row-count check."}], "verdict": "Clear answer, thin on checks.", "strengths": ["Specific example"], "weaknesses": ["No numbers"],
          "practice_next": ["Say how you verified the fix"], "questions": [], "next_focus": "evidence"}


def gemini(body):
    return {"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]}


def run(p, scenario):
    browser = p.chromium.launch(headless=True, executable_path=os.environ.get('PREP_BROWSER'))
    context = browser.new_context()
    calls, held, errors = [], [], []
    report_answers = list(scenario['report_answers'])          # what each report request gets, in order

    def route(r):
        url = urlsplit(r.request.url)
        if url.hostname == 'localhost':
            path = unquote(url.path).lstrip('/')
            if path.endswith('/'): path += 'index.html'
            file = (ROOT / path).resolve()
            if not file.is_relative_to(ROOT) or not file.is_file(): r.abort(); return
            if path == 'prep/app/audio.js': r.fulfill(body=AUDIO, content_type='text/javascript'); return
            r.fulfill(body=file.read_bytes(), content_type=mimetypes.guess_type(file)[0] or 'application/octet-stream'); return
        if url.hostname.endswith('workers.dev'):
            cors = {'access-control-allow-origin': 'http://localhost'}
            if r.request.method == 'OPTIONS':
                r.fulfill(status=204, headers={**cors, 'access-control-allow-headers': 'content-type'}); return
            body = r.request.post_data_json or {}
            calls.append((url.path, body.get('stage'), body.get('model')))
            status, result = 200, {}
            if url.path == '/mock/config': result = {'demo': {'seconds': 420}, 'plans': {}, 'region': 'in'}
            elif url.path == '/mock/demo/start': result = {'ok': True, 'demo': 'a' * 24, 'token': 'fake-token', 'seconds': 420}
            elif url.path == '/mock/demo/generate' and body.get('stage') == 'plan': result = gemini(PLAN)
            elif url.path == '/mock/demo/generate':
                answer = report_answers.pop(0)
                if answer == 'hold': held.append(r); return             # answered later, by the test
                status, result = (200, gemini(REPORT)) if answer == 200 else (answer, {'error': {'message': 'Gemini too slow'}})
            r.fulfill(status=status, json=result, headers=cors); return
        r.abort()

    def live(ws):
        def message(raw):
            m = json.loads(raw)
            if 'setup' in m: ws.send(json.dumps({'setupComplete': {}}))
            elif 'clientContent' in m:            # the opening line: one question, one answer
                ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'Tell me about a pipeline you made reliable.'}}}))
                ws.send(json.dumps({'serverContent': {'turnComplete': True}}))
                ws.send(json.dumps({'serverContent': {'inputTranscription': {'text': 'I added retries and checked row counts after every load.'}}}))
                ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'How did you check it worked?'}, 'turnComplete': True}}))
        ws.on_message(message)

    context.route('**/*', route)
    context.route_web_socket(re.compile(r'wss://generativelanguage\.googleapis\.com/.*'), live)
    page = context.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('dialog', lambda d: d.accept())                       # "End the interview now and get your report?"
    page.goto('http://localhost/prep/app/', wait_until='networkidle')
    page.locator('#cv').fill('I am a backend engineer. I built reliable data processing systems and worked on customer integrations with my team.')
    page.locator('#practice-focus').select_option('general_cv')
    page.locator('#to-key').click()                               # one click: straight into the call
    try: expect(page.locator('#line')).to_contain_text('check it worked', timeout=20000)   # the answer is in the transcript
    except AssertionError: raise AssertionError(('the call never ran', page.locator('#live-notice').inner_text(), calls, errors))
    page.locator('#end').click()
    for _ in range(100):
        if held: break
        page.wait_for_timeout(100)
    assert held, ('the report was never asked for', calls)
    scenario['while_writing'](page, calls)
    held.pop().fulfill(status=504, json={'error': {'message': 'Gemini too slow'}}, headers={'access-control-allow-origin': 'http://localhost'})
    scenario['after'](page, calls)
    assert not report_answers, ('unused report answers', report_answers)
    assert not errors, errors
    browser.close()
    return [c for c in calls if c[0] == '/mock/demo/generate' and c[1] == 'report']


def demo_starts(calls):
    return sum(1 for c in calls if c[0] == '/mock/demo/start')


# A report that fails on both models, then is written again from the same answers.
def failing_while(page, calls):
    expect(page.locator('#report-wait')).to_be_visible()
    expect(page.locator('#report-actions')).to_be_hidden()
    assert demo_starts(calls) == 1


def failing_after(page, calls):
    expect(page.locator('#report-retry')).to_be_visible(timeout=10000)
    expect(page.locator('#report-actions')).to_be_visible()
    page.locator('#report-retry').click()
    expect(page.locator('#report-wait')).to_be_hidden(timeout=10000)
    expect(page.locator('#report')).to_contain_text('Clear answer, thin on checks.')
    assert demo_starts(calls) == 1, 'writing the report again is not a new interview'


# The Bengaluru path: Practise again during the wait, the report landing while the next interview is set up.
def race_while(page, calls):
    page.evaluate("document.getElementById('again').click()")    # the old way out of the waiting screen
    page.locator('#start').click()
    expect(page.locator('#live-notice')).to_contain_text('still being written')
    assert demo_starts(calls) == 1


def race_after(page, calls):
    page.wait_for_function("window.__lastReport && window.__lastReport.report", timeout=10000)   # the demo's report has landed
    expect(page.locator('#start')).to_be_enabled()               # still showing the demo's Start: the old trap
    page.locator('#start').click()
    expect(page.locator('#start')).to_be_disabled()
    expect(page.locator('#s-pass')).to_contain_text('used up')             # the passes, not a call
    assert demo_starts(calls) == 1, 'a spent demo must not start another interview'
    assert sum(1 for c in calls if c[1] == 'plan') == 1


with sync_playwright() as p:
    first = run(p, {'report_answers': ['hold', 503, 504, 200], 'while_writing': failing_while, 'after': failing_after})
    assert [m for _, _, m in first] == ['gemini-3.1-flash-lite', 'gemini-3.6-flash'] * 2, first
    second = run(p, {'report_answers': ['hold', 200], 'while_writing': race_while, 'after': race_after})
    assert [m for _, _, m in second] == ['gemini-3.1-flash-lite', 'gemini-3.6-flash'], second
    print(json.dumps({'result': 'passed', 'retry_run': first, 'race_run': second}))
