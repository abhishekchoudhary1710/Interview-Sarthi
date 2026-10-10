"""My Sarthi dashboard: sign in to account/ against the TEST worker and check the one-section-at-a-time layout
at a 390 px phone and a 1280 px laptop (owner, 10 Oct 2026). Claude and Codex both run this before pushing.

    python tests/account_dash_browser.py [out_dir]        # screenshots go to out_dir (default: dash-shots/)

No server is started: Playwright answers every request to 127.0.0.1:8765 (the only local origin the test worker
allows) from this checkout, so it works where that port cannot be bound (Windows) and next to a running preview.
Exit code 0 when every check passed."""
import sys, pathlib
from playwright.sync_api import sync_playwright
SITE = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else SITE / "dash-shots"); OUT.mkdir(parents=True, exist_ok=True)
import mimetypes, urllib.parse
def serve(route):
    path = urllib.parse.urlparse(route.request.url).path
    f = SITE / path.lstrip("/")
    if f.is_dir(): f = f / "index.html"
    if not f.is_file(): return route.fulfill(status=404, body="not found")
    ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
    if f.suffix == ".js": ctype = "text/javascript"
    route.fulfill(status=200, body=f.read_bytes(), headers={"content-type": ctype})
EMAIL = "owner-check@example.com"
PANES = ["home", "live", "interviews", "profile", "prep", "purchases", "help", "apply", "account"]
results = []
def ok(name, cond, detail=""):
    results.append((bool(cond), name, detail)); print(("PASS " if cond else "FAIL ") + name + (f"  ({detail})" if detail else ""))
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge") if sys.platform == "win32" else p.chromium.launch()
    for label, vp in (("phone", {"width": 390, "height": 844}), ("laptop", {"width": 1280, "height": 860})):
        ctx = b.new_context(viewport=vp, device_scale_factor=1); ctx.route("http://127.0.0.1:8765/**", serve); pg = ctx.new_page()
        errors = []; pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("http://127.0.0.1:8765/account/")
        pg.fill("#test-email", EMAIL); pg.click("#test-login button")
        pg.wait_for_selector("#signed-in:not([hidden])", timeout=30000); pg.wait_for_timeout(800)
        visible = lambda: [s for s in PANES if pg.is_visible(f"#{s}")]
        ok(f"{label}: opens on Home only", visible() == ["home"], str(visible()))
        tiles = pg.locator("#home-tiles .tile")
        ok(f"{label}: Home has 6 tiles", tiles.count() == 6, str(tiles.count()))
        ok(f"{label}: no sideways scroll", pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), pg.evaluate("[document.documentElement.scrollWidth, innerWidth]"))
        pg.screenshot(path=str(OUT / f"{label}-home.png"), full_page=True)
        for s in PANES[1:]:
            pg.click(f'#menu a[data-pane="{s}"]'); pg.wait_for_timeout(250)
            ok(f"{label}: menu {s} shows only {s}", visible() == [s], str(visible()))
            ok(f"{label}: url #{s}", pg.evaluate("location.hash") == f"#{s}")
            ok(f"{label}: {s} marked current", pg.get_attribute(f'#menu a[data-pane="{s}"]', "aria-current") == "page")
            pg.screenshot(path=str(OUT / f"{label}-{s}.png"), full_page=False)
        pg.go_back(); pg.wait_for_timeout(300)
        ok(f"{label}: Back returns to the previous section", visible() == ["apply"], str(visible()))
        pg.goto("http://127.0.0.1:8765/account/#profile"); pg.wait_for_selector("#signed-in:not([hidden])", timeout=30000); pg.wait_for_timeout(600)
        ok(f"{label}: a link to #profile opens Profile", visible() == ["profile"], str(visible()))
        pg.click('#menu a[data-pane="home"]'); pg.wait_for_timeout(250)
        pg.locator("#home-tiles .tile", has_text="Live interviews").locator("button").first.click(); pg.wait_for_timeout(250)
        ok(f"{label}: Home tile button opens its section", visible() == ["interviews"], str(visible()))
        pg.click('#menu a[data-pane="home"]'); pg.wait_for_timeout(250)
        pg.locator("#home-tiles .tile", has_text="Your PCs").get_by_role("button", name="Connect a PC").click(); pg.wait_for_timeout(300)
        ok(f"{label}: Connect a PC from Home opens the connect card", pg.is_visible("#connect-card") and visible() == ["interviews"])
        if label == "phone":
            pos = pg.evaluate("getComputedStyle(document.getElementById('menu')).position")
            ok("phone: tabs stay at the top while scrolling (sticky)", pos == "sticky", pos)
        ok(f"{label}: no script errors", not errors, "; ".join(errors)[:200])
        ctx.close()
    b.close()
bad = [r for r in results if not r[0]]
print(f"\n{len(results) - len(bad)}/{len(results)} passed")
sys.exit(1 if bad else 0)
