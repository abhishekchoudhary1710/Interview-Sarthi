"""End-to-end run of the Prep Sarthi app in headless Chromium with a fake mic.

Needs: a local server on the repo root (python -m http.server 8765), a Gemini
key in PS_KEY, and a 16 kHz mono WAV of a "candidate" in PS_WAV (silence, then
speech). Chromium plays the WAV as the microphone, the real interviewer talks
back, the test ends the interview after PS_SECONDS and waits for the report.
Screenshots land in .seo-preview/ (gitignored).

    PS_KEY=... PS_WAV=C:/path/candidate.wav python tests/mock_e2e.py
"""
import json
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
WAV = os.environ["PS_WAV"]
SECONDS = int(os.environ.get("PS_SECONDS", "75"))
CV = """Abhishek Choudhary
Solo founder, Interview Sarthi (interviewsarthi.com)
- Built a Windows AI interview assistant in Python and PyQt; overlay hidden from screen share.
- Moved the live engine to Gemini Live; cut answer latency from ~4 s to under 2 s.
- Licence server on Cloudflare Workers + D1; Cashfree payments; 7-day offline grace.
- Runs an autonomous social posting pipeline (GitHub Actions, Veo, Chirp)."""


def main() -> int:
    console, failures = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=[
            "--use-fake-device-for-media-stream",
            "--use-fake-ui-for-media-stream",
            f"--use-file-for-fake-audio-capture={WAV}%noloop",
            "--autoplay-policy=no-user-gesture-required",
        ])
        context = browser.new_context(viewport={"width": 420, "height": 860}, is_mobile=True, has_touch=True)
        page = context.new_page()
        page.on("console", lambda m: console.append(f"{m.type}: {m.text}"))
        page.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        page.on("dialog", lambda d: d.accept())
        page.goto(f"{BASE}/prep/app/", wait_until="networkidle")

        page.fill("#cv", CV)
        page.select_option("#practice-focus", "general_cv")
        page.fill("#name", "Abhishek")
        page.select_option("#minutes", "8")
        page.click("#to-key")
        page.wait_for_selector("#s-key.on")
        page.screenshot(path=str(OUT / "mock-1-key.png"))

        page.fill("#key", KEY)
        page.click("#check-key")
        page.wait_for_selector("#s-live.on", timeout=20000)
        entitle = page.text_content("#entitle")
        print("entitlement pill:", entitle)

        page.click("#start")
        page.wait_for_selector("#livetag.on", timeout=120000)
        t0 = time.time()
        heard_lines = set()
        while time.time() - t0 < SECONDS:
            for _ in range(5):
                time.sleep(1)
                you = (page.text_content('#youline') or '').strip()
                if you and you not in heard_lines:
                    heard_lines.add(you)
                    print(f"  {int(time.time() - t0):3d}s  YOU-LINE shown: {you[:90]!r}")
            n_i = page.locator(".bubble.interviewer").count()
            n_c = page.locator(".bubble.candidate").count()
            wheel = page.evaluate("(() => { const w = document.querySelector('#wheel svg'); return w.dataset.state + ' ' + (w.querySelector('.spin').style.transform || ''); })()")
            print(f"  {int(time.time() - t0):3d}s  interviewer {n_i}  candidate {n_c}  clock {page.text_content('#clock')}  wheel {wheel}  hint {page.text_content('#hint')!r}  you {(page.text_content('#youline') or '')[:50]!r}")
            if int(time.time() - t0) in range(18, 24):
                page.screenshot(path=str(OUT / "mock-2-live.png"))
        interviewer_lines = page.locator(".bubble.interviewer span").all_text_contents()
        candidate_lines = page.locator(".bubble.candidate span").all_text_contents()
        for line in interviewer_lines:
            print("  INTERVIEWER:", line)
        for line in candidate_lines:
            print("  CANDIDATE  :", line)
        if not interviewer_lines:
            failures.append("interviewer never spoke")
        if not candidate_lines:
            failures.append("candidate speech was never transcribed")
        if not heard_lines:
            failures.append("the 'She heard' line never appeared on the call screen")

        page.click("#end")
        page.wait_for_selector("#s-report.on", timeout=10000)
        page.wait_for_selector("#report .score, #report h2", timeout=90000)
        page.screenshot(path=str(OUT / "mock-3-report.png"), full_page=True)
        record = page.evaluate("window.__lastReport && {score: window.__lastReport.report && window.__lastReport.report.overall_score, questions: window.__lastReport.report && window.__lastReport.report.questions.length, model: window.__lastReport.model, metrics: window.__lastReport.metrics}")
        print("report:", json.dumps(record, indent=1)[:900])
        if not record or record.get("score") is None:
            failures.append("no report score")
        log = page.text_content("#log")
        (OUT / "mock-log.txt").write_text(log or "", encoding="utf-8")
        browser.close()

    bad_console = [c for c in console if c.startswith("error") and "favicon" not in c]
    if bad_console:
        print("console errors:", *bad_console, sep="\n  ")
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
