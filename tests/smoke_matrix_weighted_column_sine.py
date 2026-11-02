"""Responsive weighted column sine, keyboard and invalid-weight recovery."""
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
        for i, v in enumerate(("1", "0", "1", "1", "1", "2")):
            page.locator("#mat-grid input").nth(i).fill(v)
        for i, v in enumerate(("1", "2", "9")):
            page.locator("#mat-rhs-grid input").nth(i).fill(v)
        for i, v in enumerate(("1", "1", "0.01")):
            page.locator("#mat-weight-grid input").nth(i).fill(v)
        expected = math.sqrt(1.05 / (2.01 * 1.04))
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#mat-weighted-least-squares").focus()
            page.keyboard.press("Enter")
            result = page.locator("#mat-result")
            assert not result.evaluate("(e) => e.classList.contains('error')"), result.inner_text()
            assert "Weighted design column independence (sine):" in result.inner_text()
            assert "not a certified condition number" in result.inner_text()
            value = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01]).designColumnSine")
            assert math.isclose(value, expected, abs_tol=1e-12), value
            assert not page.evaluate("() => document.documentElement.scrollWidth > innerWidth + 1"), width
        near = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
            "[[1,1],[1,1.0001],[1,1.0002]],[1,1.0001,1.0002],[1,1,1])")
        assert 0 < near["designColumnSine"] < 1e-4
        assert "nearly parallel" in near["designColumnGuidance"]
        page.locator("#mat-weight-grid input").last.fill("0")
        page.locator("#mat-weighted-least-squares").click()
        assert "Weights must be finite" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-weight-grid input").last.fill("0.01")
        page.locator("#mat-weighted-least-squares").click()
        assert page.locator("#mat-send").is_enabled()
        assert not errors, errors
        browser.close()
    print("PASS weighted column sine, near-rank warning and responsive recovery")


if __name__ == "__main__":
    main()
