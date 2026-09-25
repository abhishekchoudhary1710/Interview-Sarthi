"""Apply homepage browser QA. Blocks external traffic; writes ignored screenshots.

Run with Python Playwright and an installed Chromium browser. Optionally set
BROWSER_EXECUTABLE to a local Chromium binary.
"""
import json, mimetypes, os
from pathlib import Path
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'.seo-preview/apply-redesign'
OUT.mkdir(parents=True,exist_ok=True)
missing=[]
def route_local(route):
    url = urlsplit(route.request.url)
    if url.hostname != 'localhost':
        route.abort()
        return
    name=unquote(url.path).lstrip('/') or 'index.html'
    if name.endswith('/'): name+='index.html'
    file=(ROOT/name).resolve()
    if not file.is_relative_to(ROOT) or not file.is_file():
        missing.append(name)
        route.fulfill(status=404,body='Not found')
        return
    route.fulfill(status=200,body=file.read_bytes(),content_type=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('BROWSER_EXECUTABLE'),headless=True)
    context=browser.new_context(reduced_motion='reduce')
    context.route('**/*',route_local)
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda error: errors.append(str(error)))
    for width in (320,360,390,768,1024,1440):
        page.set_viewport_size({'width':width,'height':960})
        page.goto('http://localhost/apply/',wait_until='networkidle')
        assert page.locator('h1').count()==1
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), f'Overflow at {width}'
        if width in (390,1440):
            page.screenshot(path=str(OUT/f'apply-{width}.png'),full_page=True)
            page.screenshot(path=str(OUT/f'apply-{width}-top.png'))
        if width < 760:
            button=page.get_by_role('button',name='Toggle navigation')
            button.click()
            assert button.get_attribute('aria-expanded')=='true'
            page.get_by_role('navigation',name='Main navigation').get_by_role('link',name='Features').click()
            assert button.get_attribute('aria-expanded')=='false'
            button.click()
            page.keyboard.press('Escape')
            assert button.get_attribute('aria-expanded')=='false'
        # Every walkthrough panel must fit and remain selectable with a keyboard.
        for tab in page.get_by_role('tab').all():
            tab.click()
            panel=page.locator('#'+tab.get_attribute('aria-controls'))
            assert panel.is_visible()
            assert not panel.evaluate('(el)=>el.scrollHeight > el.clientHeight + 1'), f'Panel clips at {width}'
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
        page.get_by_role('tab').first.focus()
        page.keyboard.press('ArrowRight')
        assert page.locator('#tab-match').get_attribute('aria-selected')=='true'
        page.keyboard.press('End')
        assert page.locator('#tab-fill').get_attribute('aria-selected')=='true'
        page.keyboard.press('Home')
        assert page.locator('#tab-search').get_attribute('aria-selected')=='true'
        assert page.get_by_role('button',name='Play preview').is_visible()
        page.locator('.screenshot-link').click()
        assert page.locator('dialog').is_visible()
        page.keyboard.press('Escape')
        assert not page.locator('dialog').is_visible()
        assert page.locator('.screenshot-link').evaluate('(el)=>el===document.activeElement')
        question=page.get_by_text('Can I use ApplySarthi on my phone?',exact=True)
        question.click()
        assert question.locator('..').get_attribute('open') is not None
        schema=json.loads(page.locator('script[type="application/ld+json"]').inner_text())
        faq=next(n for n in schema['@graph'] if n['@type']=='FAQPage')
        visible=page.locator('.faq-list details')
        assert visible.count()==len(faq['mainEntity'])
        for i,item in enumerate(faq['mainEntity']):
            assert visible.nth(i).locator('summary').inner_text()==item['name']
            assert visible.nth(i).locator('p').text_content()==item['acceptedAnswer']['text']
        for image in page.locator('main img').all():
            image.scroll_into_view_if_needed()
            assert image.evaluate('(el)=>el.complete && el.naturalWidth>0')
    nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
    nojs.route('**/*',route_local)
    fallback=nojs.new_page()
    fallback.goto('http://localhost/apply/',wait_until='load')
    assert fallback.get_by_role('navigation',name='Main navigation').is_visible()
    fallback.get_by_text('Can I use ApplySarthi on my phone?',exact=True).click()
    assert fallback.locator('.faq-list details').nth(4).get_attribute('open') is not None
    assert not fallback.evaluate('document.documentElement.scrollWidth > innerWidth')
    # Autoplay advances only while visible, pauses on selection and honors motion changes.
    motion=browser.new_context(viewport={'width':1440,'height':1000})
    motion.route('**/*',route_local)
    demo=motion.new_page()
    demo.on('pageerror',lambda error: errors.append(str(error)))
    demo.goto('http://localhost/apply/',wait_until='networkidle')
    demo.wait_for_function("document.querySelector('.product-visual').dataset.step === '1'",timeout=9000)
    demo.get_by_role('tab').last.click()
    assert demo.get_by_role('button',name='Play preview').is_visible()
    demo.get_by_role('button',name='Play preview').click()
    demo.get_by_role('heading',level=1).click()
    demo.wait_for_function("document.querySelector('.product-visual').dataset.step === '0'",timeout=9000)
    demo.emulate_media(reduced_motion='reduce')
    assert demo.get_by_role('button',name='Play preview').is_visible()
    assert not demo.locator('.product-visual').evaluate("el=>el.classList.contains('is-playing')")
    assert not missing, missing
    assert not errors, errors
    (OUT/'checks.json').write_text(json.dumps({'widths':[320,360,390,768,1024,1440],'overflow':False,'browser_errors':errors,'missing_assets':missing,'navigation':'passed','screenshot_dialog_and_focus':'passed','faq_schema_matches_visible_copy':True,'javascript_disabled':'passed','walkthrough_tabs_keyboard_autoplay_reduced_motion':'passed'},indent=2)+'\n')
    print('PASS: six viewport sizes; menu, dialog, focus, FAQ/schema, assets and no-JS fallback.')
    browser.close()
