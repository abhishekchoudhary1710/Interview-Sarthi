"""Local browser check for clean interview UI. No microphone, AI or billing calls.

Requires Python Playwright and Chromium; BROWSER_EXECUTABLE optionally selects it.
The test exposes callbacks only in its intercepted response, never in shipped code.
"""
import mimetypes
import os
from pathlib import Path
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HOOK = '''
window.__prepUiCheck = {
  log, onTranscript,
  open() { S.ent = { kind: 'trial', secondsLeft: 1200 }; preLive(); }
};
'''

def local(route):
    url = urlsplit(route.request.url)
    if url.hostname != 'localhost':
        route.abort()
        return
    name = unquote(url.path).lstrip('/') or 'index.html'
    if name.endswith('/'):
        name += 'index.html'
    file = (ROOT / name).resolve()
    if not file.is_relative_to(ROOT) or not file.is_file():
        route.fulfill(status=404, body='Not found')
        return
    data = file.read_bytes()
    if name == 'prep/app/app.js':
        data += HOOK.encode()
    route.fulfill(status=200, body=data, content_type=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('BROWSER_EXECUTABLE'), headless=True)
    context = browser.new_context(reduced_motion='reduce')
    context.route('**/*', local)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    for width in (390, 1366):
        page.set_viewport_size({'width': width, 'height': 900})
        for query, enabled in (('', False), ('?diagnostics=1', True), ('', False)):
            page.goto('http://localhost/prep/app/' + query, wait_until='networkidle')
            page.wait_for_function('!!window.__prepUiCheck')
            assert page.locator('#diagnostics').is_visible() == enabled
            page.evaluate('window.__prepUiCheck.open()')
            page.evaluate('''() => {
              window.__prepUiCheck.log('connection_status', { ready: true });
              window.__prepUiCheck.onTranscript({who: 'interviewer', text: 'Tell me about your project.'}, true);
              window.__prepUiCheck.onTranscript({who: 'candidate', text: 'I built a reporting tool.'}, true);
            }''')
            assert page.locator('#s-live').is_visible()
            assert page.locator('#line').text_content() == 'Tell me about your project.'
            assert 'I built a reporting tool.' in page.locator('#youline').text_content()
            assert page.locator('#diagnostics').is_visible() == enabled
            if enabled:
                assert 'connection_status' in page.locator('#log').text_content()
                assert page.locator('#transcript .bubble').count() == 2
            else:
                assert page.locator('#log').text_content() == ''
                assert page.locator('#transcript').text_content() == ''
                assert not page.get_by_text('Diagnostics', exact=True).is_visible()
                out = ROOT / '.seo-preview'
                out.mkdir(exist_ok=True)
                page.screenshot(path=str(out / f'prep-clean-interview-{width}.png'), full_page=True)
    assert not errors, errors
    browser.close()
    print('PASS: no normal logs or duplicate transcript; captions, support opt-in and clean reload work on desktop/mobile.')
