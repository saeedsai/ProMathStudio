"""Cubic spline (natural/clamped/not-a-knot/periodic) and Akima references, failures and browser UI."""
from pathlib import Path
import math
import os
import numpy as np
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
API = "MathStudio.interpolationTools.interpolate"


def natural_reference(xs, ys, queries):
    """Independent second-derivative (M) formulation solved densely with numpy."""
    n = len(xs)
    h = np.diff(xs)
    a = np.zeros((n, n))
    b = np.zeros(n)
    a[0, 0] = a[-1, -1] = 1.0
    for i in range(1, n - 1):
        a[i, i - 1] = h[i - 1]
        a[i, i] = 2 * (h[i - 1] + h[i])
        a[i, i + 1] = h[i]
        b[i] = 6 * ((ys[i + 1] - ys[i]) / h[i] - (ys[i] - ys[i - 1]) / h[i - 1])
    m = np.linalg.solve(a, b)
    out = []
    for x in queries:
        i = min(max(np.searchsorted(xs, x, side="right") - 1, 0), n - 2)
        hi, t0, t1 = h[i], xs[i + 1] - x, x - xs[i]
        y = (m[i] * t0 ** 3 + m[i + 1] * t1 ** 3) / (6 * hi) \
            + (ys[i] / hi - m[i] * hi / 6) * t0 + (ys[i + 1] / hi - m[i + 1] * hi / 6) * t1
        out.append(y)
    return out


