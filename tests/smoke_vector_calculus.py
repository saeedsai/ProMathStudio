"""Numerical derivatives (Ridders) and vector calculus: references, refusals and responsive browser UI."""
from pathlib import Path
import math
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

CALL = """([k, o]) => MathStudio.vectorCalculus[k](o)"""
FAILS = """([k, o]) => {try {MathStudio.vectorCalculus[k](o); return '';} catch (e) {return e.message;}}"""


def close(a, b, tol):
    return abs(a - b) <= tol


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert '<script id="promath-vector-calculus">' in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        run = lambda k, o: page.evaluate(CALL, [k, o])
        fails = lambda k, o: page.evaluate(FAILS, [k, o])

        # Ordinary derivatives with error estimates.
        d1 = run("derivative", {"expression": "sin(x)", "x": 1})
        assert close(d1["value"], math.cos(1), 1e-12) and 0 <= d1["error"] < 1e-10, d1
        d4 = run("derivative", {"expression": "exp(x)", "x": 0, "order": 4})
        assert close(d4["value"], 1, 1e-6) and d4["error"] < 1e-6, d4
        d2 = run("derivative", {"expression": "exp(x)", "x": 0, "order": 2})
        assert close(d2["value"], 1, 1e-9), d2
        d3 = run("derivative", {"expression": "x^4", "x": 2, "order": 3})
        assert close(d3["value"], 48, 1e-6), d3
        big = run("derivative", {"expression": "x^3", "x": 1e6, "order": 2})  # step scaled to |x|
        assert close(big["value"], 6e6, 1e-3), big
        osc = run("derivative", {"expression": "sin(1000*x)", "x": 0.3})  # smaller-start retry
        assert close(osc["value"], 1000 * math.cos(300), 1e-6), osc
        log = run("derivative", {"expression": "ln(x)", "x": 0.001})  # near a domain boundary
        assert close(log["value"], 1000, 1e-6), log

        # Gradient, Hessian, Jacobian, divergence, curl, Laplacian, directional.
        g = run("gradient", {"expression": "x^2*y+z^3", "point": [1, 2, 3]})
        for got, exp in zip(g["values"], [4, 1, 27]):
            assert close(got, exp, 1e-9), g
        assert len(g["errors"]) == 3 and all(e >= 0 for e in g["errors"]), g
        h = run("hessian", {"expression": "x^2*y", "point": [1, 2]})
        for row, ref in zip(h["matrix"], [[4, 2], [2, 0]]):
            for got, exp in zip(row, ref):
                assert close(got, exp, 1e-8), h
        assert h["matrix"][0][1] == h["matrix"][1][0] and h["symmetric"], h
        h3 = run("hessian", {"expression": "sin(x)*cos(y)*exp(z)", "point": [0.3, 0.7, 0.2]})
        s, c, e = math.sin(0.3), math.cos(0.7), math.exp(0.2)
        assert close(h3["matrix"][0][1], -math.cos(0.3) * math.sin(0.7) * e, 1e-8), h3
        assert close(h3["matrix"][2][2], s * c * e, 1e-8), h3
        j = run("jacobian", {"field": "x*y; x+y", "point": [1, 2]})
        for row, ref in zip(j["matrix"], [[2, 1], [1, 1]]):
            for got, exp in zip(row, ref):
                assert close(got, exp, 1e-9), j
        j32 = run("jacobian", {"field": ["x^2", "x*y", "y^3"], "point": [1, 2]})
        assert len(j32["matrix"]) == 3 and close(j32["matrix"][2][1], 12, 1e-8), j32
        div = run("divergence", {"field": "x; y; z", "point": [1, 2, 3]})
        assert close(div["value"], 3, 1e-9), div
        curl = run("curl", {"field": "-y; x; 0", "point": [1, 2, 3]})
        for got, exp in zip(curl["values"], [0, 0, 2]):
            assert close(got, exp, 1e-9), curl
        curl2 = run("curl", {"field": "-y; x", "point": [1, 2]})
        assert curl2["scalar"] and close(curl2["value"], 2, 1e-9), curl2
        lap = run("laplacian", {"expression": "x^2+y^2+z^2", "point": [1, 1, 1]})
        assert close(lap["value"], 6, 1e-8), lap
        dd = run("directional", {"expression": "x^2*y+z^3", "point": [1, 2, 3], "direction": [1, 2, 2]})
        assert close(dd["value"], (4 + 2 + 54) / 3, 1e-9) and close(math.hypot(*dd["unit"]), 1, 1e-15), dd
        via = page.evaluate("""() => MathStudio.vectorCalculus.compute('divergence', {field: 'x*y; y*z; z*x', point: [1, 2, 3]})""")
        assert close(via["value"], 2 + 3 + 1, 1e-9), via

        # Refusals: kinks, jumps, non-finite values and invalid inputs.
        assert "non-differentiable" in fails("derivative", {"expression": "abs(x)", "x": 0})
        assert "non-differentiable" in fails("gradient", {"expression": "abs(x)+y", "point": [0, 1]})
        assert "non-differentiable" in fails("derivative", {"expression": "floor(x)", "x": 1})
        assert "exceeds the threshold" in fails("derivative", {"expression": "sign(x)", "x": 0})
        assert "Division by zero" in fails("derivative", {"expression": "1/x", "x": 0})
        assert "domain boundary" in fails("derivative", {"expression": "sqrt(x)", "x": 0})
        assert "Unknown variable" in fails("derivative", {"expression": "q+x", "x": 1})
        assert "order" in fails("derivative", {"order": 5})
        assert "order" in fails("derivative", {"order": 1.5})
        assert "required" in fails("derivative", {"x": ""})
        assert "1–1000" in fails("gradient", {"expression": " ", "point": [1, 2]})
        assert "coordinates" in fails("gradient", {"point": [1, 2, 3, 4]})
        assert "finite" in fails("gradient", {"point": [1, "abc"]})
        assert "1e8" in fails("gradient", {"point": [1e9, 0]})
        assert "semicolons" in fails("jacobian", {"field": "x", "point": [1, 2]})
        assert "semicolons" in fails("jacobian", {"field": "x; ", "point": [1, 2]})
        assert "as many" in fails("divergence", {"field": "x; y", "point": [1, 2, 3]})
        assert "Curl needs" in fails("curl", {"field": "x; y; z", "point": [1, 2]})
        assert "non-zero" in fails("directional", {"direction": [0, 0, 0]})
        assert "match" in fails("directional", {"direction": [1, 1]})
        assert "threshold" in fails("gradient", {"tolerance": 0})
        assert "Unknown operation" in page.evaluate(
            """() => {try {MathStudio.vectorCalculus.compute('nope', {}); return '';} catch (e) {return e.message;}}""")

        # UI: derivative via keyboard, then Hessian, curl and error recovery.
        page.locator('[data-workspace="editor"]').click()
        page.locator("#vectorcalc-details").evaluate("e => e.open = true")
        output = page.locator("#vc-output")
        assert output.get_attribute("role") == "status" and output.get_attribute("aria-live") == "polite"
        assert not page.locator("#vc-y").is_visible() and page.locator("#vc-order").is_visible()
        page.locator("#vc-expression").fill("sin(x)")
        page.locator("#vc-x").fill("1")
        page.locator("#vc-run").focus()
        page.keyboard.press("Enter")
        text = output.inner_text()
        assert "Value = 0.540302305868" in text and "±" in text and "Evaluations" in text, text
        page.locator("#vc-op").select_option("hessian")
        page.locator("#vc-dim").select_option("2")
        assert page.locator("#vc-y").is_visible() and not page.locator("#vc-z").is_visible() and not page.locator("#vc-order").is_visible()
        page.locator("#vc-expression").fill("x^2*y")
        page.locator("#vc-y").fill("2")
        page.locator("#vc-run").click()
        text = output.inner_text()
        assert "Hessian (symmetric)" in text and "[ " in text and text.count("\n[") >= 1, text
        page.locator("#vc-op").select_option("curl")
        page.locator("#vc-dim").select_option("3")
        assert page.locator("#vc-field").is_visible() and not page.locator("#vc-expression").is_visible()
        page.locator("#vc-field").fill("-y; x; 0")
        page.locator("#vc-run").click()
        assert "Curl ∇×F" in output.inner_text() and "(0, 0, 2)" in output.inner_text(), output.inner_text()
        page.locator("#vc-op").select_option("derivative")
        page.locator("#vc-expression").fill("abs(x)")
        page.locator("#vc-x").fill("0")
        page.locator("#vc-run").click()
        assert "error" in (output.get_attribute("class") or "") and "Adjust" in output.inner_text()
        assert page.locator("#vc-to-table").is_disabled()
        page.locator("#vc-op").select_option("gradient")
        page.locator("#vc-expression").fill("x^2*y+z^3")
        page.locator("#vc-x").fill("1")
        page.locator("#vc-run").click()
        assert "error" not in (output.get_attribute("class") or "") and "(4, 1, 27)" in output.inner_text(), output.inner_text()
        page.locator("#vc-to-table").click()
        exported = page.evaluate("""() => MathStudio.dataTables.tables.find(t => t.name.startsWith('VectorCalculus_gradient'))""")
        assert exported and exported["columns"] == ["quantity", "value", "estimated_error"] and len(exported["rows"]) == 3, exported
        assert abs(float(exported["rows"][2][1]) - 27) < 1e-9, exported

        # Responsive: no horizontal overflow and >=40px controls at 390 and 1280.
        page.locator('[data-workspace="editor"]').click()
        page.locator("#vectorcalc-details").evaluate("e => e.open = true")
        page.locator("#vc-op").select_option("hessian")
        page.locator("#vc-run").click()
        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            assert page.locator("#vc-run").is_visible()
            overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            small = page.evaluate("""() => [...document.querySelectorAll('#vectorcalc-details input, #vectorcalc-details select, #vectorcalc-details button')]
                .filter(e => e.offsetParent !== null && e.getBoundingClientRect().height < 40).map(e => e.id)""")
            assert not small, (width, small)
            box = output.bounding_box()
            assert box["x"] >= 0 and box["x"] + box["width"] <= width + 1, (width, box)
        assert not errors, errors
        browser.close()
    print("PASS: Ridders derivatives, gradient/Hessian/Jacobian/div/curl/Laplacian/directional references, refusals, table export and responsive UI")


if __name__ == "__main__":
    main()
