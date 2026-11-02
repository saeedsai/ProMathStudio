"""LOO prediction output, keyboard, responsive layout and error recovery."""
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
            output = page.locator("#mat-result")
            assert not output.evaluate("(e) => e.classList.contains('error')"), output.inner_text()
            assert "Leave-one-out predictions (rows 1–3):" in output.inner_text()
            assert "predicted minus observed" in output.inner_text()
            values = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
                "[[1,0],[1,1],[1,2]],[1,2,9],[1,1,0.01]).looPredictions")
            assert all(math.isclose(v, expected, abs_tol=1e-9)
                       for v, expected in zip(values, (-5, 5, 3))), values
            assert not page.evaluate("() => document.documentElement.scrollWidth > innerWidth + 1"), width
        singular = page.evaluate("() => MathStudio.matrixTools.weightedLeastSquares("
            "[[1,0],[0,1],[0,1]],[2,3,4],[1,1,1]).looPredictions")
        assert singular[0] is None
        page.locator("#mat-weight-grid input").last.fill("0")
        page.locator("#mat-weighted-least-squares").click()
        assert "Weights must be finite" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-weight-grid input").last.fill("0.01")
        page.locator("#mat-weighted-least-squares").click()
        assert page.locator("#mat-send").is_enabled()
        assert not errors, errors
        browser.close()
    print("PASS weighted LOO predictions and responsive recovery")


if __name__ == "__main__":
    main()
