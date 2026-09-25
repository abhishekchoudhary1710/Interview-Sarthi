"""Optional browser QA: pip install playwright, then install Chromium or use Edge.
Serves repository responses in memory; blocks all external requests and payments.
"""
import json
import mimetypes
from pathlib import Path
import sys
from urllib.parse import parse_qs, unquote, urlsplit
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from seo_audit import public_pages
ARTIFACTS = ROOT / '.seo-preview'
ARTIFACTS.mkdir(exist_ok=True)


def route_local(route):
    url = urlsplit(route.request.url)
    if url.hostname != 'localhost':
        route.abort()
        return
    path = unquote(url.path).lstrip('/') or 'index.html'
    if path.endswith('/'):
        path += 'index.html'
    file = (ROOT / path).resolve()
    if not file.is_relative_to(ROOT) or not file.is_file():
        route.fulfill(status=404, body='Not found')
        return
    route.fulfill(status=200, body=file.read_bytes(), content_type=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')


with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    context = browser.new_context()
    context.route('**/*', route_local)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    checked = []
    for width in (390, 1366):
        page.set_viewport_size({'width':width, 'height':900})
        for path in public_pages():
            page.goto('http://localhost/' + path, wait_until='load')
            page.evaluate("document.querySelectorAll('.rv').forEach(el=>el.classList.add('in'))")
            overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
            if overflow:
                errors.append(f'{path}: horizontal viewport overflow at {width}px')
            checked.append({'page':path,'width':width,'overflow':overflow})
            if path in ('index.html','live/index.html','facts.html','best-ai-interview-assistant-india.html','guides/index.html'):
                page.screenshot(path=str(ARTIFACTS / f"{path.replace('/','-')}-{width}.png"),full_page=True)
    page.goto('http://localhost/live/',wait_until='load')
    monthly = page.get_by_role('link',name='Buy 1-Month Pass',exact=False)
    assert monthly.count()==2
    for item in monthly.all():
        assert 'license.interviewsarthi.com/buy?plan=30d' in item.get_attribute('href')
    # Both monthly CTAs, including the closing one below the region script,
    # must honor the visible currency choice and remember it after a reload.
    for region, label in (('intl', 'outside India (USD)'), ('in', 'India')):
        if page.locator('#regionname').inner_text() != label:
            page.locator('#regionswap').click()
        for reload in (False, True):
            if reload:
                page.reload(wait_until='load')
            assert page.locator('#regionname').inner_text() == label
            assert monthly.count() == 2
            for item in monthly.all():
                query = parse_qs(urlsplit(item.get_attribute('href')).query)
                assert query['plan'] == ['30d']
                assert query['region'] == [region]
    page.goto('http://localhost/thanks.html?license_key=TEST-RECEIPT&email=test@example.invalid',wait_until='load')
    assert page.locator('#keyval').inner_text() == 'TEST-RECEIPT'
    assert urlsplit(page.url).query == ''
    assert page.locator('#keywrap').is_visible()
    assert page.evaluate("dataLayer.filter(x=>x[0]==='event' && x[1]==='purchase').length") == 1
    assert not page.evaluate("Array.from(document.scripts).some(s=>s.src.includes('clarity.ms'))")
    page.goto('http://localhost/?utm_source=chatgpt.com',wait_until='load')
    assert page.evaluate("dataLayer.some(x=>x[1]==='ai_referral_visit' && x[2].ai_source==='chatgpt')")
    browser.close()
    output = {'viewport_checks':len(checked),'errors':errors,'checks':checked,'receipt_and_checkout':'passed'}
    (ARTIFACTS/'browser-results.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in output.items() if key!='checks'}))
    sys.exit(bool(errors))
