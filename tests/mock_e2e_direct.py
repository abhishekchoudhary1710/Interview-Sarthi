"""Buying must not depend on the interview setup. Three journeys, sandbox only:

1. The pricing page's "Get the 7-day pass" opens the app at checkout for that
   pass; with no Gemini key anywhere, sign in, pay, land in the account, and
   "Start practising" leads into the interview setup.
2. The same buyer on a brand-new browser finds "Already bought a pass? Sign in"
   and sees the pass without pressing Buy.
3. Someone who reaches Cashfree and presses Back is told plainly that nothing
   was paid, within seconds, instead of a long "confirming" wait.

    python tests/mock_e2e_direct.py        (local server on 8765; no Gemini key needed)
"""
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".seo-preview"
OUT.mkdir(exist_ok=True)
BASE = os.environ.get("PS_BASE", "http://127.0.0.1:8765")
EMAIL = f"direct{int(time.time())}@example.com"


def pay_in_simulator(page):
    page.wait_for_url("**cashfree**", timeout=30000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2500)
    page.get_by_text("Test Wallet").first.click()
    page.wait_for_timeout(3000)
    for label in ("Pay", "Proceed", "Continue", "Pay Now"):
        try:
            page.get_by_role("button", name=label).first.click(timeout=2500)
            break
        except Exception:
            pass
    page.wait_for_timeout(4000)
    page.locator("input").first.fill("111000")
    page.get_by_text("SUCCESS", exact=True).first.click(timeout=5000)
    page.get_by_role("button", name="Submit").click(timeout=5000)
    page.wait_for_url("**/mock/app/**", timeout=60000)


def main() -> int:
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---- 1. straight from the pricing page, no key anywhere
        ctx = browser.new_context(viewport={"width": 420, "height": 900}, is_mobile=True)
        page = ctx.new_page()
        page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        page.goto(f"{BASE}/mock/#pricing", wait_until="networkidle")
        href = page.get_attribute('.pricecard.best a.pill', "href")
        print("1. pricing button goes to:", href)
        page.click('.pricecard.best a.pill')
        page.wait_for_selector("#s-pass.on", timeout=15000)
        page.wait_for_selector("#checkout", state="visible", timeout=10000)
        print("   opens at checkout     :", page.text_content("#checkout-plan"), "| url cleaned:", "buy=" not in page.url)
        page.screenshot(path=str(OUT / "direct-1-checkout.png"), full_page=True)
        if "7-Day" not in (page.text_content("#checkout-plan") or ""):
            failures.append("the pricing button did not open checkout for the 7-day pass")
        page.fill("#testlogin-email", EMAIL)
        page.click("#testlogin-go")
        page.wait_for_selector("#pass-pay", state="visible", timeout=15000)
        print("   signed in with no key :", page.text_content("#pass-who2"))
        page.fill("#phone", "9876543210")
        page.click("#pay")
        pay_in_simulator(page)
        page.wait_for_selector("#account-card", state="visible", timeout=120000)
        print("   after paying          :", page.text_content("#pass-notice"), "|", page.text_content("#pass-days"))
        page.click("#go-practise")
        page.wait_for_selector("#s-cv.on", timeout=5000)
        print("   Start practising      : leads to the CV step, chip", repr(page.text_content("#entitle")))
        if "Pass" not in (page.text_content("#entitle") or ""):
            failures.append("chip lost the pass after Start practising")
        ctx.close()

        # ---- 2. the same buyer on a new device
        ctx = browser.new_context(viewport={"width": 420, "height": 900}, is_mobile=True)
        page = ctx.new_page()
        page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        page.goto(f"{BASE}/mock/app/", wait_until="networkidle")
        page.wait_for_function("document.getElementById('entitle').textContent.trim() !== '…'", timeout=15000)
        print("2. new device chip       :", repr(page.text_content("#entitle")))
        page.click("#entitle")
        page.wait_for_selector("#have-pass", state="visible", timeout=8000)
        page.click("#have-pass")
        page.wait_for_selector("#checkout", state="visible")
        print("   sign-in only          :", page.text_content("#checkout-label"), "| pay form hidden:", not page.locator("#pass-pay").is_visible())
        page.screenshot(path=str(OUT / "direct-2-signin.png"), full_page=True)
        page.fill("#testlogin-email", EMAIL)
        page.click("#testlogin-go")
        page.wait_for_selector("#account-card", state="visible", timeout=15000)
        print("   pass found            :", page.text_content("#pass-notice"), "|", page.text_content("#pass-days"))

        # ---- 3. backing out of Cashfree
        page.click("#extend")
        page.wait_for_selector("#buy-block", state="visible")
        page.click("#buy-cta")
        page.wait_for_selector("#pass-pay", state="visible")
        page.fill("#phone", "9876543210")
        page.click("#pay")
        page.wait_for_url("**cashfree**", timeout=30000)
        page.wait_for_timeout(2500)
        t0 = time.time()
        page.goto(f"{BASE}/mock/app/", wait_until="networkidle")          # the Back button, in effect
        page.wait_for_function("/not completed/.test(document.getElementById('pass-notice').textContent)", timeout=40000)
        print(f"3. backed out of Cashfree: told in {time.time() - t0:.0f}s ->", page.text_content("#pass-notice"))
        page.screenshot(path=str(OUT / "direct-3-abandoned.png"), full_page=True)
        ctx.close()
        browser.close()
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
