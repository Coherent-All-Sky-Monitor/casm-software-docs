"""Exercise the served documentation and capture desktop/mobile previews."""
from pathlib import Path
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8070"


def main():
    output = ROOT / "_build" / "screenshots"
    output.mkdir(parents=True, exist_ok=True)
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(URL, wait_until="networkidle")
        banner = page.locator("article .admonition").filter(has_text="isolated candidate software")
        assert banner.count() == 1
        assert banner.locator('a[href="developer/audit-release.html"]').count() == 1
        assert page.locator(".package-card").count() == 0
        assert page.locator("article figure img").count() == 1
        assert page.locator("article figure img").get_attribute("src").endswith(
            "solar-waterfall.webp"
        )
        page.screenshot(path=str(output / "desktop.png"), full_page=True)
        page.locator('article a[href="guides/read-visibilities.html"]').first.click()
        page.wait_for_url("**/guides/read-visibilities.html")
        assert page.locator("h1").count() == 1
        assert page.locator('figure img[src$="visibility-two-antennas.png"]').count() == 1
        assert page.locator('figure img[src$="cross-amplitude-phase.png"]').count() == 1
        assert page.locator(".highlight .kn").first.evaluate(
            "node => getComputedStyle(node).color"
        ) == "rgb(40, 87, 126)"
        page.goto(URL + "/search.html?q=VisibilityReader", wait_until="networkidle")
        page.wait_for_selector("#search-results li", timeout=15000)
        assert page.locator("#search-results li").count() > 0
        for tutorial in (
            "read-visibilities", "read-voltages", "solar-phase", "solar-waterfall",
            "check-calibration", "generate-weights", "injection-recovery",
        ):
            page.goto(URL + f"/guides/{tutorial}.html", wait_until="networkidle")
            assert page.locator("figure img").count() > 0, tutorial
            assert page.locator("figure img").evaluate_all(
                "images => images.every(img => img.complete && img.naturalWidth > 0)"
            ), tutorial
            page.screenshot(path=str(output / f"{tutorial}.png"), full_page=True)
        page.goto(URL + "/guides/check-calibration.html", wait_until="networkidle")
        page.screenshot(path=str(output / "calibration.png"), full_page=True)
        page.goto(URL + "/guides/rank1-diagnostics.html", wait_until="networkidle")
        assert page.locator("figure img").count() == 1
        assert "Look at the singular values" not in page.locator("article").inner_text()
        assert page.locator("figure img").evaluate_all(
            "images => images.every(img => img.complete && img.naturalWidth > 0)"
        )
        page.emulate_media(color_scheme="dark")
        assert page.locator(".sidebar-drawer").evaluate(
            'node => getComputedStyle(node).backgroundColor'
        ) == "rgb(12, 13, 15)"
        assert page.locator(".highlight .kn").first.evaluate(
            "node => getComputedStyle(node).color"
        ) == "rgb(175, 196, 226)"
        page.screenshot(path=str(output / "dark-tutorial.png"), full_page=True)
        page.goto(URL + "/packages/io-api.html", wait_until="networkidle")
        page.locator(".viewcode-link").first.click()
        page.wait_for_url("**/_modules/**")
        assert page.locator(".viewcode-block").count() > 0
        assert (page.request.get(URL + "/llms.txt")).ok
        assert (page.request.get(URL + "/guides/rank1-diagnostics.html.md")).ok
        page.emulate_media(color_scheme="light")
        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(URL, wait_until="networkidle")
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert page.locator("article .admonition").filter(has_text="isolated candidate software").is_visible()
        page.screenshot(path=str(output / "mobile.png"), full_page=True)
        browser.close()
    assert not errors, errors
    print("OK: navigation, search, source links, figures, dark/mobile layouts and Markdown endpoints")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-build", action="store_true",
                        help="Test this checkout on a temporary loopback port; leave 8070 untouched")
    args = parser.parse_args()
    if args.local_build:
        handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / "_build/html"))
        with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            URL = f"http://127.0.0.1:{server.server_port}"
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                main()
            finally:
                server.shutdown()
                thread.join()
    else:
        main()
