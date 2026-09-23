"""Buy a Prep Sarthi pass end to end against the SANDBOX worker and Cashfree sandbox.

Local preview only (the page talks to the sandbox worker when served from
127.0.0.1, and that worker accepts a made-up sign-in). It walks the buyer's
path in the order the screen offers it: choose a pass, press Buy, sign in,
leave a number, pay, and land back in your own account. Then it reloads the
page to prove a returning buyer sees their pass straight away instead of the
free-minutes chip. Screenshots land in .seo-preview/.

    PS_KEY=... python tests/mock_e2e_buy.py [stop-at-checkout]
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
KEY = os.environ["PS_KEY"]
STOP = len(sys.argv) > 1 and sys.argv[1] == "stop-at-checkout"
EMAIL = f"buyer{int(time.time())}@example.com"
CV = "Riya Sharma\nBackend engineer, three years.\n- Built a payments service in Java and Spring Boot; cut failed transactions by 30%.\n- Moved nightly jobs to Kafka streams."


def main() -> int:
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"])
        context = browser.new_context(viewport={"width": 420, "height": 900}, is_mobile=True)
        page = context.new_page()
        page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        page.goto(f"{BASE}/prep/app/", wait_until="networkidle")
        page.fill("#cv", CV)
        page.select_option("#practice-focus", "general_cv")
        page.click("#to-key")
        page.fill("#key", KEY)
        page.click("#check-key")
        page.wait_for_selector("#s-live.on", timeout=20000)
        print("chip before  :", page.text_content("#entitle"))

        # step 1: the two passes and one Buy button. No sign-in in the way yet.
        page.click("#entitle")
        page.wait_for_selector("#s-pass.on")
        page.wait_for_selector("#buy-block", state="visible", timeout=8000)
        print("step 1       :", page.text_content("#buy-cta").strip(), "| checkout hidden:", not page.locator("#checkout").is_visible())
        page.screenshot(path=str(OUT / "buy-1-plans.png"), full_page=True)
        if page.locator("#checkout").is_visible():
            failures.append("the sign-in step is visible before Buy is pressed")

        # a different plan changes the button
        page.click('.plan[data-plan="m"]')
        if "30-day" not in page.text_content("#buy-cta"):
            failures.append("choosing the 30-day plan did not change the Buy button")
        page.click('.plan[data-plan="w"]')

        # step 2: who you are, then the number
        page.click("#buy-cta")
        page.wait_for_selector("#checkout", state="visible", timeout=8000)
        print("step 2       :", page.text_content("#checkout-plan"), "| buy block hidden:", not page.locator("#buy-block").is_visible())
        page.wait_for_selector("#testlogin", state="visible", timeout=8000)
        page.screenshot(path=str(OUT / "buy-2-who.png"), full_page=True)
        page.fill("#testlogin-email", EMAIL)
        page.click("#testlogin-go")
        page.wait_for_selector("#pass-pay", state="visible", timeout=15000)
        print("signed in    :", page.text_content("#pass-who2"))
        page.fill("#phone", "9876543210")
        page.screenshot(path=str(OUT / "buy-3-pay.png"), full_page=True)
        page.click("#pay")
        page.wait_for_url("**cashfree**", timeout=30000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2500)
        print("checkout     :", page.url[:60])
        if STOP:
            print("stopped at the Cashfree page as asked")
            browser.close()
            return 0

        # Cashfree sandbox: Test Wallet, then its simulator (stated OTP, SUCCESS, Submit).
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
        page.wait_for_url("**/prep/app/**", timeout=60000)

        # step 4: your own account, and no pay form in your face
        page.wait_for_selector("#pass-notice.ok", timeout=120000)
        page.wait_for_selector("#account-card", state="visible", timeout=10000)
        print("after paying :", page.text_content("#pass-notice"))
        print("account      :", page.text_content("#pass-who"), "|", page.text_content("#pass-days"), "|", page.text_content("#pass-until"))
        print("chip after   :", page.text_content("#entitle"))
        page.screenshot(path=str(OUT / "buy-4-account.png"), full_page=True)
        if page.locator("#checkout").is_visible() or page.locator("#buy-block").is_visible():
            failures.append("a pay form is still shown after paying")
        if "Pass" not in (page.text_content("#entitle") or ""):
            failures.append("the chip does not show a pass after paying")

        # "Extend my pass" brings the plans back, on purpose
        page.click("#extend")
        page.wait_for_selector("#buy-block", state="visible", timeout=5000)
        print("extend shows the plans again: ok")

        # the bug he reported: reload, and the chip must already know about the pass
        page.goto(f"{BASE}/prep/app/", wait_until="networkidle")
        page.wait_for_function("document.getElementById('entitle').textContent.trim() !== '…'", timeout=20000)
        chip = page.text_content("#entitle")
        print("chip on load :", chip)
        page.screenshot(path=str(OUT / "buy-5-reload.png"), full_page=True)
        if "Pass" not in (chip or ""):
            failures.append(f"after a reload the chip says {chip!r} instead of the pass")
        page.click("#entitle")
        page.wait_for_selector("#account-card", state="visible", timeout=8000)
        print("reload panel :", page.text_content("#pass-days"))

        # and with the key forgotten, the pass must still be known from the account
        page.evaluate("localStorage.removeItem('ps_gemini_key')")
        page.goto(f"{BASE}/prep/app/", wait_until="networkidle")
        page.wait_for_function("document.getElementById('entitle').textContent.trim() !== '…'", timeout=20000)
        print("chip, no key :", page.text_content("#entitle"))
        if "Pass" not in (page.text_content("#entitle") or ""):
            failures.append("with no key in the browser, a signed-in buyer loses sight of their pass")
        browser.close()
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