def close(a, b, tol, ctx):
    assert abs(a - b) <= tol, (a, b, tol, ctx)


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "function cyclicThomas(sub,diag,sup,rhs)" in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium",
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        run = lambda o: page.evaluate(f"o => {API}(o)", o)

        # Every method reproduces the data nodes exactly.
        pts = [[0, 1], [0.7, -2], [1.5, 3.25], [2.2, 0.5], [3, 1]]
        for method in ["natural", "clamped", "notaknot", "periodic", "akima", "makima"]:
            r = run({"points": pts, "queries": [p[0] for p in pts], "method": method, "endSlopes": [1, -1]})
            assert r["type"] == "interpolation-" + method, r
            assert r["columns"] == ["x", "y", "dy/dx", "d2y/dx2", "integral from x0"], r
            assert [row[1] for row in r["rows"]] == [p[1] for p in pts], (method, r["rows"])
            assert r["rows"][0][4] == 0

        # Hand-checked natural reference (scipy CubicSpline bc_type='natural' agrees): S(1.5)=0.5,
        # M1=-4, M2=4 from 4M1+M2=-12, M1+4M2=12.
        r = run({"points": [[0, 0], [1, 1], [2, 0], [3, 1]], "queries": [0, 0.5, 1.5, 2.5, 3], "method": "natural"})
        close(r["rows"][2][1], 0.5, 1e-14, "natural 1.5")
        close(r["rows"][2][3], 0.0, 1e-12, "natural S'' at 1.5")
        close(r["rows"][0][3], 0.0, 1e-12, "natural S''(x0)")
        close(r["rows"][-1][3], 0.0, 1e-12, "natural S''(xn)")
        # On [0,1]: S = a x + M1 x^3/6 with M1=-4 → S(0.5)=a/2-1/12, a = 1 + 4/6.
        close(r["rows"][1][1], (5 / 3) / 2 - 4 / 48, 1e-14, "natural 0.5")

        # Independent dense M-formulation reference on non-uniform data.
        xs = [0, 0.3, 1.1, 1.7, 2.9, 4.0]
        ys = [1.0, -0.4, 2.2, 0.3, 0.9, -1.5]
        qs = [0.05, 0.6, 1.4, 2.0, 3.3, 3.95]
        r = run({"points": [[a, b] for a, b in zip(xs, ys)], "queries": qs, "method": "natural"})
        for row, ref in zip(r["rows"], natural_reference(xs, ys, qs)):
            close(row[1], ref, 1e-12, ("natural dense", row))

        # Not-a-knot and exact-slope clamped reproduce any cubic, including derivatives and integral.
        f = lambda x: x ** 3 - 2 * x
        nodes = [-1.0, -0.2, 0.5, 1.3, 2.0]
        cubic = [[x, f(x)] for x in nodes]
        qs = [-1, -0.7, 0.1, 0.5, 0.9, 1.6, 2]
        for method, slopes in [("notaknot", None), ("clamped", [3 * 1 - 2, 3 * 4 - 2])]:
            o = {"points": cubic, "queries": qs, "method": method}
            if slopes:
                o["endSlopes"] = slopes
            r = run(o)
            for x, y, d1, d2, integral in r["rows"]:
                close(y, f(x), 1e-12, (method, x))
                close(d1, 3 * x * x - 2, 1e-12, (method, "d1", x))
                close(d2, 6 * x, 1e-11, (method, "d2", x))
                exact = (x ** 4 / 4 - x * x) - (1 / 4 - 1)
                close(integral, exact, 1e-12, (method, "int", x))

        # Integral of clamped spline through x^2 nodes equals x^3/3.
        r = run({"points": [[x, x * x] for x in [0, 0.5, 1.25, 2, 3]], "queries": [0.3, 1, 2.5, 3],
                 "method": "clamped", "endSlopes": [0, 6]})
        for x, y, *_rest, integral in r["rows"]:
            close(integral, x ** 3 / 3, 1e-12, ("x^2 integral", x))

        # Periodic sin on [0, 2pi] with 9 nodes.
        nodes = [2 * math.pi * k / 8 for k in range(9)]
        sin_pts = [[x, math.sin(x)] for x in nodes]
        qs = [2 * math.pi * k / 97 for k in range(98)]
        qs[-1] = nodes[-1]
        r = run({"points": sin_pts, "queries": qs, "method": "periodic"})
        assert max(abs(y - math.sin(x)) for x, y, *_ in r["rows"]) <= 2e-3
        close(r["rows"][0][2], r["rows"][-1][2], 1e-12, "periodic slope")
        close(r["rows"][0][3], r["rows"][-1][3], 1e-12, "periodic curvature")
        close(r["rows"][-1][4], 0.0, 1e-12, "periodic integral of sin")

        # Akima / makima reproduce linear data and do not overshoot a step.
        lin = [[x, 3 * x - 1] for x in [0, 0.4, 1, 1.9, 3, 3.5]]
        for method in ["akima", "makima"]:
            r = run({"points": lin, "queries": [0.2, 0.7, 1.5, 2.6, 3.2], "method": method})
            for x, y, d1, d2, _ in r["rows"]:
                close(y, 3 * x - 1, 1e-12, (method, x))
                close(d1, 3, 1e-12, (method, "d1"))
            step = [[x, 0 if x < 3 else 1] for x in range(7)]
            q = [k / 20 for k in range(121)]
            r = run({"points": step, "queries": q, "method": method})
            ys = [row[1] for row in r["rows"]]
            assert max(ys) <= 1 and min(ys) >= 0, (method, max(ys), min(ys))
        # Natural spline does overshoot the same step (documents the difference).
        r = run({"points": step, "queries": q, "method": "natural"})
        assert max(row[1] for row in r["rows"]) > 1
        # Akima 1970 end extrapolation reference: data (0,0),(1,1),(2,0),(3,0) slope at x0.
        r = run({"points": [[0, 0], [1, 1], [2, 0], [3, 0]], "queries": [0, 1, 2, 3], "method": "akima"})
        # d = [5,3,1,-1,0,1,2]; m0 = (|d3-d2| d1 + |d1-d0| d2)/(...) = (2*3+2*1)/4 = 2
        close(r["slopes"][0], 2, 1e-14, "akima m0")
        close(r["slopes"][1], (1 * 1 + 2 * -1) / 3, 1e-14, "akima m1")

        # Negative cases.
        for invalid in [
            {"points": [[0, 0], [0, 1], [1, 2]], "queries": [0.5], "method": "natural"},
            {"points": [[0, 0], [1, 1], [2, 0]], "queries": [1], "method": "notaknot"},
            {"points": [[0, 0], [1, 1]], "queries": [0.5], "method": "akima"},
            {"points": [[0, 0], [1, 1]], "queries": [0.5], "method": "periodic"},
            {"points": [[0, 0], [1, 1], [2, 0.5]], "queries": [1], "method": "periodic"},
            {"points": [[0, 0], [1, 1], [2, 0]], "queries": [2.5], "method": "natural"},
            {"points": [[0, 0], [1, 1], [2, 0]], "queries": [-0.1], "method": "makima"},
            {"points": [[0, 0], [1, 1], [2, 0]], "queries": [1], "method": "clamped"},
            {"points": [[0, 0], [1, 1], [2, 0]], "queries": [1], "method": "clamped", "endSlopes": [0, "x"]},
            {"points": [[0, 0], [1, 1], [2, 0]], "queries": [1], "method": "spline"},
            {"points": [[0, 0], [1, float("nan")], [2, 0]], "queries": [1], "method": "natural"},
        ]:
            msg = page.evaluate(f"""o => {{ try {{ {API}(o); return null; }} catch(e) {{ return e.message; }} }}""", invalid)
            assert msg, invalid
        msg = page.evaluate(f"""() => {{ try {{ {API}({{points:[[0,0],[1,1],[2,0.5]],queries:[1],method:'periodic'}}); }}
            catch(e) {{ return e.message; }} }}""")
        assert "Periodic" in msg, msg
        # Existing methods unchanged.
        r = run({"points": [[0, 0], [1, 2], [2, 4]], "queries": [0.5], "method": "linear"})
        assert r["columns"] == ["x", "y"] and r["rows"] == [[0.5, 1]], r

        # UI: method select, clamped slope inputs, keyboard run, table/graph export, 390 px.
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        assert page.locator("#interp-slopes").is_hidden()
        page.locator("#interp-method").select_option("clamped")
        assert page.locator("#interp-slope-start").is_visible()
        page.locator("#interp-samples").fill("0,0\n0.5,0.25\n1.25,1.5625\n2,4\n3,9")
        page.locator("#interp-queries").fill("1,2.5")
        page.locator("#interp-slope-start").fill("0")
        page.locator("#interp-slope-end").fill("6")
        page.locator("#interp-run").focus()
        page.keyboard.press("Enter")
        out = page.locator("#interp-output").inner_text()
        assert "Clamped cubic spline" in out and "integral from x0" in out, out
        assert "2.5 → 6.25 | 5 | 2 | 5.20833333333" in out, out
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#interp-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).name").startswith("Interpolation_Clamped")
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-method").select_option("periodic")
        assert page.locator("#interp-slopes").is_hidden()
        assert page.locator("#interp-to-table").is_disabled()
        page.locator("#interp-run").click()
        assert "first and last y values" in page.locator("#interp-output").inner_text()
        assert page.locator("#interp-to-graph").is_disabled()
        page.locator("#interp-method").select_option("akima")
        page.locator("#interp-run").click()
        assert "Akima" in page.locator("#interp-output").inner_text()
        page.locator("#interp-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert page.evaluate("MathStudio.graphData.getState().points.length") == 2
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-method").select_option("clamped")
        assert page.locator("#interp-slope-end").is_visible()
        width = page.evaluate("document.documentElement.scrollWidth")
        assert width <= 390 + 1, width
        assert not errors, errors
        browser.close()
    print("PASS: cubic spline/Akima references, derivatives, integrals, failures and responsive UI")


if __name__ == "__main__":
    main()
