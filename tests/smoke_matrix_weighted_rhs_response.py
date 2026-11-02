"""Weighted RHS response: numerical reference, keyboard, mobile and recovery."""
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
        for i, value in enumerate(("1", "0", "1", "1", "1", "2")):
            cells.nth(i).fill(value)
        for i, value in enumerate(("1", "2", "9")):
            rhs.nth(i).fill(value)
        for i, value in enumerate(("1", "1", "0.01")):
            weights.nth(i).fill(value)
        expected = ((104/105, -102/105), (2/105, 99/105), (-1/105, 3/105))
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#mat-weighted-least-squares").focus()
            page.keyboard.press("Enter")
            output = page.locator("#mat-result")
            assert not output.evaluate("(e) => e.classList.contains('error')"), output.inner_text()
            assert "RHS +1-unit response (rows 1–3" in output.inner_text()
            assert "not a statistical uncertainty or error bound" in output.inner_text()
            fit = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01])")
            for row, ref in zip(fit["rhsResponseRows"], expected):
                for actual, value in zip(row, ref):
                    assert math.isclose(actual, value, abs_tol=1e-11)
            assert not page.evaluate("() => document.documentElement.scrollWidth > innerWidth + 1"), width
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
    print("PASS weighted RHS response, keyboard/mobile and recovery")


if __name__ == "__main__":
    main()
