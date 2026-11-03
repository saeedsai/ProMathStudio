"""Double/triple Gauss-Kronrod and discrete-data integration: references, refusals and browser UI."""
from pathlib import Path
import math
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

CALL = """([k, o]) => MathStudio.integration[k](o)"""
FAILS = """([k, o]) => {try {MathStudio.integration[k](o); return '';} catch (e) {return e.message;}}"""


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert '<script id="promath-integration-tools">' in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        run = lambda k, o: page.evaluate(CALL, [k, o])
        fails = lambda k, o: page.evaluate(FAILS, [k, o])

        # Double-integral references.
        refs = [
            ({"expression": "x*y"}, 0.25, 1e-12),
            ({"expression": "sin(y)", "a": 0, "b": math.pi, "lower": "0", "upper": "x"}, math.pi, 1e-9),
            ({"expression": "1", "a": 0, "b": 1, "lower": "0", "upper": "sqrt(1-x^2)"}, math.pi / 4, 1e-6),
            ({"expression": "exp(-(x^2+y^2))", "a": -3, "b": 3, "lower": "-3", "upper": "3"}, math.pi * math.erf(3) ** 2, 1e-7),
            # ∫0^1 ∫_{x^2}^{x} (x+y) dy dx = 1/3 - 1/4 + 1/6 - 1/10 = 3/20.
            ({"expression": "x+y", "a": 0, "b": 1, "lower": "x^2", "upper": "x"}, 3 / 20, 1e-10),
        ]
        for options, expected, tol in refs:
            r = run("double", options)
            assert abs(r["value"] - expected) < tol, (options, r)
            assert r["estimatedError"] >= 0 and r["evaluations"] <= 200000, r
            assert "not a certified bound" in r["note"]
        # Reversed inner limits flip orientation.
        rev = run("double", {"expression": "1", "lower": "1", "upper": "0"})
        assert abs(rev["value"] + 1) < 1e-12, rev

        # Triple-integral references over boxes.
        cube = run("triple", {"expression": "x*y*z"})
        assert abs(cube["value"] - 0.125) < 1e-12, cube
        box = run("triple", {"expression": "1", "a": 0, "b": 2, "c": 0, "d": 3, "e": 0, "g": 4})
        assert abs(box["value"] - 24) < 1e-10, box
        expo = run("triple", {"expression": "exp(x+y+z)"})
        assert abs(expo["value"] - (math.e - 1) ** 3) < 1e-9, expo

        # Refusals: singularity, budget, ordering, tolerance and inputs.
        msg = fails("double", {"expression": "1/(x-0.5)"})
        assert "singular" in msg.lower() or "not finite" in msg.lower(), msg
        msg = fails("double", {"expression": "1/(x-0.31234567)"})
        assert msg, "near-singular integrand must be refused"
        msg = fails("double", {"expression": "sin(200*x*y)", "maxEvaluations": 1000})
        assert "budget" in msg.lower(), msg
        assert "exceed" in fails("double", {"a": 1, "b": 1})
        assert "exceed" in fails("double", {"a": 2, "b": 1})
        assert "exceed" in fails("triple", {"e": 1, "g": 0})
        assert fails("double", {"tolerance": 0})
        assert fails("double", {"maxEvaluations": 999})
        assert fails("double", {"expression": ""})
        assert fails("double", {"upper": "sqrt(x-2)"})
        assert fails("triple", {"expression": "log(x-0.5)"})  # complex for x<0.5
        integrable = run("double", {"expression": "ln(x)"})  # integrable endpoint singularity not on a node
        assert abs(integrable["value"] + 1) < 1e-6, integrable

        # Discrete data.
        xs = [0, 0.5, 1, 1.5, 2]
        sq = run("discrete", {"x": xs, "y": [x * x for x in xs]})
        assert abs(sq["trapezoid"] - 2.75) < 1e-12 and abs(sq["simpson"] - 8 / 3) < 1e-12, sq
        cubic = run("discrete", {"x": xs, "y": [x ** 3 for x in xs]})
        assert abs(cubic["simpson"] - 4) < 1e-12, cubic
        assert abs(cubic["rows"][-1][2] - cubic["trapezoid"]) < 1e-15
        nonuni = run("discrete", {"x": [0, 1, 3], "y": [1, 3, 2]})
        assert abs(nonuni["trapezoid"] - 7) < 1e-12 and nonuni["simpson"] is None and "non-uniform" in nonuni["simpsonNote"], nonuni
        odd = run("discrete", {"x": [0, 1, 2, 3], "y": [0, 1, 2, 3]})
        assert odd["simpson"] is None and "odd" in odd["simpsonNote"] and abs(odd["trapezoid"] - 4.5) < 1e-12
        blanks = run("discrete", {"x": ["0", "", "1", "2"], "y": ["0", "5", "1", ""]})
        assert blanks["ignored"] == 2 and blanks["points"] == 2 and abs(blanks["trapezoid"] - 0.5) < 1e-12, blanks
        assert "ascending" in fails("discrete", {"x": [0, 2, 1], "y": [1, 1, 1]})
        assert "ascending" in fails("discrete", {"x": [0, 1, 1], "y": [1, 1, 1]})
        assert "two" in fails("discrete", {"x": [1], "y": [1]})
        assert fails("discrete", {"x": [0, "abc"], "y": [1, 2]})

        # Table-backed integration through the Data Tables API.
        page.evaluate("""() => MathStudio.dataTables.importData({headers:['t','v'],rows:[['0','0'],['1','1'],['2','4'],['3','9'],['4','16']]},'IntSrc')""")
        tab = run("discreteFromTable", {"table": "IntSrc", "xColumn": 0, "yColumn": 1})
        assert abs(tab["simpson"] - 64 / 3) < 1e-12 and abs(tab["trapezoid"] - 22) < 1e-12, tab
        assert fails("discreteFromTable", {"table": "IntSrc", "xColumn": 0, "yColumn": 0})

        # UI: double integral via keyboard.
        page.locator('[data-workspace="editor"]').click()
        page.locator("#integration-details").evaluate("e => e.open = true")
        page.locator("#int-expression").fill("sin(y)")
        page.locator("#int-b").fill(str(math.pi))
        page.locator("#int-g2").fill("x")
        page.locator("#int-run").focus()
        page.keyboard.press("Enter")
        output = page.locator("#int-output")
        text = output.inner_text()
        assert "Integral ≈ 3.14159265359" in text and "Estimated error" in text and "Evaluations" in text, text
        assert output.get_attribute("role") == "status" and output.get_attribute("aria-live") == "polite"
        # Error and recovery.
        page.locator("#int-expression").fill("1/(x-0.5)")
        page.locator("#int-g2").fill("1")
        page.locator("#int-b").fill("1")
        page.locator("#int-run").click()
        assert "error" in (output.get_attribute("class") or "") and "Adjust the inputs" in output.inner_text()
        page.locator("#int-expression").fill("x*y")
        page.locator("#int-run").click()
        assert "error" not in (output.get_attribute("class") or "") and "Integral ≈ 0.25" in output.inner_text()
        # Triple mode.
        page.locator("#int-mode").select_option("triple")
        assert page.locator("#int-c").is_visible() and not page.locator("#int-g1").is_visible()
        page.locator("#int-expression").fill("1")
        page.locator("#int-b").fill("2")
        page.locator("#int-d").fill("3")
        page.locator("#int-f").fill("4")
        page.locator("#int-run").click()
        assert "Integral ≈ 24" in output.inner_text(), output.inner_text()
        # Discrete mode with export of the cumulative column.
        page.locator("#int-mode").select_option("discrete")
        assert not page.locator("#int-expression").is_visible()
        page.locator("#int-table").select_option(label="IntSrc")
        page.locator("#int-run").click()
        text = output.inner_text()
        assert "Trapezoid: 22" in text and "Simpson: 21.3333333333" in text, text
        assert page.locator("#int-to-table").is_enabled()
        page.locator("#int-to-table").click()
        exported = page.evaluate("""() => MathStudio.dataTables.tables.find(t => t.name.startsWith('Integration_Cumulative'))""")
        assert exported and exported["columns"] == ["t", "v", "cumulative_trapezoid"], exported
        assert float(exported["rows"][-1][2]) == 22.0, exported

        # Responsive: no horizontal overflow and ≥40px controls at 390px.
        page.locator('[data-workspace="editor"]').click()
        page.locator("#integration-details").evaluate("e => e.open = true")
        page.locator("#int-mode").select_option("double")
        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            assert page.locator("#int-run").is_visible()
            overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            small = page.evaluate("""() => [...document.querySelectorAll('#integration-details input, #integration-details select, #integration-details button')]
                .filter(e => e.offsetParent !== null && e.getBoundingClientRect().height < 40).map(e => e.id)""")
            assert not small, (width, small)
            box = page.locator("#int-output").bounding_box()
            assert box["x"] >= 0 and box["x"] + box["width"] <= width + 1, (width, box)
        assert not errors, errors
        browser.close()
    print("PASS: double/triple Gauss-Kronrod references, refusals, discrete trapezoid/Simpson, table export and responsive UI")


if __name__ == "__main__":
    main()
