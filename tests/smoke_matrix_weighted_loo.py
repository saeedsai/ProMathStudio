"""Weighted leave-one-out residuals: keyboard, responsive UI and invalid-input recovery."""
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
        cells = page.locator("#mat-grid input")
        rhs = page.locator("#mat-rhs-grid input")
        weights = page.locator("#mat-weight-grid input")
        for i, v in enumerate(("1", "0", "1", "1", "1", "2")):
            cells.nth(i).fill(v)
        for i, v in enumerate(("1", "2", "9")):
            rhs.nth(i).fill(v)
        for i, v in enumerate(("1", "1", "0.01")):
            weights.nth(i).fill(v)
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#mat-weighted-least-squares").focus()
            page.keyboard.press("Enter")
            output = page.locator("#mat-result")
            assert not output.evaluate("(e) => e.classList.contains('error')"), output.inner_text()
            assert "Leave-one-out prediction residuals (rows 1–3):" in output.inner_text()
            assert "Weighted leave-one-out PRESS:" in output.inner_text()
            assert "not a statistical uncertainty estimate" in output.inner_text()
            fit = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01])")
            for x, expected in zip(fit["looResiduals"], (-6, 3, -6)):
                assert math.isclose(x, expected, abs_tol=1e-9)
            assert math.isclose(fit["looWeightedPress"], 45.36, abs_tol=1e-9)
            assert not page.evaluate("() => document.documentElement.scrollWidth > innerWidth + 1"), width
        singular = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
            "[[1,0],[0,1],[0,1]],[2,3,4],[1,1,1])")
        assert singular["looResiduals"][0] is None and singular["looWeightedPress"] is None
        weights.last.fill("0")
        page.locator("#mat-weighted-least-squares").click()
        assert "Weights must be finite" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        weights.last.fill("0.01")
        page.locator("#mat-weighted-least-squares").click()
        assert not page.locator("#mat-result").evaluate("(e) => e.classList.contains('error')")
        assert page.locator("#mat-send").is_enabled()
        assert not errors, errors
        browser.close()
    print("PASS weighted leave-one-out references, keyboard/mobile and recovery")


if __name__ == "__main__":
    main()
