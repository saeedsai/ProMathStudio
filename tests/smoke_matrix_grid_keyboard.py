"""Matrix grid arrow-key focus, value preservation and mobile browser regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")

        a = page.locator("#mat-grid")
        a.locator('[data-row="0"][data-col="0"]').fill("7")
        a.locator('[data-row="0"][data-col="0"]').focus()
        page.keyboard.press("ArrowRight")
        assert a.locator('[data-row="0"][data-col="1"]').evaluate("(e)=>document.activeElement===e")
        page.keyboard.press("ArrowDown")
        assert a.locator('[data-row="1"][data-col="1"]').evaluate("(e)=>document.activeElement===e")
        page.keyboard.press("ArrowLeft")
        assert a.locator('[data-row="1"][data-col="0"]').evaluate("(e)=>document.activeElement===e")
        page.keyboard.press("ArrowUp")
        assert a.locator('[data-row="0"][data-col="0"]').evaluate("(e)=>document.activeElement===e")
        page.keyboard.press("ArrowUp")
        page.keyboard.press("ArrowLeft")
        assert a.locator('[data-row="0"][data-col="0"]').evaluate("(e)=>document.activeElement===e")
        assert a.locator('[data-row="0"][data-col="0"]').input_value() == "7"

        page.locator("#mat-rows").select_option("3")
        page.locator("#mat-cols").select_option("3")
        a.locator('[data-row="1"][data-col="2"]').focus()
        page.keyboard.press("ArrowDown")
        assert a.locator('[data-row="2"][data-col="2"]').evaluate("(e)=>document.activeElement===e")
        page.keyboard.press("ArrowRight")
        assert a.locator('[data-row="2"][data-col="2"]').evaluate("(e)=>document.activeElement===e")

        b = page.locator("#mat-b-grid")
        b.locator('[data-row="0"][data-col="0"]').focus()
        page.keyboard.press("ArrowRight")
        assert b.locator('[data-row="0"][data-col="1"]').evaluate("(e)=>document.activeElement===e")

        rhs = page.locator("#mat-rhs-grid")
        rhs.locator('[data-row="0"][data-col="0"]').focus()
        page.keyboard.press("ArrowDown")
        assert rhs.locator('[data-row="1"][data-col="0"]').evaluate("(e)=>document.activeElement===e")
        page.keyboard.press("ArrowRight")
        assert rhs.locator('[data-row="1"][data-col="0"]').evaluate("(e)=>document.activeElement===e")

        weights = page.locator("#mat-weight-grid")
        weights.locator('[data-row="0"][data-col="0"]').focus()
        page.keyboard.press("ArrowDown")
        assert weights.locator('[data-row="1"][data-col="0"]').evaluate("(e)=>document.activeElement===e")
        assert weights.locator('[data-row="0"][data-col="0"]').input_value() == "1"
        page.keyboard.press("Tab")
        assert not weights.locator('[data-row="1"][data-col="0"]').evaluate("(e)=>document.activeElement===e")

        page.set_viewport_size({"width": 390, "height": 844})
        assert a.locator('[data-row="2"][data-col="2"]').is_visible()
        a.locator('[data-row="2"][data-col="1"]').focus()
        page.keyboard.press("ArrowRight")
        assert a.locator('[data-row="2"][data-col="2"]').evaluate("(e)=>document.activeElement===e")
        assert not errors, errors
        browser.close()
    print("PASS Matrix A/B/RHS/weight arrows, 2x2/3x3, boundaries, Tab and 390px mobile")


if __name__ == "__main__":
    main()
