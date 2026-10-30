"""Matrix sensitivity advisory browser, recovery and mobile regression."""
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
        cells = page.locator("#mat-grid input")
        rhs = page.locator("#mat-rhs-grid input")
        page.locator("#mat-solve").click()
        output = page.locator("#mat-result").inner_text()
        assert "Condition guidance: Below the 1e8" in output, output
        assert "Normwise backward error" in output, output
        assert page.locator("#mat-send").is_enabled()
        for i, v in enumerate(["1e-9", "0", "0", "1e9"]):
            cells.nth(i).fill(v)
        for i, v in enumerate(["2e-9", "3e9"]):
            rhs.nth(i).fill(v)
        page.locator("#mat-solve").click()
        output = page.locator("#mat-result").inner_text()
        assert "Condition guidance: High sensitivity" in output, output
        assert "small residual does not certify accuracy" in output, output
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-inverse").click()
        assert "Condition guidance: High sensitivity" in page.locator("#mat-result").inner_text()
        for i, v in enumerate(["1", "2", "2", "4"]):
            cells.nth(i).fill(v)
        for i, v in enumerate(["3", "6"]):
            rhs.nth(i).fill(v)
        page.locator("#mat-solve").click()
        assert "Singular" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        for i, v in enumerate(["1", "0", "0", "1"]):
            cells.nth(i).fill(v)
        page.locator("#mat-solve").click()
        assert "Condition guidance: Below the 1e8" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_enabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#mat-result").is_visible()
        assert page.locator("#mat-solve").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS matrix condition advisory, inverse, singular recovery and mobile")


if __name__ == "__main__":
    main()
