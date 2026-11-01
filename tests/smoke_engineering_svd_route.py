"""Engineering SVD route: mobile/keyboard focus, rank deficiency, reference residuals and recovery."""
import math
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TOOL = "matrix.svd.real.small"


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"),
                         wait_until="load")
        tools = page.evaluate("""() => MathStudio.engineeringCatalog.tools
            .filter(t => t.id === 'matrix.svd.real.small')
            .map(t => ({status:t.status,route:t.route,disciplines:t.disciplines}))""")
        assert len(tools) == 1, tools
        assert tools[0]["status"] == "available", tools
        assert tools[0]["route"] == {
            "mode": "calculator", "target": "matrix", "focusId": "mat-svd"}, tools
        assert "aerospace" in tools[0]["disciplines"]

        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator('[data-workspace="engineering"]').click()
            page.locator("#eng-discipline").select_option("aerospace")
            page.locator("#eng-search").fill("singular value decomposition")
            card = page.locator(f'#eng-results article[data-tool-id="{TOOL}"]')
            assert card.count() == 1 and card.locator("button").count() == 1
            assert page.locator("#engineering-panel").evaluate(
                "(e) => e.scrollWidth <= e.clientWidth + 1"), width
            page.locator("#calc-input").evaluate('(e) => e.value="9+2"')
            card.locator("button").focus()
            page.keyboard.press("Enter")
            page.wait_for_function("document.activeElement?.id === 'mat-svd'")
            assert page.locator("#matrix-tools").evaluate("(e) => e.open")
            assert page.locator("#calc-input").input_value() == "9+2"

            page.locator("#mat-rows").select_option("2")
            page.locator("#mat-cols").select_option("3")
            cells = page.locator("#mat-grid input")
            assert cells.count() == 6
            for i, value in enumerate(("1", "2", "3", "2", "4", "6")):
                cells.nth(i).fill(value)
            page.locator("#mat-svd").focus()
            page.keyboard.press("Enter")
            rank_one = page.locator("#mat-result").inner_text()
            assert "Numerical rank: 1" in rank_one, rank_one
            assert not page.locator("#mat-result").evaluate(
                "(e) => e.classList.contains('error')")

            # An empty matrix entry must be rejected and recoverable.
            cells.nth(5).fill("")
            page.locator("#mat-svd").click()
            assert page.locator("#mat-result").evaluate(
                "(e) => e.classList.contains('error')")
            for i, value in enumerate(("3", "0", "0", "0", "2", "0")):
                cells.nth(i).fill(value)
            page.locator("#mat-svd").click()
            output = page.locator("#mat-result").inner_text()
            assert "Numerical rank: 2" in output, output
            assert "Singular values (descending):" in output, output
            assert not page.locator("#mat-result").evaluate(
                "(e) => e.classList.contains('error')")
            match = re.search(r"Relative reconstruction residual:\s*([0-9.eE+-]+)", output)
            assert match and float(match.group(1)) < 1e-10, output

            # Independent reference: singular values of diagonal 2x3 A are 3, 2.
            values = page.evaluate("""() => MathStudio.matrixTools.svd2x3(
                [[3,0,0],[0,2,0]]).S""")
            assert all(math.isclose(x, y, rel_tol=1e-10)
                       for x, y in zip(values, (3, 2))), values
            assert not page.evaluate(
                "() => document.documentElement.scrollWidth > innerWidth + 1"), width
        assert not errors, errors
        browser.close()
    print("PASS Engineering SVD route, rank deficient, 2x3 reference, keyboard and responsive recovery")


if __name__ == "__main__":
    main()
