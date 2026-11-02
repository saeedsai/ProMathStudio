"""Weighted least-squares guidance accessibility, scale invariance and recovery."""
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
        help_text = page.locator("#mat-weight-guidance").inner_text()
        assert "same positive factor" in help_text
        assert "consistent units" in help_text
        assert "uncertainty estimates" in help_text
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 850})
            inputs = page.locator("#mat-weight-grid input")
            assert inputs.count() == 3
            assert all(inputs.nth(i).get_attribute("aria-describedby") == "mat-weight-guidance"
                       for i in range(3))
            assert page.locator("#mat-weight-guidance").is_visible()
        for i, value in enumerate(("1", "0", "1", "1", "1", "2")):
            page.locator("#mat-grid input").nth(i).fill(value)
        for i, value in enumerate(("1", "2", "9")):
            page.locator("#mat-rhs-grid input").nth(i).fill(value)
        weights = page.locator("#mat-weight-grid input")
        for i, value in enumerate(("1", "1", "0.01")):
            weights.nth(i).fill(value)
        page.locator("#mat-weighted-least-squares").click()
        first = page.evaluate("() => MathStudio.matrixTools.calculate('weightedLeastSquares').value")
        assert math.isclose(first["weightedResidualSquared"], 12/35, rel_tol=1e-10)
        for i, value in enumerate(("100", "100", "1")):
            weights.nth(i).fill(value)
        page.locator("#mat-weighted-least-squares").click()
        scaled = page.evaluate("() => MathStudio.matrixTools.calculate('weightedLeastSquares').value")
        assert all(math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10)
                   for a, b in zip(first["solution"], scaled["solution"]))
        assert math.isclose(scaled["weightedResidualSquared"],
                            100 * first["weightedResidualSquared"], rel_tol=1e-10)
        for i, value in enumerate(("1", "2", "2", "4", "3", "6")):
            page.locator("#mat-grid input").nth(i).fill(value)
        page.locator("#mat-weighted-least-squares").click()
        assert "Rank-deficient" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        for i, value in enumerate(("1", "0", "1", "1", "1", "2")):
            page.locator("#mat-grid input").nth(i).fill(value)
        page.locator("#mat-weighted-least-squares").click()
        assert page.locator("#mat-send").is_enabled()
        assert not errors, errors
        browser.close()
    print("PASS weighted guidance, accessibility, scaling, rank recovery and responsive UI")


if __name__ == "__main__":
    main()
