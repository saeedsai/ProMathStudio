"""Weighted least-squares condition screening: references, accessible UI and recovery."""
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
            assert "Relative weight ratio (max/min):" in output.inner_text()
            assert "Weighted design QR diagonal spread (heuristic):" in output.inner_text()
            result = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                                   "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01])")
            assert math.isclose(result["weightRatio"], 100, rel_tol=1e-12)
            assert result["qrDiagonalSpread"] >= 1
            assert math.isclose(result["solution"][0], 33/35, abs_tol=1e-10)
            assert not page.evaluate("() => document.documentElement.scrollWidth > innerWidth + 1"), width
        weights.last.fill("0")
        page.locator("#mat-weighted-least-squares").click()
        assert "Weights must be finite" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        weights.last.fill("0.01")
        page.locator("#mat-weighted-least-squares").click()
        assert not page.locator("#mat-result").evaluate("(e) => e.classList.contains('error')")
        assert page.locator("#mat-send").is_enabled()
        extreme = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
            "[[1,0],[0,1],[1,1]],[2,3,5],[1e-12,1,1e12])")
        assert extreme["weightRatio"] == 1e24 and all(math.isfinite(x) for x in extreme["solution"])
        assert "Potential sensitivity" in extreme["conditioningAdvisory"]
        assert not errors, errors
        browser.close()
    print("PASS weighted least-squares QR screening, scale, mobile and error recovery")


if __name__ == "__main__":
    main()
