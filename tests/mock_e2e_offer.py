"""The pass offer must appear when someone would want it, and must never cost
them their interview.

Local preview against the sandbox worker. Needs a key whose free time is just
over five minutes (the offer shows at five), a spoken WAV for the fake mic:

    PS_KEY=... PS_WAV=C:/path/candidate2.wav python tests/mock_e2e_offer.py

Checks: the offer appears mid-interview; the pass screen warns that an
interview is running and disables buying; Back returns to the SAME running
interview (not the start screen); after End, the report shows the offer too.
"""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".seo-preview"
OUT.mkdir(exist_ok=True)
BASE = os.environ.get("PS_BASE", "http://127.0.0.1:8765")
KEY = os.environ["PS_KEY"]
WAV = os.environ["PS_WAV"]
CV = "Riya Sharma\nBackend engineer, three years.\n- Built a payments service in Java and Spring Boot; cut failed transactions by 30%.\n- Moved nightly jobs to Kafka streams."


def main() -> int:
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=[
            "--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream",
            f"--use-file-for-fake-audio-capture={WAV}%noloop", "--autoplay-policy=no-user-gesture-required",
        ])
        page = browser.new_context(viewport={"width": 420, "height": 900}, is_mobile=True).new_page()
        page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        page.on("dialog", lambda d: d.accept())
        page.goto(f"{BASE}/mock/app/", wait_until="networkidle")
        page.evaluate("localStorage.removeItem('ps_session')")          # a free user, not a buyer
        page.goto(f"{BASE}/mock/app/", wait_until="networkidle")
        page.fill("#cv", CV)
        page.click("#to-key")
        page.fill("#key", KEY)
        page.click("#check-key")
        page.wait_for_selector("#s-live.on", timeout=20000)
        print("chip         :", page.text_content("#entitle"))
        page.click("#start")
        page.wait_for_selector("#livetag.on", timeout=30000)

        page.wait_for_selector("#live-offer", state="visible", timeout=90000)
        print("offer        :", page.text_content("#live-offer-text"))
        page.screenshot(path=str(OUT / "offer-1-live.png"))
        clock_before = page.text_content("#clock")

        page.click("#live-offer-go")
        page.wait_for_selector("#s-pass.on")
        page.wait_for_selector("#pass-running", state="visible", timeout=5000)
        print("pass screen  : warns about the running interview:", page.locator("#pass-running").is_visible(), "| Buy disabled:", page.is_disabled("#buy-cta"))
        page.screenshot(path=str(OUT / "offer-2-pass-while-running.png"), full_page=True)
        if not page.is_disabled("#buy-cta"):
            failures.append("Buy is clickable while an interview is running")

        page.wait_for_timeout(3000)
        page.click("#pass-running-back")
        page.wait_for_selector("#s-live.on")
        still_live = page.get_attribute("#livetag", "class")
        print("back         : tag", repr(still_live), "| start card hidden:", not page.locator("#pre-live").is_visible(), "| clock", clock_before, "->", page.text_content("#clock"))
        if "on" not in (still_live or "") or page.locator("#pre-live").is_visible():
            failures.append("coming back from passes reset the running interview")

        page.wait_for_timeout(12000)
        page.click("#end")
        page.wait_for_selector("#s-report.on", timeout=10000)
        page.wait_for_selector("#report .score, #report h2", timeout=90000)
        page.wait_for_selector("#report-offer", state="visible", timeout=10000)
        print("report offer :", page.text_content("#report-offer-text"))
        page.screenshot(path=str(OUT / "offer-3-report.png"), full_page=True)
        browser.close()
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
