"""Browser regression: shared condition number in Ax=b and inverse, mobile recovery."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        inputs = page.locator("#mat-grid input")
        rhs = page.locator("#mat-rhs-grid input")
        for i, value in enumerate(["2", "1", "0", "3"]):
            inputs.nth(i).fill(value)
        for i, value in enumerate(["3", "6"]):
            rhs.nth(i).fill(value)
        page.locator("#mat-solve").click()
        result = page.locator("#mat-result").inner_text()
        assert "Infinity-norm condition number:" in result, result
        assert "Normwise backward error (∞):" in result, result
        assert page.locator("#mat-send").is_enabled()

        page.locator("#mat-inverse").click()
        result = page.locator("#mat-result").inner_text()
        assert "Infinity-norm condition number:" in result, result
        assert page.locator("#mat-send").is_enabled()

        for i, value in enumerate(["1", "2", "2", "4"]):
            inputs.nth(i).fill(value)
        page.locator("#mat-solve").click()
        assert "Singular" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()

        for i, value in enumerate(["1e-9", "0", "0", "1e9"]):
            inputs.nth(i).fill(value)
        for i, value in enumerate(["2e-9", "3e9"]):
            rhs.nth(i).fill(value)
        page.locator("#mat-solve").click()
        result = page.locator("#mat-result").inner_text()
        assert "Infinity-norm condition number:" in result, result
        assert "unavailable" not in result, result
        assert page.locator("#mat-send").is_enabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#mat-solve").is_visible()
        assert page.locator("#mat-inverse").is_visible()
        assert page.locator("#mat-send").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS Ax=b and inverse condition number, singular recovery and mobile")


if __name__ == "__main__":
    main()
