"""RREF/rank regression: scaled pivots, degenerate matrices and editor UI."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def close(actual, expected):
    return len(actual) == len(expected) and all(
        len(a) == len(b) and all(math.isclose(x, y, rel_tol=1e-10, abs_tol=1e-10)
        for x, y in zip(a, b)) for a, b in zip(actual, expected))

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":1280,"height":850})
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        panel = page.locator("#matrix-tools")
        panel.evaluate("(el) => el.open = true")
        cases = [
            ([[1,2],[3,4]], 2, [[1,0],[0,1]]),
            ([[1,2,3],[2,4,6]], 1, [[1,2,3],[0,0,0]]),
            ([[0,0],[0,0]], 0, [[0,0],[0,0]]),
            ([[0,1,2],[0,0,3]], 2, [[0,1,0],[0,0,1]]),
            ([[1,1],[1,1+1e-14]], 1, [[1,1],[0,0]]),
            ([[1e12,0],[0,1]], 2, [[1,0],[0,1]]),
            ([[1,0,0],[0,1,0],[0,0,1]], 3, [[1,0,0],[0,1,0],[0,0,1]]),
        ]
        for matrix, rank, expected in cases:
            result = page.evaluate("(matrix) => MathStudio.matrixTools.rref(matrix)", matrix)
            assert result["rank"] == rank, (matrix, result)
            assert close(result["matrix"], expected), (matrix, result)
            assert page.evaluate("(matrix) => MathStudio.matrixTools.rank(matrix)", matrix) == rank
        invalid = page.evaluate("""() => {
            try { MathStudio.matrixTools.rref([[1, Infinity],[2,3]]); return ''; }
            catch (e) { return e.message; }
        }""")
        assert "finite" in invalid
        invalid = page.evaluate("""() => {
            try { MathStudio.matrixTools.rref([[1,2,3],[4,5]]); return ''; }
            catch (e) { return e.message; }
        }""")
        assert "rectangular" in invalid
        for index, value in enumerate(["1","2","2","4"]):
            page.locator("#mat-grid input").nth(index).fill(value)
        page.locator("#mat-rref").click()
        assert "Rank: 1" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-send").click()
        assert "matrix(" in page.locator("#equation-input").input_value()
        page.locator('[data-workspace="calculator"]').click()
        panel.evaluate("(el) => el.open = true")
        page.locator("#mat-rank").click()
        assert page.locator("#mat-result").inner_text().strip().endswith("1")
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-grid input").first.fill("3")
        assert page.locator("#mat-send").is_disabled()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#mat-rref").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: RREF/rank references, scaled pivots, invalids, UI, editor and responsive layout")

if __name__ == "__main__":
    main()
