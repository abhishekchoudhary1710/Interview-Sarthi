"""A muted microphone must never start the interview or spend free minutes.

Headless Chromium plays a WAV of pure silence as the mic (PS_WAV). After Start,
the page has to stay in "Mic check", show the help panel with the microphone
list within a few seconds, open no Gemini session, and go back to the start
when End is pressed.

    PS_KEY=... PS_WAV=C:/path/silence.wav python tests/mock_e2e_muted.py
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
            f"--use-file-for-fake-audio-capture={WAV}",
        ])
        page = browser.new_context(viewport={"width": 420, "height": 860}, is_mobile=True).new_page()
        page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        sockets = []
        page.on("websocket", lambda ws: sockets.append(ws.url))
        page.goto(f"{BASE}/mock/app/", wait_until="networkidle")
        page.fill("#cv", CV)
        page.click("#to-key")
        page.fill("#key", KEY)
        page.click("#check-key")
        page.wait_for_selector("#s-live.on", timeout=20000)
        page.click("#start")
        page.wait_for_selector("#micfix", state="visible", timeout=12000)
        page.screenshot(path=str(OUT / "mock-muted.png"))
        text = page.text_content("#micfix-text")
        tag = page.text_content("#livetag")
        mics = page.locator("#micselect option").count()
        print("help text :", text)
        print("status tag:", tag, "| mics listed:", mics, "| gemini sockets opened:", len(sockets))
        if "silence" not in (text or "").lower() and "muted" not in (text or "").lower():
            failures.append("help text does not explain the silence")
        if tag != "Mic check":
            failures.append(f"status should still be Mic check, is {tag!r}")
        if sockets:
            failures.append("a Gemini session was opened although no voice was heard")
        if mics < 1:
            failures.append("no microphones listed")
        page.click("#end")
        page.wait_for_selector("#pre-live", state="visible", timeout=5000)
        print("after End : back at the start screen,", page.text_content("#livetag"))
        browser.close()
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
