"""Exercise the real Start button and diagnostic uploads with fake audio and network.
No Gemini, production database, payment or microphone requests leave this process.
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
  constructor() { this.sampleRate=48000; this.micLabel='PRIVATE MICROPHONE'; }
  async start() { this.timer=setInterval(()=>this.onChunk?.(new Int16Array(100),.04),100); }
  async stop() { clearInterval(this.timer); }
  clear() {} play() {} async microphones() { return []; }
}'''

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=os.environ.get('PREP_BROWSER'))
    context = browser.new_context()
    requests, events, errors = [], [], []
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
                r.fulfill(status=204, headers={'access-control-allow-origin':'http://localhost','access-control-allow-headers':'content-type'}); return
            body = r.request.post_data_json or {}
            requests.append((url.path, body))
            status, result = 200, {}
            if url.path == '/mock/config': result = {'demo':{'seconds':420},'plans':{},'region':'in'}
            elif url.path == '/mock/demo/start': result = {'ok':True,'demo':'a'*24,'token':'PRIVATE LIVE TOKEN','seconds':420}
            elif url.path == '/mock/demo/generate': status, result = 429, {'error':{'message':'Quota exhausted'}}
            elif url.path == '/mock/diagnostics/events': events.extend(body['events'])
            r.fulfill(status=status, json=result, headers={'access-control-allow-origin':'http://localhost'}); return
        r.abort()
    def live(ws):     # a fake Gemini Live: it connects and the interviewer asks the first question
        def message(raw):
            m = json.loads(raw)
            if 'setup' in m: ws.send(json.dumps({'setupComplete': {}}))
            elif 'clientContent' in m: ws.send(json.dumps({'serverContent': {'outputTranscription': {'text': 'Tell me about yourself.'}, 'turnComplete': True}}))
        ws.on_message(message)
    context.route('**/*', route)
    context.route_web_socket(re.compile(r'wss://generativelanguage\.googleapis\.com/.*'), live)
    page = context.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto('http://localhost/prep/app/', wait_until='networkidle')
    page.locator('#cv').fill('PRIVATE CV: I am a backend engineer. I built reliable data processing systems and worked on customer integrations with my team.')
    page.locator('#practice-focus').select_option('general_cv')
    page.locator('#to-key').click()                     # one click: straight into the call
    # The plan fails on both models (429), in the background: the interview goes ahead without it.
    expect(page.locator('#line')).to_contain_text('Tell me about yourself', timeout=10000)
    page.wait_for_function("document.querySelector('#livetag').textContent === 'Live'")
    for _ in range(50):
        if sum(1 for path, b in requests if path == '/mock/demo/generate') >= 2: break
        page.wait_for_timeout(100)
    page.evaluate("async () => { const d=await import('/prep/app/diagnostics.js'); await d.flushDiagnostics(); await d.flushDiagnostics(); }")
    names = [e['name'] for e in events]
    for name in ['attempt_start','mic','preparation_start','demo_requested','demo_granted','preparation_ready','request_start','model_fallback','preparation_failed','connection_attempt','connected']:
        assert name in names, (name, names)  # a failed plan never stops the call
    diagnostic_bodies = [b for path,b in requests if path.startswith('/mock/diagnostics/')]
    assert 'PRIVATE' not in json.dumps(diagnostic_bodies)
    attempt = next(b['id'] for path,b in requests if path == '/mock/diagnostics/start')
    model_requests = [b for path,b in requests if path == '/mock/demo/generate']
    assert len(model_requests) == 2
    assert all(b['diagnostics']['id'] == attempt and b['stage']=='plan' for b in model_requests)
    assert all(any(e['data'].get('request_id') == b['diagnostics']['request_id'] for e in events) for b in model_requests)
    assert not errors, errors
    print(json.dumps({'result':'passed','events':names,'browser_errors':errors}))
    browser.close()
