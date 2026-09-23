"""Google's sign-in button must draw once, without a spurious failure message.

Runs against the LIVE site by default, because only production has a Google
client id. It never signs in; it only checks that arriving at checkout draws
Google's button and leaves no error on screen, and that a genuinely blocked
script is reported in words a person can act on.

    python tests/mock_e2e_gsi.py
"""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".seo-preview"
OUT.mkdir(exist_ok=True)
BASE = os.environ.get("PS_BASE", "https://interviewsarthi.com")


def main() -> int:
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---- normal browser: the button draws, and nothing complains
        page = browser.new_context(viewport={"width": 420, "height": 900}, is_mobile=True).new_page()
        page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        page.goto(f"{BASE}/prep/app/?buy=w", wait_until="networkidle")
        page.wait_for_selector("#checkout", state="visible", timeout=20000)
        page.wait_for_selector("#gbutton iframe", timeout=20000)
        page.wait_for_timeout(3000)                      # past the blocked-button check
        notice = (page.text_content("#pass-notice") or "").strip()
        print("plan         :", page.text_content("#checkout-plan"))
        print("google button:", page.locator("#gbutton iframe").count(), "iframe(s)")
        print("notice       :", repr(notice))
        page.screenshot(path=str(OUT / "gsi-ok.png"), full_page=True)
        if notice:
            failures.append(f"a message is shown even though the button drew: {notice!r}")
        if page.locator("#gbutton iframe").count() != 1:
            failures.append("Google's button did not draw exactly once")

        # going back and forth must not redraw or complain
        page.click("#checkout-back")
        page.wait_for_selector("#buy-block", state="visible")
        page.click("#buy-cta")
        page.wait_for_timeout(2500)
        print("after back/forth:", page.locator("#gbutton iframe").count(), "iframe(s), notice", repr((page.text_content("#pass-notice") or "").strip()))
        if page.locator("#gbutton iframe").count() != 1 or (page.text_content("#pass-notice") or "").strip():
            failures.append("returning to checkout redrew the button or raised a message")

        # ---- a blocker: the message must name the cause and what to do
        ctx = browser.new_context(viewport={"width": 420, "height": 900}, is_mobile=True)
        ctx.route("**/gsi/client*", lambda route: route.abort())
        blocked = ctx.new_page()
        blocked.goto(f"{BASE}/prep/app/?buy=w", wait_until="networkidle")
        blocked.wait_for_selector("#checkout", state="visible", timeout=20000)
        blocked.wait_for_selector("#pass-notice.bad", timeout=20000)
        msg = blocked.text_content("#pass-notice")
        print("blocked      :", msg)
        blocked.screenshot(path=str(OUT / "gsi-blocked.png"), full_page=True)
        if "blocker" not in msg.lower() and "shields" not in msg.lower():
            failures.append("the blocked message does not explain the likely cause")
        browser.close()
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
