"""Verify country-specific prices throughout demo checkout, without real payments.

Reuses the offline app fixture. Screenshots include dollar prices at desktop and
phone sizes; PREP_REVIEW_DIR and PREP_BROWSER select the output and browser.
"""
import json
import mimetypes
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright, expect
from prep_demo_buy_browser import App, BASE, OUT, ROOT


def verify_initial_price(p, width, height):
    import os
    browser = p.chromium.launch(headless=True, executable_path=os.environ.get('PREP_BROWSER'))
    context = browser.new_context(viewport={'width': width, 'height': height})

    def route(r):
        url = urlsplit(r.request.url)
        if url.hostname != 'localhost': r.abort(); return
        path = unquote(url.path).lstrip('/')
        if path.endswith('/'): path += 'index.html'
        file = (ROOT / path).resolve()
        # Prevent config and modules from replacing the initial checkout paint.
        if file.suffix == '.js' or not file.is_relative_to(ROOT) or not file.is_file(): r.abort(); return
        r.fulfill(body=file.read_bytes(), content_type=mimetypes.guess_type(file)[0] or 'application/octet-stream')

    context.route('**/*', route)
    page = context.new_page()
    page.goto(BASE + '/prep/app/?buy=m')
    expect(page.locator('#checkout-plan')).to_have_text('30-Day Pass · Loading price…')
    expect(page.locator('.plan[data-plan="m"] .price')).to_have_text('Loading price…')
    expect(page.locator('#pay')).to_have_text('Pay securely →')
    browser.close()


def assert_dollars(app):
    expect(app.page.locator('.plan[data-plan="m"] .price')).to_have_text('$9.99')
    expect(app.page.locator('#checkout-plan')).to_have_text('30-Day Pass · $9.99')
    expect(app.page.locator('#pay')).to_have_text('Pay $9.99 →')
    expect(app.page.locator('#phone')).to_be_hidden()


def main():
    checks = []
    with sync_playwright() as p:
        for width, height in ((1366, 768), (390, 844)):
            verify_initial_price(p, width, height)
            app = App(p, (width, height), region='intl')
            app.start()
            expect(app.page.locator('#demo-call-price')).to_have_text('$9.99')
            app.shot('call-intl', width)
            app.page.locator('#end').click()
            expect(app.page.locator('#demo-exit-buy')).to_have_text('Get unlimited practice · $9.99')
            app.shot('end-card-intl', width)
            app.buy('demo_exit')
            assert_dollars(app)
            app.shot('checkout-intl', width)
            app.page.locator('#testlogin-go').click()
            expect(app.page.locator('#pass-pay')).to_be_visible()
            assert_dollars(app)
            app.release_report()
            app.page.locator('#pass-back').click()
            expect(app.page.locator('#report-offer-go')).to_have_text('Get 30 days for $9.99 →')
            app.close()

            for status in ('paid', 'failed'):
                app = App(p, (width, height), region='intl')
                app.start(); app.buy(); assert_dollars(app)
                app.release_report()
                app.pay_and_return(status, 'demo_call')
                if status == 'paid':
                    purchase = app.events('purchase')[0]
                    assert purchase['currency'] == 'USD' and purchase['value'] == 9.99, purchase
                else: expect(app.page.locator('#report-offer-go')).to_have_text('Get 30 days for $9.99 →')
                app.shot(status + '-return-intl', width)
                app.close()
            checks.append({'viewport': [width, height], 'outside_india': '$9.99', 'first_paint': 'no rupee fallback'})
    result = {'result': 'passed', 'checks': checks, 'payment_provider': 'Dodo (simulated)'}
    (OUT / 'currency-verification.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
