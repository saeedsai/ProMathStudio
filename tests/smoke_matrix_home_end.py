"""Matrix Home/End keyboard focus and 390px browser regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        page.locator("#mat-rows").select_option("3")
        page.locator("#mat-cols").select_option("3")
        a = page.locator("#mat-grid")
        a.locator('[data-row="1"][data-col="1"]').fill("7")
        a.locator('[data-row="1"][data-col="1"]').focus()
        for key, row, col in [("Home",1,0),("End",1,2),
                              ("Control+Home",0,0),("Control+End",2,2)]:
            page.keyboard.press(key)
            assert a.locator(f'[data-row="{row}"][data-col="{col}"]').evaluate(
                "(e)=>document.activeElement===e"), key
        assert a.locator('[data-row="1"][data-col="1"]').input_value() == "7"
        assert "Matrix A row 2 column 2" in a.locator(
            '[data-row="1"][data-col="1"]').get_attribute("aria-label")
        b = page.locator("#mat-b-grid")
        b.locator('[data-row="0"][data-col="0"]').focus()
        page.keyboard.press("End")
        assert b.locator('[data-row="0"][data-col="1"]').evaluate(
            "(e)=>document.activeElement===e")
        rhs = page.locator("#mat-rhs-grid")
        rhs.locator('[data-row="1"][data-col="0"]').fill("8")
        rhs.locator('[data-row="1"][data-col="0"]').focus()
        page.keyboard.press("Control+End")
        assert rhs.locator('[data-row="2"][data-col="0"]').evaluate(
            "(e)=>document.activeElement===e")
        assert rhs.locator('[data-row="1"][data-col="0"]').input_value() == "8"
        w = page.locator("#mat-weight-grid")
        w.locator('[data-row="2"][data-col="0"]').focus()
        page.keyboard.press("Control+Home")
        assert w.locator('[data-row="0"][data-col="0"]').evaluate(
            "(e)=>document.activeElement===e")
        page.set_viewport_size({"width": 390, "height": 844})
        a.locator('[data-row="1"][data-col="1"]').focus()
        page.keyboard.press("End")
        assert a.locator('[data-row="1"][data-col="2"]').evaluate(
            "(e)=>document.activeElement===e")
        assert not errors, errors
        browser.close()
    print("PASS Matrix Home/End four grids, 3x3, values and mobile")


if __name__ == "__main__":
    main()
