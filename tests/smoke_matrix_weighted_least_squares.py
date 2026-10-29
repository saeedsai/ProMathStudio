"""Weighted 3x2 QR least-squares UI, numerical reference and invalid-input browser regression."""
import math
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
        page.locator("#matrix-tools").evaluate("(el) => el.open = true")
        page.locator("#mat-rows").select_option("3")
        assert page.locator("#mat-weight-grid input").count() == 3
        assert page.locator("#mat-weight-grid input").all_input_values() == ["1", "1", "1"]
        for i, value in enumerate(["1", "0", "1", "1", "1", "2"]):
            page.locator("#mat-grid input").nth(i).fill(value)
        for i, value in enumerate(["1", "2", "9"]):
            page.locator("#mat-rhs-grid input").nth(i).fill(value)
        for i, value in enumerate(["1", "1", "0.01"]):
            page.locator("#mat-weight-grid input").nth(i).fill(value)
        page.locator("#mat-weighted-least-squares").click()
        result = page.evaluate("() => MathStudio.matrixTools.calculate('weightedLeastSquares')")
        assert result["operation"] == "weightedLeastSquares"
        expected = [33 / 35, 41 / 35]
        for actual, target in zip(result["value"]["solution"], expected):
            assert math.isclose(actual, target, rel_tol=1e-10, abs_tol=1e-10), result
        assert math.isclose(result["value"]["weightedResidualSquared"], 12 / 35, rel_tol=1e-10)
        output = page.locator("#mat-result").inner_text()
        assert "weightedLeastSquares:" in output and "Weighted squared residual:" in output, output
        assert "Weighted orthogonality:" in output, output
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-send").click()
        editor = page.locator("#equation-input").input_value()
        assert "matrix([0.942857142857],[1.17142857143])" in editor, editor

        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(el) => el.open = true")
        page.locator("#mat-weight-grid input").last.fill("0")
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-weighted-least-squares").click()
        assert "Weights must be finite" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-weight-grid input").last.fill("0.01")
        page.locator("#mat-weighted-least-squares").click()
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-rows").select_option("2")
        assert page.locator("#mat-weight-grid input").count() == 2
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-weighted-least-squares").click()
        assert "3×2" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#mat-weighted-least-squares").is_visible()
        assert page.locator("#mat-weight-grid input").count() == 2
        assert not errors, errors
        browser.close()
    print("PASS: weighted QR 3x2 fit, UI, editor transfer, validation, mobile")


if __name__ == "__main__":
    main()
