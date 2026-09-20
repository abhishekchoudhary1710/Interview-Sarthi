"""Buy a Prep Sarthi pass end to end against the SANDBOX worker and Cashfree sandbox.

Local preview only (the page talks to the sandbox worker when served from
127.0.0.1, and that worker accepts a made-up sign-in). Steps: CV, key, open
passes, test sign-in, phone, pay with Cashfree's test UPI id, return, and the
pass must show as live. Screenshots land in .seo-preview/.

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
        page = browser.new_context(viewport={"width": 420, "height": 900}, is_mobile=True).new_page()
        page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        page.goto(f"{BASE}/mock/app/?ref=TESTREF", wait_until="networkidle")
        page.fill("#cv", CV)
        page.click("#to-key")
        page.fill("#key", KEY)
        page.click("#check-key")
        page.wait_for_selector("#s-live.on", timeout=20000)
        print("chip before:", page.text_content("#entitle"))

        page.click("#entitle")
        page.wait_for_selector("#s-pass.on")
        page.wait_for_selector("#testlogin", state="visible", timeout=8000)
        page.screenshot(path=str(OUT / "buy-1-passes.png"), full_page=True)
        page.fill("#testlogin-email", EMAIL)
        page.click("#testlogin-go")
        page.wait_for_selector("#pass-pay", state="visible", timeout=15000)
        print("signed in :", page.text_content("#pass-who"))
        page.click('.plan[data-plan="w"]')
        page.fill("#phone", "9876543210")
        page.screenshot(path=str(OUT / "buy-2-pay.png"), full_page=True)
        page.click("#pay")
        page.wait_for_url("**cashfree**", timeout=30000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "buy-3-cashfree.png"), full_page=True)
        print("checkout  :", page.url[:80])
        if STOP:
            print("stopped at the Cashfree page as asked")
            browser.close()
            return 0
        # Cashfree sandbox: the Test Wallet leads to a simulator with a Success button.
        page.get_by_text("Test Wallet").first.click()
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "buy-4-wallet.png"), full_page=True)
        for label in ("Pay", "Proceed", "Continue", "Pay Now"):
            try:
                page.get_by_role("button", name=label).first.click(timeout=2500)
                break
            except Exception:
                pass
        page.wait_for_timeout(4000)
        page.screenshot(path=str(OUT / "buy-5-sim.png"), full_page=True)
        print("simulator :", page.url[:90])
        # The simulator: its stated OTP, the SUCCESS outcome, Submit.
        page.locator("input").first.fill("111000")
        page.get_by_text("SUCCESS", exact=True).first.click(timeout=5000)
        page.get_by_role("button", name="Submit").click(timeout=5000)
        page.wait_for_url("**/mock/app/**", timeout=60000)
        print("returned  :", page.url[:90])
        page.wait_for_selector("#pass-notice.ok", timeout=120000)
        print("notice    :", page.text_content("#pass-notice"))
        print("chip after:", page.text_content("#entitle"))
        page.screenshot(path=str(OUT / "buy-6-done.png"), full_page=True)
        if "Pass" not in (page.text_content("#entitle") or ""):
            failures.append("the chip does not show a pass after paying")
        browser.close()
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
