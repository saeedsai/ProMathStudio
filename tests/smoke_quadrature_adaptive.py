"""Bounded adaptive Simpson quadrature: references, rejection and browser integration."""
from pathlib import Path
import math
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "function adaptiveSimpson(" in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(html, wait_until="load")
        evaluate = lambda options: page.evaluate("o => MathStudio.numerical.adaptiveSimpson(o)", options)
        sin_result = evaluate({"expression": "sin(x)", "a": 0, "b": math.pi, "tolerance": 1e-9})
        assert abs(sin_result["value"] - 2) < 1e-8, sin_result
        assert sin_result["evaluations"] <= 4096 and sin_result["refinements"] > 0
        polynomial = evaluate({"expression": "x^2", "a": 0, "b": 1, "tolerance": 1e-10})
        assert abs(polynomial["value"] - 1/3) < 1e-12, polynomial
        assert polynomial["estimatedError"] < 1e-10
        constant = evaluate({"expression": "5", "a": 2, "b": 3})
        assert abs(constant["value"] - 5) < 1e-12
        for invalid in [
            {"expression": ""}, {"a": 1, "b": 0}, {"a": 0, "b": 0},
            {"expression": "sqrt(-1)"}, {"expression": "1/0"},
            {"tolerance": 0}, {"tolerance": 1e-15}, {"tolerance": 0.1},
            {"maxEvaluations": 15}, {"maxEvaluations": 20001},
            {"maxEvaluations": 16, "expression": "sin(40*x)", "a": 0, "b": 1, "tolerance": 1e-12},
        ]:
            assert page.evaluate("""o => {try {MathStudio.numerical.adaptiveSimpson(o);return false;}catch(e){return !!e.message;}}""", invalid), invalid
        page.locator('[data-workspace="solver"]').click()
        page.locator("#num-details").evaluate("(e) => e.open=true")
        page.locator("#num-method").select_option("quadrature")
        assert page.locator("#num-tolerance").is_visible()
        assert page.locator("#num-budget").is_visible()
        assert not page.locator("#num-nx").is_visible()
        page.locator("#num-expression").fill("sin(x)")
        page.locator("#num-start").fill("0")
        page.locator("#num-end").fill(str(math.pi))
        page.locator("#num-run").click()
        output = page.locator("#num-output").inner_text()
        assert "Adaptive Simpson" in output and "Integral:" in output and "Estimated error:" in output, output
        assert page.locator("#num-to-table").is_disabled()
        assert page.locator("#num-to-graph").is_disabled()
        page.locator("#num-tolerance").fill("0")
        page.locator("#num-run").click()
        assert "tolerance" in page.locator("#num-output").inner_text().lower()
        page.locator("#num-method").select_option("poisson")
        assert page.locator("#num-tolerance").is_hidden()
        page.locator("#num-expression").fill("pi^2*sin(pi*x)")
        page.locator("#num-end").fill("1")
        page.locator("#num-run").click()
        assert "finite differences" in page.locator("#num-output").inner_text()
        assert page.locator("#num-to-table").is_enabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#num-details").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: adaptive Simpson references, errors, budget, UI and existing Poisson handoff")

if __name__ == "__main__":
    main()
