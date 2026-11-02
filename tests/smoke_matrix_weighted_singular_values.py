"""Weighted design singular values: Chromium keyboard/mobile recovery."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e) => e.open=true")
        page.locator("#mat-rows").select_option("3")
        page.locator("#mat-cols").select_option("2")
        for i, v in enumerate(("1", "1", "1", "1.000001", "1", "1.000002")):
            page.locator("#mat-grid input").nth(i).fill(v)
        for i, v in enumerate(("1", "0.999999", "0.999998")):
            page.locator("#mat-rhs-grid input").nth(i).fill(v)
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#mat-weighted-least-squares").focus()
            page.keyboard.press("Enter")
            result = page.locator("#mat-result")
            assert not result.evaluate("(e) => e.classList.contains('error')"), result.inner_text()
            assert "Weighted design singular values (max, min" in result.inner_text()
            assert "do not certify coefficient accuracy" in result.inner_text()
            vals = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,1],[1,1.000001],[1,1.000002]],[1,.999999,.999998],[1,1,1]).weightedDesignSingularValues")
            assert len(vals) == 2 and all(math.isfinite(x) and x > 0 for x in vals), vals
            assert abs(vals[1] / 1e-6 - 1) < 1e-6, vals
            assert not page.evaluate("() => document.documentElement.scrollWidth > innerWidth + 1"), width
        page.locator("#mat-weight-grid input").last.fill("0")
        page.locator("#mat-weighted-least-squares").click()
        assert "Weights must be finite" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-weight-grid input").last.fill("1")
        page.locator("#mat-weighted-least-squares").click()
        assert page.locator("#mat-send").is_enabled()
        assert not errors, errors
        browser.close()
    print("PASS weighted singular values browser recovery")


if __name__ == "__main__":
    main()
