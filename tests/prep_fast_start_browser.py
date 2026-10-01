"""One click from the CV screen to the interviewer, without waiting for the interview plan (1 Oct 2026).
Fake audio, a fake licence server and a fake Gemini Live socket: no request leaves this process.

1. Free demo: "Start interview" reaches the interviewer while the plan request is still unanswered; the plan,
   answered later, still reaches the report.
2. A plan that fails on both models never stops the interview; the report scores the broad areas instead.
3. A returning pass holder with a saved key starts in one click too, and the interviewer gets their earlier
   practice (coaching.js) in its instructions.

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
# When the page sends the interviewer its first stage direction: the moment it is asked to speak.
TIMING = '''(() => { const send = WebSocket.prototype.send;
  WebSocket.prototype.send = function (data) { if (!window.__openingAt && String(data).includes('clientContent')) window.__openingAt = performance.now(); return send.call(this, data); }; })();'''
REQ = {"label": "Data pipelines", "category": "problem_solving", "priority": "essential", "source_quote": "",
       "cv_evidence": "built reliable data processing systems", "cv_match": "direct", "assessment_method": "interview",
       "question": "How did you make a pipeline reliable?", "followups": [], "next_assessment": "",
       "criteria": {"weak": "Names tools only.", "adequate": "Explains one safeguard.", "strong": "Justifies safeguards and how they were checked."}}
CV = 'I am a backend engineer. I built reliable data processing systems and worked on customer integrations with my team.'
ROLE, LEVEL = 'Accountant', 'Entry-level / fresher'


def gemini(body):
    return {"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]}


def plan(role, level):
    return {"role": role, "level": level, "uncertainties": [], "deferred_requirements": [], "requirements": [REQ]}


REPORT = {"overall_score": 60, "requirements": [{"id": "r1", "status": "assessed", "score": 6, "evidence_turns": [2], "explanation": "Named retries."}],
          "competencies": [], "verdict": "Clear answer, thin on checks.", "strengths": ["Specific"], "weaknesses": ["No numbers"],
          "practice_next": ["Say how you verified it"], "questions": [], "next_focus": {"group": "ownership", "issue": "Says we", "drill": "Say I"}}


def run(p, *, plan_answer, storage=None, status=None, focus='general_cv'):
    browser = p.chromium.launch(headless=True, executable_path=os.environ.get('PREP_BROWSER'))
    context = browser.new_context()
    calls, held, errors, setups = [], [], [], []
    cors = {'access-control-allow-origin': 'http://localhost'}

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
            if r.request.method == 'OPTIONS':
                r.fulfill(status=204, headers={**cors, 'access-control-allow-headers': 'content-type'}); return
            body = r.request.post_data_json or {}
            calls.append((url.path, body.get('stage'), body.get('model'), body))
            code, result = 200, {}
            if url.path == '/mock/config': result = {'demo': {'seconds': 420}, 'plans': {}, 'region': 'in'}
            elif url.path == '/mock/status' and status: result = status
            elif url.path == '/mock/demo/start': result = {'ok': True, 'demo': 'a' * 24, 'token': 'fake-token', 'seconds': 420}
            elif url.path == '/mock/demo/generate' and body.get('stage') == 'plan':
                if plan_answer == 'hold': held.append(r); return
                code, result = plan_answer
            elif url.path == '/mock/demo/generate': result = gemini(REPORT)
            r.fulfill(status=code, json=result, headers=cors); return
        if url.hostname == 'generativelanguage.googleapis.com':     # a pass holder's own key: plan and report
            body = r.request.post_data_json or {}
            model = re.search(r'models/([^:]+)', url.path).group(1)
            calls.append(('google', 'plan' if 'requirements' in json.dumps(body.get('generationConfig', {})) and 'TRANSCRIPT' not in json.dumps(body) else 'report', model, body))
            if calls[-1][1] == 'plan': r.fulfill(json=gemini(plan(ROLE, LEVEL)))
            else: r.fulfill(json=gemini(REPORT))
            return
        r.abort()

    def live(ws):
        def message(raw):
            m = json.loads(raw)
            if 'setup' in m:
                setups.append(m['setup']['systemInstruction']['parts'][0]['text'])
                ws.send(json.dumps({'setupComplete': {}}))
            elif 'clientContent' in m:
                ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'Tell me about a pipeline you made reliable.'}, 'turnComplete': True}}))
                ws.send(json.dumps({'serverContent': {'inputTranscription': {'text': 'I added retries and checked row counts after every load.'}}}))
                ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'How did you check it worked?'}, 'turnComplete': True}}))
        ws.on_message(message)

    context.route('**/*', route)
    context.route_web_socket(re.compile(r'wss://generativelanguage\.googleapis\.com/.*'), live)
    context.add_init_script(TIMING)
    if storage:
        context.add_init_script('(() => { const s = %s; for (const k in s) localStorage.setItem(k, s[k]); })();' % json.dumps(storage))
    page = context.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost/prep/app/', wait_until='networkidle')
    page.locator('#cv').fill(CV)
    page.locator('#practice-focus').select_option(focus)
    if focus == 'role':
        page.locator('#target-role').fill(ROLE)
        page.locator('#target-level').select_option(LEVEL)
    expect(page.locator('#to-key')).to_have_text(re.compile('Start interview'))
    page.locator('#to-key').evaluate("b => { window.__clickAt = performance.now(); b.click(); }")
    try: expect(page.locator('#line')).to_contain_text('check it worked', timeout=15000)
    except AssertionError: raise AssertionError(('the call never ran', page.locator('#live-notice').inner_text(), [c[:3] for c in calls], errors))
    start_ms = page.evaluate('window.__openingAt - window.__clickAt')
    plan_was_waiting = bool(held)
    if held:
        held.pop().fulfill(json=gemini(plan('General CV practice', 'No target seniority')), headers=cors)
    page.locator('#end').click()
    expect(page.locator('#report-wait')).to_be_hidden(timeout=30000)
    expect(page.locator('#report')).to_contain_text('Clear answer, thin on checks.')
    assert not errors, errors
    browser.close()
    report = [c[3] for c in calls if c[1] == 'report']
    report_text = json.dumps(report[0]) if report else ''
    return {'start_ms': start_ms, 'plan_was_waiting': plan_was_waiting, 'setups': setups, 'report_text': report_text, 'calls': [c[:3] for c in calls]}


with sync_playwright() as p:
    # 1. The plan is still unanswered when the interviewer is asked to speak, and reaches the report later.
    held = run(p, plan_answer='hold')
    assert held['plan_was_waiting'], 'the interviewer spoke before the plan arrived'
    assert held['start_ms'] < 2500, held['start_ms']
    assert 'PREPARED ROLE ASSESSMENT PLAN' not in held['setups'][0], 'the interviewer works from the CV and JD'
    assert 'PRE-INTERVIEW ROLE REQUIREMENTS' in held['report_text'], 'the plan made during the call scores the report'

    # 2. A plan that fails on both models: the interview runs, and the report scores the broad areas.
    failed = run(p, plan_answer=(429, {'error': {'message': 'quota'}}))
    assert 'ASSESSMENT AREAS' in failed['report_text'] and 'PRE-INTERVIEW ROLE REQUIREMENTS' not in failed['report_text']
    assert [m for path, stage, m in failed['calls'] if stage == 'plan'] == ['gemini-3.1-flash-lite', 'gemini-3.6-flash']

    # 3. A returning pass holder: saved key, live pass, two earlier interviews for the same role.
    track = 'role_baseline|accountant|entry-level / fresher'
    past = [{'sv': 1, 'id': f'iv-{i}', 'kind': 'interview', 'at': at, 'minutes': 12, 'demo': False, 'track': track, 'score': score,
             'groups': {'ownership': {'score': 4.0, 'n': 1}, 'communication': {'score': 8.0, 'n': 1}},
             'questions': [{'q': q, 'score': 5}], 'focus': None}
            for i, (at, score, q) in enumerate([('2026-09-28T10:00:00Z', 55, 'How do you reconcile accounts?'),
                                                 ('2026-09-30T10:00:00Z', 62, 'Walk me through a month-end close.')])]
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    for i, s in enumerate(past): s['at'] = now.replace(microsecond=0).isoformat().replace('+00:00', 'Z') if i else s['at']
    passed = run(p, plan_answer=(500, {}), focus='role', storage={'ps_gemini_key': 'test-key', 'ps_history': json.dumps(past)},
                 status={'pass': {'valid': True, 'seconds_left': 86400, 'expires_at': '2026-10-30T00:00:00Z'}, 'trial': {'seconds_left': 0, 'total': 1200}})
    brief = passed['setups'][0]
    assert "THE CANDIDATE'S EARLIER PRACTICE" in brief, brief[-1500:]
    assert 'Weakest areas so far: Ownership (4.0/10)' in brief
    assert '- Walk me through a month-end close.' in brief
    assert not any(path == '/mock/demo/start' for path, _, _ in passed['calls']), 'a pass holder never uses the demo'
    print(json.dumps({'result': 'passed', 'demo_start_ms': round(held['start_ms']), 'pass_start_ms': round(passed['start_ms'])}))
