"""Exercise the served documentation and capture desktop/mobile previews."""
from pathlib import Path
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
        assert page.locator(".package-card").count() == 3
        page.screenshot(path=str(output / "desktop.png"), full_page=True)
        page.locator('.package-card[href="packages/io.html"]').click()
        page.wait_for_url("**/packages/io.html")
        assert page.locator("h1").count() == 1
        page.goto(URL + "/search.html?q=VisibilityReader", wait_until="networkidle")
        page.wait_for_selector("#search-results li", timeout=15000)
        assert page.locator("#search-results li").count() > 0
        page.goto(URL + "/guides/check-calibration.html", wait_until="networkidle")
        page.screenshot(path=str(output / "calibration.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(URL, wait_until="networkidle")
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.screenshot(path=str(output / "mobile.png"), full_page=True)
        browser.close()
    assert not errors, errors
    print("OK: desktop navigation, search, mobile layout; no JavaScript errors")


if __name__ == "__main__":
    main()
