"""Two-scale cusp detection without false tangential-root classification."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def solve(expr):
            return page.evaluate(
                """expr => window.MathStudio.numerical.scalarRoots(
                    expr,'x',-1,1,{samples:350,tolerance:1e-9})""", expr)

        for expr in ("abs(x)", "sqrt(abs(x))"):
            result = solve(expr)
            assert result["roots"], result
            i = min(range(len(result["roots"])), key=lambda j: abs(result["roots"][j]))
            assert abs(result["roots"][i]) < 1e-9, result
            assert result["localSlopeWarnings"][i] == "possible-cusp", result
            assert "not a mathematical certificate" in result["note"], result

        for expr in ("x^2", "x^4", "x^3", "x-0.5"):
            result = solve(expr)
            assert result["roots"], result
            assert all(flag == "none" for flag in result["localSlopeWarnings"]), result

        boundary = solve("sqrt(x)")
        assert boundary["roots"] and "forward" in boundary["localSlopeMethods"], boundary
        assert all(flag == "none" for flag in boundary["localSlopeWarnings"]), boundary
        assert solve("x-x")["localSlopeWarnings"] == []
        jump = solve("0.00001*(x-0.12345)/sqrt((x-0.12345)^2)")
        assert jump["roots"] == [] and jump["localSlopeWarnings"] == [], jump

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("abs(x)")
        page.locator("#num-start").fill("-1")
        page.locator("#num-end").fill("1")
        output = page.locator("#num-output")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#num-run").click()
            assert "Possible non-smooth cusp roots (heuristic): 1" in output.inner_text()
            assert output.get_attribute("aria-live") == "polite"
        page.locator("#num-end").fill("-2")
        page.locator("#num-run").click()
        assert output.evaluate("(el) => el.classList.contains('error')")
        page.locator("#num-end").fill("1")
        page.locator("#num-expression").fill("x^2")
        page.locator("#num-run").click()
        assert "Possible non-smooth cusp roots (heuristic): 0" in output.inner_text()
        assert not output.evaluate("(el) => el.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS cusp screening, smooth tangencies, boundaries and UI recovery")


if __name__ == "__main__":
    main()
