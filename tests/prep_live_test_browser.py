"""Live Sarthi's try-it test, kept apart from Prep Sarthi's free demo (3 Oct 2026).
Fake audio, a fake licence server and a fake Gemini Live socket: no request leaves this process.

The Windows app's guide opens /prep/app/?from=livesarthi. Before 3 Oct that visit used up the person's Prep demo,
ended on a Prep offer and counted in Prep's numbers. Checked here:
1. A test runs on /mock/livetest/start, never /mock/demo/start; no plan and no report is asked for; the demo is
   still unused afterwards; the end screen offers Live Sarthi (rupees in India), never a Prep pass; GA4 hears
   livetest_* only. The tab remembers the mode across a reload, and Test again starts a second test.
2. A refused test says why on the call screen and never opens Prep's passes.
3. Outside India the Live price is in dollars.
4. The same browser without ?from=livesarthi is ordinary Prep: the free demo, its report and Prep's events.

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
GA = '(() => { window.__ga = []; window.gtag = (...a) => { if (a[0] === "event") window.__ga.push(a[1]); }; })();'
CV = 'I am a backend engineer. I built reliable data processing systems and worked on customer integrations with my team.'
REPORT = {"overall_score": 60, "requirements": [], "competencies": [], "verdict": "Clear answer, thin on checks.", "strengths": ["Specific"],
          "weaknesses": ["No numbers"], "practice_next": ["Say how you verified it"], "questions": [],
          "next_focus": {"group": "ownership", "issue": "Says we", "drill": "Say I"}}


def gemini(body):
    return {"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]}


def open_app(p, *, query, test_answer=None, region='in'):
    browser = p.chromium.launch(headless=True, executable_path=os.environ.get('PREP_BROWSER'))
    context = browser.new_context()
    calls, errors = [], []
    cors = {'access-control-allow-origin': 'http://localhost'}

    def route(r):
        url = urlsplit(r.request.url)
        if url.hostname == 'localhost':
            path = unquote(url.path).lstrip('/')
            if path.endswith('/'): path += 'index.html'
            if path == 'assets/analytics.js': r.fulfill(body='', content_type='text/javascript'); return   # GA is the recorder above
            file = (ROOT / path).resolve()
            if not file.is_relative_to(ROOT) or not file.is_file(): r.abort(); return
            if path == 'prep/app/audio.js': r.fulfill(body=AUDIO, content_type='text/javascript'); return
            r.fulfill(body=file.read_bytes(), content_type=mimetypes.guess_type(file)[0] or 'application/octet-stream'); return
        if url.hostname.endswith('workers.dev'):
            if r.request.method == 'OPTIONS':
                r.fulfill(status=204, headers={**cors, 'access-control-allow-headers': 'content-type'}); return
            body = r.request.post_data_json or {}
            calls.append((url.path, body.get('stage')))
            result = {}
            if url.path == '/mock/config': result = {'demo': {'seconds': 420}, 'plans': {'m': {'amount': 99, 'days': 30, 'label': '30-Day Pass', 'usd': 999}}, 'region': region, 'google_client_id': 'x'}
            elif url.path == '/mock/livetest/start': result = test_answer or {'ok': True, 'test': 'b' * 24, 'token': 'fake-token', 'seconds': 420}
            elif url.path == '/mock/demo/start': result = {'ok': True, 'demo': 'a' * 24, 'token': 'fake-token', 'seconds': 420}
            elif url.path == '/mock/demo/generate': result = gemini(REPORT) if body.get('stage') != 'plan' else gemini({})
            r.fulfill(status=200, json=result, headers=cors); return
        r.abort()

    def live(ws):
        def message(raw):
            m = json.loads(raw)
            if 'setup' in m:
                ws.send(json.dumps({'setupComplete': {}}))
            elif 'clientContent' in m:
                ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'Tell me about a pipeline you made reliable.'}, 'turnComplete': True}}))
                ws.send(json.dumps({'serverContent': {'inputTranscription': {'text': 'I added retries and checked row counts after every load.'}}}))
                ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'How did you check it worked?'}, 'turnComplete': True}}))
        ws.on_message(message)

    context.route('**/*', route)
    context.route_web_socket(re.compile(r'wss://generativelanguage\.googleapis\.com/.*'), live)
    context.add_init_script(GA)
    page = context.new_page()
    page.on('pageerror', lambda e: errors.append(f'{e}\n{e.stack}'))
    page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost/prep/app/' + query, wait_until='networkidle')
    return browser, page, calls, errors


def start(page):
    # Once the page has asked the server what it may do (the chip leaves its placeholder): a click before that
    # deliberately stops at the Start button, since iOS keeps audio off without the click's own gesture.
    page.wait_for_function('document.getElementById("entitle").textContent !== "\\u2026"')
    page.locator('#cv').fill(CV)
    page.locator('#to-key').click()


def talk_and_end(page, calls, errors):
    try: expect(page.locator('#line')).to_contain_text('check it worked', timeout=15000)
    except AssertionError: raise AssertionError(('the call never ran', page.locator('#live-notice').inner_text(), calls, errors))
    page.locator('#end').click()


def events(page):
    return [e for e in page.evaluate('window.__ga')]


with sync_playwright() as p:
    # 1. A Live Sarthi test from start to finish.
    browser, page, calls, errors = open_app(p, query='?from=livesarthi&utm_source=interview-sarthi-app')
    expect(page.locator('#s-cv .label').first).to_have_text('Live Sarthi test')
    for hidden in ('#entitle', '#open-invite', '#open-progress'): expect(page.locator(hidden)).to_be_hidden()
    expect(page.locator('#practice-focus')).to_have_value('general_cv')       # a CV is all a test needs
    start(page)
    expect(page.locator('#left')).to_contain_text('Live Sarthi test', timeout=15000)
    talk_and_end(page, calls, errors)
    expect(page.locator('#s-livetest')).to_be_visible()
    expect(page.locator('#lt-price')).to_have_text('Passes from Rs 99 for 2 days.')
    expect(page.locator('#lt-buy')).to_have_attribute('href', '/live/#pricing')
    expect(page.locator('#s-report')).to_be_hidden()
    expect(page.locator('#s-pass')).to_be_hidden()
    paths = [c[0] for c in calls]
    assert '/mock/livetest/start' in paths and '/mock/demo/start' not in paths, paths
    assert '/mock/demo/generate' not in paths, 'a test asks for no plan and no report'
    assert page.evaluate('localStorage.getItem("ps_demo_used")') is None, 'the Prep demo is still unused'
    names = events(page)
    assert 'livetest_open' in names and 'livetest_start' in names and 'livetest_offer_shown' in names, names
    assert not [n for n in names if n.startswith('mock_')], names
    page.locator('#lt-buy').evaluate('a => a.addEventListener("click", e => e.preventDefault())')
    page.locator('#lt-buy').click()
    assert 'livetest_offer_click' in events(page)
    # Test again: a second test, still never the demo.
    page.locator('#lt-again').click()
    page.locator('#start').click()
    talk_and_end(page, calls, errors)
    expect(page.locator('#s-livetest')).to_be_visible()
    assert [c[0] for c in calls].count('/mock/livetest/start') == 2
    # A reload in the same tab is still a test (the address no longer carries ?from=).
    assert 'from=' not in page.url, page.url
    page.reload(wait_until='networkidle')
    expect(page.locator('#s-cv .label').first).to_have_text('Live Sarthi test')
    assert not errors, errors
    browser.close()

    # 2. Refused: the reason on the call screen, never Prep's passes.
    browser, page, calls, errors = open_app(p, query='?from=livesarthi', test_answer={'ok': False, 'reason': 'used'})
    start(page)
    expect(page.locator('#live-notice')).to_contain_text("today's tests on this PC", timeout=15000)
    expect(page.locator('#s-pass')).to_be_hidden()
    assert 'livetest_demo_refused' in events(page)
    assert not errors, errors
    browser.close()

    # 3. Outside India the Live price is in dollars.
    browser, page, calls, errors = open_app(p, query='?from=livesarthi', region='intl')
    start(page)
    talk_and_end(page, calls, errors)
    expect(page.locator('#lt-price')).to_have_text('Passes from $9.99 for 2 days.')
    browser.close()

    # 4. Without ?from=livesarthi this is ordinary Prep: the demo, its report, Prep's own events.
    browser, page, calls, errors = open_app(p, query='')
    expect(page.locator('#s-cv .label').first).to_have_text('Step 1 of 3')
    expect(page.locator('#entitle')).to_be_visible()
    page.locator('#practice-focus').select_option('general_cv')
    start(page)
    talk_and_end(page, calls, errors)
    expect(page.locator('#report')).to_contain_text('Clear answer, thin on checks.', timeout=30000)
    paths = [c[0] for c in calls]
    assert '/mock/demo/start' in paths and '/mock/livetest/start' not in paths, paths
    names = events(page)
    assert 'mock_demo_start' in names and 'mock_demo_end' in names and not [n for n in names if n.startswith('livetest_')], names
    assert not errors, errors
    browser.close()
    print(json.dumps({'result': 'passed'}))
