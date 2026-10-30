"""Contextual matrix factor transfer, invalidation, keyboard and mobile browser regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        selectors = page.locator("[data-mat-factor]")
        assert selectors.count() == 4
        assert all(not selectors.nth(i).is_visible() for i in range(4))
        assert page.locator("#mat-send").is_disabled()
        assert page.locator(".matrix-actions button").count() == 16

        # Each successful factorization displays exactly one relevant selector.
        for button, operation in (("mat-lu", "lu"), ("mat-qr", "qr"),
                                  ("mat-eigen", "eigen"), ("mat-svd", "svd")):
            page.locator("#" + button).click()
            assert page.locator("#mat-send").is_enabled(), page.locator("#mat-result").inner_text()
            visible = [x.get_attribute("data-mat-factor") for x in selectors.all() if x.is_visible()]
            assert visible == [operation], (button, visible)
            assert page.evaluate("document.activeElement.id") == button
        # Preserve editor factor selection and transfer (swap matrix).
        for i, value in enumerate(["0", "1", "1", "0"]):
            page.locator("#mat-grid input").nth(i).fill(value)
        page.locator("#mat-lu").click()
        assert page.locator('[data-mat-factor="lu"]').is_visible()
        page.locator("#mat-lu-factor").select_option("P")
        page.locator("#mat-send").click()
        assert "matrix([0,1],[1,0])" in page.locator("#equation-input").input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")

        # Input edits invalidate stale factor selectors and editor transfer.
        page.locator("#mat-grid input").first.fill("1")
        assert page.locator("#mat-send").is_disabled()
        assert all(not selectors.nth(i).is_visible() for i in range(4))
        page.locator("#mat-grid input").first.fill("")
        page.locator("#mat-lu").click()
        assert "Enter a number" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        assert all(not selectors.nth(i).is_visible() for i in range(4))
        page.locator("#mat-grid input").first.fill("1")
        page.locator("#mat-qr").click()
        assert page.locator('[data-mat-factor="qr"]').is_visible()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator(".matrix-result-actions").is_visible()
        assert page.locator("#mat-qr-factor").is_visible()
        assert page.locator("#mat-send").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS contextual Matrix transfer, all factors, invalidation, keyboard and 390px mobile")


if __name__ == "__main__":
    main()
