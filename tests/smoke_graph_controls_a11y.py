"""Graph axes and imported dataset controls: accessible 40px targets at mobile/tablet/desktop widths."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def audit(page, selector):
    return page.evaluate("""selector => {
      const controls = [...document.querySelectorAll(selector)]
        .filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
      return {count: controls.length, small: controls
        .map(e => ({id: e.id, height: e.getBoundingClientRect().height}))
        .filter(x => x.height < 39.5)};
    }""", selector)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        page.locator('[data-workspace="graph"]').click()
        # Task-first UI keeps axis ranges in a collapsed advanced disclosure.
        axes = page.locator("#graph-controls-collapsible")
        summary = page.locator("#graph-controls-collapsible > summary")
        summary.focus()
        page.keyboard.press("Enter")
        assert axes.evaluate("(e) => e.open")
        nested_axes = page.locator("#ui-graph-axes")
        nested_summary = page.locator("#ui-graph-axes > summary")
        nested_summary.focus()
        page.keyboard.press("Enter")
        assert nested_axes.evaluate("(e) => e.open")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            result = audit(page, '#graph-panel .graph-controls input')
            assert result["count"] >= 5, (width, result)
            assert result["small"] == [], (width, result)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), width

        axis = page.locator("#graph-xmin")
        axis.focus()
        page.keyboard.press("ControlOrMeta+A")
        page.keyboard.type("-12")
        assert axis.input_value() == "-12"
        page.locator("#graph-plot").click()
        assert page.locator("#graph-status").inner_text().strip()

        page.locator('[data-workspace="data"]').click()
        advanced = page.locator("#dt-advanced")
        if not advanced.evaluate("(e) => e.open"):
            advanced.locator("summary").focus()
            page.keyboard.press("Enter")
        assert advanced.evaluate("(e) => e.open")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            result = audit(page, '#dt-advanced .graph-data-grid select, #dt-advanced .graph-data-grid button, #dt-advanced .graph-data-grid input[type=file]')
            assert result["count"] >= 3, (width, result)
            assert result["small"] == [], (width, result)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), width

        assert not errors, errors
        browser.close()
    print("PASS Graph axes and dataset import controls: 40px targets, keyboard, responsive layout")


if __name__ == "__main__":
    main()
