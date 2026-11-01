"""Matrix touch targets, keyboard focus, and responsive controls."""
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
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"),
                         wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        page.locator("#matrix-tools").evaluate("(el) => el.open=true")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            audit = page.evaluate("""() => {
                const root = document.getElementById('matrix-tools');
                const controls = [...root.querySelectorAll(
                    '.matrix-controls select,.matrix-actions button,.matrix-result-actions button,.matrix-grid input')]
                    .filter(e=>e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
                return {total:controls.length,
                    small:controls.map(e=>[e.id||e.getAttribute('aria-label')||e.tagName,
                        e.getBoundingClientRect().height]).filter(x=>x[1]<39.5),
                    overflow:document.documentElement.scrollWidth>innerWidth+1};
            }""")
            assert audit["total"] >= 8, audit
            assert not audit["small"], (width, audit)
            assert not audit["overflow"], (width, audit)
        first = page.locator('#mat-grid [data-row="0"][data-col="0"]')
        first.focus()
        page.keyboard.press("ArrowRight")
        assert page.locator('#mat-grid [data-row="0"][data-col="1"]').evaluate(
            "(el) => el === document.activeElement")
        assert not errors, errors
        browser.close()
    print("PASS Matrix 40px controls and keyboard at 390/768/1280")


if __name__ == "__main__":
    main()
