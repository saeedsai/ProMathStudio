"""Weighted Engineering route: keyboard, 3x2 QR reference, invalid weights, mobile."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TOOL = "matrix.weighted-least-squares.real.3x2"


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        tools = page.evaluate("""() => MathStudio.engineeringCatalog.tools
            .filter(t => t.id === 'matrix.weighted-least-squares.real.3x2')
            .map(t => ({status:t.status,route:t.route,disciplines:t.disciplines}))""")
        assert len(tools) == 1 and tools[0]["status"] == "available", tools
        assert tools[0]["route"] == {
            "mode": "calculator", "target": "matrix",
            "focusId": "mat-weighted-least-squares"}, tools
        assert "mechanical" in tools[0]["disciplines"]

        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator('[data-workspace="engineering"]').click()
            page.locator("#eng-discipline").select_option("mechanical")
            page.locator("#eng-search").fill("weighted least-squares fit")
            card = page.locator(f'#eng-results article[data-tool-id="{TOOL}"]')
            assert card.count() == 1 and card.locator("button").count() == 1
            assert page.locator("#engineering-panel").evaluate(
                "(e) => e.scrollWidth <= e.clientWidth + 1"), width
            page.locator("#calc-input").evaluate('(e) => e.value="11+7"')
            card.locator("button").focus()
            page.keyboard.press("Enter")
            page.wait_for_function(
                "document.activeElement?.id === 'mat-weighted-least-squares'")
            assert page.locator("#matrix-tools").evaluate("(e) => e.open")
            assert page.locator("#calc-input").input_value() == "11+7"

            page.locator("#mat-rows").select_option("3")
            page.locator("#mat-cols").select_option("2")
            cells = page.locator("#mat-grid input")
            assert cells.count() == 6
            for i, value in enumerate(("1", "0", "1", "1", "1", "2")):
                cells.nth(i).fill(value)
            rhs = page.locator("#mat-rhs-grid input")
            weights = page.locator("#mat-weight-grid input")
            assert rhs.count() == weights.count() == 3
            for i, value in enumerate(("1", "2", "9")):
                rhs.nth(i).fill(value)
            for i, value in enumerate(("1", "1", "0.01")):
                weights.nth(i).fill(value)
            page.locator("#mat-weighted-least-squares").click()
            result = page.evaluate(
                "() => MathStudio.matrixTools.calculate('weightedLeastSquares')")
            assert result["operation"] == "weightedLeastSquares", result
            for actual, expected in zip(result["value"]["solution"], (33/35, 41/35)):
                assert math.isclose(actual, expected, abs_tol=1e-10, rel_tol=1e-10), result
            assert math.isclose(result["value"]["weightedResidualSquared"],
                                12/35, abs_tol=1e-10, rel_tol=1e-10), result
            assert not page.locator("#mat-result").evaluate(
                "(e) => e.classList.contains('error')")
            weights.last.fill("0")
            page.locator("#mat-weighted-least-squares").click()
            assert "Weights must be finite" in page.locator("#mat-result").inner_text()
            assert page.locator("#mat-send").is_disabled()
            weights.last.fill("0.01")
            page.locator("#mat-weighted-least-squares").click()
            assert page.locator("#mat-send").is_enabled()
            page.locator("#mat-cols").select_option("3")
            page.locator("#mat-weighted-least-squares").click()
            assert "3×2" in page.locator("#mat-result").inner_text()
            page.locator("#mat-cols").select_option("2")
            assert not page.evaluate(
                "() => document.documentElement.scrollWidth > innerWidth + 1"), width
        assert not errors, errors
        browser.close()
    print("PASS Engineering weighted route, 3x2 reference, invalid weights, keyboard/mobile")


if __name__ == "__main__":
    main()
