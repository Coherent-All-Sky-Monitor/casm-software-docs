"""Check tutorial figures in the local build, without contacting production."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FIGURES = {
    "read-voltages": "voltage-single-stream.png",
    "rank1-diagnostics": "rank1-vs-freq.png",
    "check-calibration": "cyga-beam-power.png",
    "image-visibilities": "allsky-saved.png",
    "injection-recovery": "inj_20260913_0023.png",
}


def main():
    output = ROOT / "_build/tutorial-screenshots"
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for width in (1440, 390):
            page.set_viewport_size({"width": width, "height": 900})
            for name, image in FIGURES.items():
                page.goto((ROOT / f"_build/html/guides/{name}.html").as_uri())
                page.wait_for_load_state("load")
                assert page.locator(f'figure img[src$="{image}"]').count() == 1
                assert page.locator("figure img").evaluate_all(
                    "items => items.every(i => i.complete && i.naturalWidth > 0)")
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(output / f"{name}-{width}.png"), full_page=True)
        browser.close()
    print("PASS five local tutorial pages: images and desktop/mobile widths")


if __name__ == "__main__":
    main()
