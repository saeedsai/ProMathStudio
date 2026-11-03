"""Weighted spectral conditioning: responsive keyboard and invalid-weight recovery."""
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
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#mat-weighted-least-squares").focus()
            page.keyboard.press("Enter")
            result = page.locator("#mat-result")
            assert not result.evaluate("(e) => e.classList.contains('error')"), result.inner_text()
            assert "Weighted design spectral condition estimate (2-norm)" in result.inner_text()
            assert "not a certified coefficient-error" in result.inner_text()
            assert "Coefficient roundoff amplification screen" in result.inner_text()
            assert "Relative weighted squared-residual shares (rows 1–3)" in result.inner_text()
            assert "Weighted fitted values (rows 1–3)" in result.inner_text()
            assert "Weighted normwise residual ratio" in result.inner_text()
            assert "Orthogonality acceptance: " in result.inner_text()
            assert "not a certified coefficient-error" in result.inner_text()
            ratio = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01]).weightedNormwiseResidualRatio")
            reference = math.sqrt(12/35) / (
                math.sqrt(61/20)*math.sqrt(2770)/35 + math.sqrt(581)/10)
            assert math.isclose(ratio, reference, rel_tol=1e-11), ratio
            fitted = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01]).fittedValues")
            assert all(math.isclose(v, ref, rel_tol=1e-10) for v, ref in
                zip(fitted, (33/35, 74/35, 23/7))), fitted
            shares = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01]).weightedResidualShares")
            assert all(math.isclose(v, ref, rel_tol=1e-10) for v, ref in
                zip(shares, (1/105, 4/105, 100/105))), shares
            value = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01]).spectralCondition2")
            assert math.isclose(value, 2.5904639930794775, rel_tol=1e-11), value
            assert not page.evaluate("() => document.documentElement.scrollWidth > innerWidth + 1"), width
        # Near-dependent columns with a genuine small residual must not
        # produce a false numerical orthogonality rejection.
        near_fit = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
            "[[1,1],[1,1.00000001],[1,1.00000002]],"
            "[1,0.99999999,0.999999982],[1,1,1])")
        assert abs(near_fit["solution"][0] - 1.9) < 1e-6, near_fit
        assert abs(near_fit["solution"][1] + 0.9) < 1e-6, near_fit
        assert near_fit["normalResidual"] >= 0, near_fit
        assert not near_fit["orthogonalityCheckSkipped"], near_fit
        assert near_fit["orthogonalityTolerance"] > 1e-8, near_fit
        assert "relaxed" in near_fit["orthogonalityGuidance"], near_fit
        # Exercise the near-rank warning in the real browser controller.
        for i,v in enumerate(("1","1","1","1.0000000001","1","1.0000000002")):
            page.locator("#mat-grid input").nth(i).fill(v)
        for i,v in enumerate(("1","0.9999999999","0.9999999998")):
            page.locator("#mat-rhs-grid input").nth(i).fill(v)
        for i in range(3):
            page.locator("#mat-weight-grid input").nth(i).fill("1")
        page.locator("#mat-weighted-least-squares").click()
        assert "Near-rank numerical warning" in page.locator("#mat-result").inner_text()
        page.locator("#mat-weight-grid input").last.fill("0")
        page.locator("#mat-weighted-least-squares").click()
        assert "Weights must be finite" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-weight-grid input").last.fill("0.01")
        page.locator("#mat-weighted-least-squares").click()
        assert page.locator("#mat-send").is_enabled()
        assert not errors, errors
        browser.close()
    print("PASS weighted spectral condition responsive recovery")


if __name__ == "__main__":
    main()
