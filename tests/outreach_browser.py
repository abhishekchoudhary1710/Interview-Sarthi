"""Optional Playwright QA against local files; blocks analytics, APIs and payments."""
import argparse
import json
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def local_route(route):
    url = urlsplit(route.request.url)
    if url.hostname != 'interviewsarthi.com':
        route.abort()
        return
    name = unquote(url.path).lstrip('/') or 'index.html'
    if name.endswith('/'):
        name += 'index.html'
    target = (ROOT / name).resolve()
    if not target.is_relative_to(ROOT) or not target.is_file():
        route.fulfill(status=404, body='Not found')
        return
    route.fulfill(body=target.read_bytes(),
                  content_type=mimetypes.guess_type(str(target))[0] or 'application/octet-stream')


def event(page, name):
    return page.evaluate('(name) => dataLayer.filter(x => x[0] === "event" && x[1] === name).at(-1)?.[2]', name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    errors = []
    with sync_playwright() as playwright:
        options = {'headless': True}
        if args.executable:
            options['executable_path'] = str(args.executable)
        browser = playwright.chromium.launch(**options)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                'AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36')
        context.route('**/*', local_route)
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        entry = 'https://interviewsarthi.com/live/international.html?utm_source=career_creator&' \
                'utm_medium=referral&utm_campaign=international_us_live&utm_content=software-review-01'
        page.goto(entry, wait_until='load')
        assert event(page, 'outreach_visit')['outreach_campaign'] == 'international_us_live'
        page.goto('https://interviewsarthi.com/live/?region=intl', wait_until='load')
        assert page.evaluate('dataLayer.find(x => x[0] === "config")[2].campaign_name') is None
        page.evaluate('document.addEventListener("click", e => e.preventDefault())')
        page.get_by_role('link', name='Buy 1-Month Pass', exact=True).first.click()
        checkout = event(page, 'begin_checkout')
        assert checkout['outreach_content'] == 'software-review-01'
        assert checkout['currency'] == 'USD' and checkout['value'] == 29.99
        # A receipt in another tab uses only the validated checkout context.
        receipt = context.new_page()
        receipt.on('pageerror', lambda error: errors.append(str(error)))
        receipt.goto('https://interviewsarthi.com/thanks.html?license_key=QA-SECRET',
                     referer='https://checkout.dodopayments.com/', wait_until='load')
        purchase = event(receipt, 'purchase')
        assert purchase['outreach_campaign'] == 'international_us_live'
        assert purchase['currency'] == 'USD'
        assert receipt.evaluate('dataLayer.find(x => x[0] === "config")[2].ignore_referrer')
        assert not receipt.evaluate('JSON.stringify(dataLayer).includes("QA-SECRET")')
        receipt.reload(wait_until='load')
        assert event(receipt, 'purchase') is None
        page.goto('https://interviewsarthi.com/prep/?utm_source=reddit&utm_medium=referral&'
                  'utm_campaign=international_uk_prep&utm_content=data-community-01', wait_until='load')
        assert event(page, 'outreach_visit')['target_market'] == 'uk'
        page.goto('https://interviewsarthi.com/live/', referer='https://www.google.com/', wait_until='load')
        page.evaluate('sarthiTrack("download_click", {method:"store"})')
        assert 'outreach_campaign' not in event(page, 'download_click')
        browser.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'entry_navigation_checkout_receipt': 'passed',
                                       'prep_entry_and_unrelated_referral': 'passed',
                                       'external_requests': 'blocked', 'errors': errors}, indent=2) + '\n')
    assert not errors, errors
    print('Browser campaign entry, navigation, checkout, receipt and referral checks passed.')
