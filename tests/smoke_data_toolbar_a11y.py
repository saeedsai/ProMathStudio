"""Data Tables toolbar touch targets and keyboard behavior at desktop/mobile widths."""
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

        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            audit = page.evaluate("""() => {
              const toolbars = [...document.querySelectorAll('#data-panel .data-inner > .data-toolbar')];
              const controls = toolbars.flatMap(x => [...x.querySelectorAll('button,input,select')])
                .filter(el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden');
              return {count: controls.length, small: controls
                .map(el => ({id:el.id, height:el.getBoundingClientRect().height}))
                .filter(x => x.height < 39.5),
                overflow: document.documentElement.scrollWidth > innerWidth + 1};
            }""")
            assert audit["count"] >= 10, audit
            assert not audit["small"], f"width={width}: {audit['small']}"
            assert not audit["overflow"], f"horizontal overflow at {width}px"

        # The existing filter remains keyboard-operable after the style change.
        search = page.locator("#dt-filter")
        search.focus()
        page.keyboard.type("sample")
        assert search.input_value() == "sample"
        page.keyboard.press("ControlOrMeta+A")
        page.keyboard.press("Backspace")
        assert search.input_value() == ""
        assert not errors, errors
        browser.close()
    print("PASS Data Tables toolbar touch targets, keyboard filter and 390/768/1280 layout")


if __name__ == "__main__":
    main()
