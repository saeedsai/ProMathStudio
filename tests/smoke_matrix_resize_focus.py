"""Matrix grid rebuild retains focus on surviving/clamped cells, desktop/mobile."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def set_dimension(page, selector, value):
    # Change a dimension without moving focus away from the currently edited cell.
    page.locator(selector).evaluate(
        """(el, value) => { el.value = value; el.dispatchEvent(new Event('change', {bubbles:true})); }""",
        str(value),
    )


def focused(page, grid, row, col):
    return page.locator(f'{grid} [data-row="{row}"][data-col="{col}"]').evaluate(
        "(el) => document.activeElement === el"
    )


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
        page.locator("#matrix-tools").evaluate("(e) => e.open = true")
        a = page.locator("#mat-grid")
        a.locator('[data-row="1"][data-col="1"]').fill("13")
        a.locator('[data-row="1"][data-col="1"]').focus()
        set_dimension(page, "#mat-rows", 3)
        assert focused(page, "#mat-grid", 1, 1)
        a.locator('[data-row="2"][data-col="1"]').fill("17")
        a.locator('[data-row="2"][data-col="1"]').focus()
        set_dimension(page, "#mat-rows", 2)
        assert focused(page, "#mat-grid", 1, 1)
        assert a.locator('[data-row="1"][data-col="1"]').input_value() == "13"

        b = page.locator("#mat-b-grid")
        b.locator('[data-row="1"][data-col="1"]').fill("19")
        b.locator('[data-row="1"][data-col="1"]').focus()
        set_dimension(page, "#mat-b-cols", 3)
        assert focused(page, "#mat-b-grid", 1, 1)
        b.locator('[data-row="1"][data-col="2"]').focus()
        set_dimension(page, "#mat-b-cols", 2)
        assert focused(page, "#mat-b-grid", 1, 1)
        assert b.locator('[data-row="1"][data-col="1"]').input_value() == "19"

        rhs = page.locator("#mat-rhs-grid")
        rhs.locator('[data-row="1"][data-col="0"]').fill("23")
        rhs.locator('[data-row="1"][data-col="0"]').focus()
        set_dimension(page, "#mat-rows", 3)
        assert focused(page, "#mat-rhs-grid", 1, 0)
        rhs.locator('[data-row="2"][data-col="0"]').focus()
        set_dimension(page, "#mat-rows", 2)
        assert focused(page, "#mat-rhs-grid", 1, 0)
        assert rhs.locator('[data-row="1"][data-col="0"]').input_value() == "23"

        page.set_viewport_size({"width": 390, "height": 844})
        weights = page.locator("#mat-weight-grid")
        weights.locator('[data-row="1"][data-col="0"]').fill("2.5")
        weights.locator('[data-row="1"][data-col="0"]').focus()
        set_dimension(page, "#mat-rows", 3)
        assert focused(page, "#mat-weight-grid", 1, 0)
        weights.locator('[data-row="2"][data-col="0"]').focus()
        set_dimension(page, "#mat-rows", 2)
        assert focused(page, "#mat-weight-grid", 1, 0)
        assert weights.locator('[data-row="1"][data-col="0"]').input_value() == "2.5"
        assert page.locator("#mat-send").is_disabled()
        assert not errors, errors
        browser.close()
    print("PASS Matrix resize focus four grids, clamping, drafts and mobile")


if __name__ == "__main__":
    main()
