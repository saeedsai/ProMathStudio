"""Table zoom keyboard, accessible percentage and clamp browser regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="data"]').click()
        page.evaluate("""() => document.querySelectorAll('#data-menu-navigation > details')
            .forEach(el => { el.open = true; })""")
        slider = page.locator("#table-zoom")
        output = page.locator("#table-zoom-value")
        assert slider.input_value() == "100"
        assert slider.get_attribute("aria-valuetext") == "100%"
        assert output.inner_text() == "100%"
        slider.focus()
        page.keyboard.press("ArrowRight")
        assert slider.input_value() == "110"
        assert slider.get_attribute("aria-valuetext") == "110%"
        assert output.inner_text() == "110%"
        assert page.locator("#table-zoom-content").evaluate(
            "(e) => e.style.zoom") == "1.1"
        page.locator("#table-zoom-out").click()
        assert slider.get_attribute("aria-valuetext") == "100%"
        page.evaluate("() => window.MathStudio.tableZoom.set(900)")
        assert slider.input_value() == "200"
        assert slider.get_attribute("aria-valuetext") == "200%"
        page.evaluate("() => window.MathStudio.tableZoom.set(-50)")
        assert slider.input_value() == "50"
        assert slider.get_attribute("aria-valuetext") == "50%"
        page.locator("#table-zoom-reset").click()
        assert slider.input_value() == "100"
        assert slider.get_attribute("aria-valuetext") == "100%"
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            assert not page.evaluate(
                "() => document.documentElement.scrollWidth > innerWidth + 1"), width
        assert not errors, errors
        browser.close()
    print("PASS extracted table zoom, keyboard, 50-200% clamp, a11y and mobile")


if __name__ == "__main__":
    main()
