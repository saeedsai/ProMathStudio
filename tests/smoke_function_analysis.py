"""Inequality solving and function domain analysis: references, failures, UI at 390/1280, keyboard, export."""
from pathlib import Path
import math
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-7


def close(a, b, tol=TOL):
    return abs(a - b) <= tol * max(1, abs(b))


def check_intervals(got, expected):
    assert len(got) == len(expected), (got, expected)
    for g, (lo, hi, lc, hc) in zip(got, expected):
        assert close(g["lo"], lo) and close(g["hi"], hi), (g, lo, hi)
        assert g["loClosed"] is lc and g["hiClosed"] is hc, (g, lc, hc)


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/function-analysis.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium",
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        solve = lambda e, lo, hi, **k: page.evaluate("o=>MathStudio.functionAnalysis.solve(o)", {"expression": e, "lo": lo, "hi": hi, **k})
        analyze = lambda e, lo, hi, **k: page.evaluate("o=>MathStudio.functionAnalysis.analyze(o)", {"expression": e, "lo": lo, "hi": hi, **k})

        # Inequality references.
        r = solve("x^2-4 < 0", -5, 5)
        check_intervals(r["intervals"], [(-2, 2, False, False)])
        assert r["notation"] == "(-2, 2)", r["notation"]
        r = solve("x^2-4 <= 0", -5, 5)
        check_intervals(r["intervals"], [(-2, 2, True, True)])
        assert r["notation"] == "[-2, 2]"
        r = solve("x^2-4 ≥ 0", -5, 5)
        check_intervals(r["intervals"], [(-5, -2, True, True), (2, 5, True, True)])
        r = solve("1/(x-1) > 0", -5, 5)
        check_intervals(r["intervals"], [(1, 5, False, True)])
        assert any(close(p, 1, 1e-6) for p in r["poles"]) or 1 in r["excludedPoints"], r
        r = solve("sin(x) >= 0.5", 0, "2*pi")
        check_intervals(r["intervals"], [(math.pi / 6, 5 * math.pi / 6, True, True)])
        assert close(r["domain"][1], 2 * math.pi, 1e-12)
        r = solve("sin(x) > 0.5", 0, "2*pi")
        check_intervals(r["intervals"], [(math.pi / 6, 5 * math.pi / 6, False, False)])
        r = solve("x = x", -5, 5)
        check_intervals(r["intervals"], [(-5, 5, True, True)])
        r = solve("x^2+1<0", -5, 5)
        assert r["intervals"] == [] and r["notation"] == "∅", r
        r = solve("x^2 = 4", -5, 5)
        assert r["notation"] == "{-2} ∪ {2}", r["notation"]
        r = solve("x^2 <= 0", -2, 2)
        assert r["notation"] == "{0}", r["notation"]
        r = solve("sqrt(x) > 0", -3, 3)
        check_intervals(r["intervals"], [(0, 3, False, True)])
        r = solve("ln(x) < 0", -3, 3)
        check_intervals(r["intervals"], [(0, 1, False, False)])
        r = solve("tan(x) > 0", -2, 2)
        check_intervals(r["intervals"], [(-2, -math.pi / 2, True, False), (0, math.pi / 2, False, False)])
        r = solve("x^2 > 1/x", -3, 3)
        check_intervals(r["intervals"], [(-3, 0, True, False), (1, 3, False, True)])

        # Domain analysis references.
        a = analyze("sqrt(x)", -3, 3)
        check_intervals(a["domainIntervals"], [(0, 3, True, True)])
        assert a["domainNotation"] == "[0, 3]" and a["zeros"] == [0]
        assert not a["symmetry"]["even"] and not a["symmetry"]["odd"], a["symmetry"]
        a = analyze("ln(x)", -3, 3)
        check_intervals(a["domainIntervals"], [(0, 3, False, True)])
        assert a["domainNotation"] == "(0, 3]" and close(a["zeros"][0], 1)
        a = analyze("tan(x)", -2, 2)
        assert len(a["poles"]) == 2 and close(a["poles"][0], -math.pi / 2, 1e-8) and close(a["poles"][1], math.pi / 2, 1e-8), a["poles"]
        assert a["symmetry"]["odd"] and not a["symmetry"]["even"] and a["range"]["unboundedNearPoles"]
        assert [m["trend"] for m in a["monotonic"]] == ["increasing"] * 3
        a = analyze("x^3-3*x", -3, 3)
        ext = [(e["kind"], e["x"], e["value"]) for e in a["extrema"]]
        assert len(ext) == 2 and ext[0][0] == "maximum" and close(ext[0][1], -1, 1e-6) and close(ext[0][2], 2, 1e-9), ext
        assert ext[1][0] == "minimum" and close(ext[1][1], 1, 1e-6) and close(ext[1][2], -2, 1e-9), ext
        assert close(a["range"]["min"], -18) and close(a["range"]["max"], 18)
        assert [m["trend"] for m in a["monotonic"]] == ["increasing", "decreasing", "increasing"]
        assert a["symmetry"]["odd"] and not a["symmetry"]["even"]
        assert sorted(round(z, 6) for z in a["zeros"]) == [round(-math.sqrt(3), 6), 0, round(math.sqrt(3), 6)]
        a = analyze("cos(x)", -3, 3)
        assert a["symmetry"]["even"] and not a["symmetry"]["odd"]
        assert len(a["extrema"]) == 1 and a["extrema"][0]["kind"] == "maximum" and abs(a["extrema"][0]["x"]) < 1e-7
        a = analyze("sin(x)", -3, 3)
        assert a["symmetry"]["odd"] and not a["symmetry"]["even"]
        a = analyze("1/x^2", -2, 2)
        assert a["domainNotation"] == "[-2, 0) ∪ (0, 2]" and 0 in a["poles"], a
        a = analyze("x^2", 0, 3)
        assert not a["symmetry"]["applicable"]
        a = analyze("sqrt(2-x^2)", -3, 3)
        check_intervals(a["domainIntervals"], [(-math.sqrt(2), math.sqrt(2), True, True)])
        assert "Sampled estimate" in a["range"]["note"]

        # Invalid inputs give errors, not results.
        invalid = [{"expression": ""}, {"expression": "x<1<2"}, {"expression": "x==1"}, {"expression": "x != 1"},
                   {"expression": "< 1"}, {"expression": "x<0", "lo": 1, "hi": 1}, {"expression": "x<0", "lo": 2, "hi": 1},
                   {"expression": "x<0", "lo": "NaN", "hi": 1}, {"expression": "x<0", "lo": "", "hi": 1},
                   {"expression": "x<0", "lo": 0, "hi": "1e13"}, {"expression": "x<0", "samples": 5},
                   {"expression": "x<0", "samples": 2.5}, {"expression": "x<0", "tolerance": 0},
                   {"expression": "sqrt(-1-x^2) < 0"}, {"expression": "x^2"}]
        for o in invalid:
            msg = page.evaluate("o=>{try{MathStudio.functionAnalysis.solve(o);return null}catch(e){return e.message}}", o)
            assert msg, o
        assert page.evaluate("()=>{try{MathStudio.functionAnalysis.analyze({expression:'ln(-1-x^2)'});return null}catch(e){return e.message}}")

        # UI: open the panel, keyboard-run, shaded plot, export, error recovery.
        page.locator('[data-workspace="editor"]').click()
        page.locator("#function-analysis-details summary").focus()
        page.keyboard.press("Enter")
        assert page.locator("#function-analysis-details").evaluate("e=>e.open")
        page.locator("#fa-expression").fill("x^2-4 <= 0")
        page.locator("#fa-expression").press("Enter")
        out = page.locator("#fa-output").inner_text()
        assert "[-2, 2]" in out and "Real domain" in out and "not a symbolic proof" in out, out
        assert "[-2, 2]" in page.locator("#fa-canvas").get_attribute("aria-label")
        assert page.locator("#fa-canvas").get_attribute("role") == "img"
        assert page.locator("#fa-output").get_attribute("aria-live") == "polite"
        assert page.locator("#fa-to-table").is_enabled()
        page.locator("#fa-to-table").focus()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.keyboard.press("Enter")
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        assert page.evaluate("MathStudio.dataTables.active.columns.length") == 4
        page.locator('[data-workspace="editor"]').click()
        page.locator("#function-analysis-details").evaluate("e=>e.open=true")
        page.locator("#fa-expression").fill("tan(x)")
        page.locator("#fa-lo").fill("-2")
        page.locator("#fa-hi").fill("2")
        assert page.locator("#fa-to-table").is_disabled()
        page.locator("#fa-run").click()
        out = page.locator("#fa-output").inner_text()
        assert "1.570796327" in out and "odd" in out, out
        page.locator("#fa-hi").fill("-3")
        page.locator("#fa-run").click()
        assert page.locator("#fa-output").evaluate("e=>e.classList.contains('error')")
        assert "Upper bound" in page.locator("#fa-output").inner_text()
        assert page.locator("#fa-to-table").is_disabled()
        page.locator("#fa-hi").fill("2*pi")
        page.locator("#fa-expression").fill("sin(x) >= 0.5")
        page.locator("#fa-lo").fill("0")
        page.locator("#fa-run").click()
        assert not page.locator("#fa-output").evaluate("e=>e.classList.contains('error')")
        assert "[0.523598776, 2.617993877]" in page.locator("#fa-output").inner_text()

        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            for sel in ("#fa-run", "#fa-to-table", "#fa-expression", "#fa-lo", "#fa-hi", "#fa-samples"):
                box = page.locator(sel).bounding_box()
                assert box and box["height"] >= 40 and box["x"] >= 0 and box["x"] + box["width"] <= width + 1, (width, sel, box)
            cbox = page.locator("#fa-canvas").bounding_box()
            assert cbox["x"] + cbox["width"] <= width + 1, (width, cbox)
            assert page.evaluate("document.documentElement.scrollWidth") <= width + 1, width
        assert not errors, errors
        browser.close()
    print("PASS: inequality intervals, domain/poles/extrema/symmetry references, invalid inputs, UI 390/1280, keyboard, export")


if __name__ == "__main__":
    main()
