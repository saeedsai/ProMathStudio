"""Matrix disclosure, draft preservation, keyboard and mobile regression."""
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
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        assert page.locator(".matrix-actions button").count() == 16
        for name in ("rhs", "weight", "b"):
            section = page.locator("#mat-" + name + "-section")
            assert section.get_attribute("open") is not None
            section.locator("summary").click()
            assert section.get_attribute("open") is None
        page.locator("#mat-b-section summary").click()
        page.locator("#mat-b-grid input").first.fill("7")
        page.locator("#mat-b-section summary").click()
        page.locator("#mat-add").click()
        assert page.locator("#mat-b-section").get_attribute("open") is not None
        assert page.locator("#mat-b-grid input").first.input_value() == "7"
        assert "8" in page.locator("#mat-result").inner_text()
        page.locator("#mat-rhs-section summary").focus()
        page.keyboard.press("Enter")
        assert page.locator("#mat-rhs-section").get_attribute("open") is not None
        page.locator("#mat-rhs-grid input").first.fill("3")
        page.locator("#mat-rhs-section summary").click()
        page.locator("#mat-solve").click()
        assert page.locator("#mat-rhs-section").get_attribute("open") is not None
        assert page.locator("#mat-rhs-grid input").first.input_value() == "3"
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-weighted-least-squares").click()
        assert page.locator("#mat-weight-section").get_attribute("open") is not None
        assert page.locator("#mat-send").is_disabled()
        assert "3×2" in page.locator("#mat-result").inner_text()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#mat-grid").is_visible()
        assert page.locator("#mat-weight-section summary").is_visible()
        assert page.locator("#mat-b-grid").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS matrix input disclosures, keyboard, draft retention and 390px mobile")
if __name__ == "__main__":
    main()
