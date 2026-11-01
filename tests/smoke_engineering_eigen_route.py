"""Engineering symmetric eigen route: 3x3 reference, invalid symmetry, keyboard/mobile recovery."""
import math
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TOOL = "matrix.eigen.symmetric.small"


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        tools = page.evaluate("""() => MathStudio.engineeringCatalog.tools
            .filter(t => t.id === 'matrix.eigen.symmetric.small')
            .map(t => ({status:t.status,route:t.route,disciplines:t.disciplines}))""")
        assert len(tools) == 1, tools
        assert tools[0]["status"] == "available", tools
        assert tools[0]["route"] == {
            "mode": "calculator", "target": "matrix", "focusId": "mat-eigen"}, tools
        assert "aerospace" in tools[0]["disciplines"]

        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator('[data-workspace="engineering"]').click()
            page.locator("#eng-discipline").select_option("aerospace")
            page.locator("#eng-search").fill("symmetric eigenanalysis")
            card = page.locator(f'#eng-results article[data-tool-id="{TOOL}"]')
            assert card.count() == 1 and card.locator("button").count() == 1
            assert page.locator("#engineering-panel").evaluate(
                "(e) => e.scrollWidth <= e.clientWidth + 1"), width
            page.locator("#calc-input").evaluate('(e) => e.value="11+7"')
            card.locator("button").focus()
            page.keyboard.press("Enter")
            page.wait_for_function("document.activeElement?.id === 'mat-eigen'")
            assert page.locator("#matrix-tools").evaluate("(e) => e.open")
            assert page.locator("#calc-input").input_value() == "11+7"

            page.locator("#mat-rows").select_option("3")
            page.locator("#mat-cols").select_option("3")
            cells = page.locator("#mat-grid input")
            assert cells.count() == 9
            matrix = ("2", "1", "0", "1", "2", "0", "0", "0", "4")
            for i, value in enumerate(matrix):
                cells.nth(i).fill(value)
            page.locator("#mat-eigen").focus()
            page.keyboard.press("Enter")
            output = page.locator("#mat-result").inner_text()
            assert "Eigenvalues (descending):" in output, output
            assert not page.locator("#mat-result").evaluate(
                "(e) => e.classList.contains('error')")
            match = re.search(r"Reconstruction residual:\s*([0-9.eE+-]+)", output)
            assert match and float(match.group(1)) < 1e-10, output
            result = page.evaluate("""() => MathStudio.matrixTools.eigenSymmetric(
                [[2,1,0],[1,2,0],[0,0,4]])""")
            assert all(math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10)
                       for a, b in zip(result["values"], (4, 3, 1))), result
            assert result["residual"] < 1e-10, result
            assert result["orthogonality"] < 1e-10, result

            # Reject nonsymmetric input; correcting it must restore the solver.
            cells.nth(3).fill("0")
            page.locator("#mat-eigen").click()
            assert page.locator("#mat-result").evaluate(
                "(e) => e.classList.contains('error')")
            assert "symmetric" in page.locator("#mat-result").inner_text().lower()
            cells.nth(3).fill("1")
            cells.nth(0).fill("")
            page.locator("#mat-eigen").click()
            assert page.locator("#mat-result").evaluate(
                "(e) => e.classList.contains('error')")
            cells.nth(0).fill("2")
            page.locator("#mat-eigen").click()
            assert not page.locator("#mat-result").evaluate(
                "(e) => e.classList.contains('error')")
            assert not page.evaluate(
                "() => document.documentElement.scrollWidth > innerWidth + 1"), width
        assert not errors, errors
        browser.close()
    print("PASS Engineering eigen route, 3x3 reference, invalid symmetry, keyboard and mobile recovery")


if __name__ == "__main__":
    main()
