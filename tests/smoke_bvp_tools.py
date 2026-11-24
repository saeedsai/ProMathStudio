"""Shooting BVP: analytic references, multiple/non-unique/no-solution cases, failures and UI."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

SHOOT = """o => { try { const r = MathStudio.bvp.shoot(o);
  return {status: r.status, parameter: r.parameter, rejected: r.rejected.length, columns: r.columns,
   sol: r.solutions.map(s => ({y0: s.y0, z0: s.slope0, res: s.residual, est: s.estimate,
    mid: s.rows[Math.floor(s.rows.length / 2)], end: s.rows.at(-1), n: s.rows.length}))};
 } catch (e) { return {error: e.message}; } }"""


def D(v):
    return {"type": "dirichlet", "value": v}


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 860})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        shoot = lambda **o: page.evaluate(SHOOT, o)

        # y''=-y, y(0)=0, y(pi/2)=1 -> sin x (slope 1).
        r = shoot(expression="-y", a=0, b=math.pi / 2, left=D(0), right=D(1), sMin=-5, sMax=5)
        assert r["status"] == "unique-in-scan" and r["parameter"] == "y′(a)", r
        s = r["sol"][0]
        assert abs(s["z0"] - 1) < 1e-8 and abs(s["mid"][1] - math.sin(s["mid"][0])) < 1e-8, s
        assert s["est"] and s["est"]["solutionDifference"] < 1e-8 and abs(s["res"]) < 1e-12, s
        assert r["columns"] == ["x", "y", "dy/dx"] and s["n"] == 201, r

        # y''=6x, y(0)=0, y(1)=1 -> x^3 (slope 0).
        r = shoot(expression="6*x", left=D(0), right=D(1), sMin=-5, sMax=5)
        assert len(r["sol"]) == 1 and abs(r["sol"][0]["z0"]) < 1e-10 and abs(r["sol"][0]["mid"][1] - 0.125) < 1e-10, r

        # y''=y with Neumann right y'(1)=cosh 1, and Robin left y+y'=1 -> sinh x.
        r = shoot(expression="y", left=D(0), right={"type": "neumann", "value": math.cosh(1)}, sMin=-5, sMax=5)
        assert len(r["sol"]) == 1 and abs(r["sol"][0]["z0"] - 1) < 1e-8, r
        assert abs(r["sol"][0]["mid"][1] - math.sinh(0.5)) < 1e-8, r
        r = shoot(expression="y", left={"type": "robin", "c0": 1, "c1": 1, "value": 1},
                  right=D(math.sinh(1)), sMin=-5, sMax=5)
        assert r["parameter"] == "y(a)" and len(r["sol"]) == 1, r
        assert abs(r["sol"][0]["y0"]) < 1e-8 and abs(r["sol"][0]["z0"] - 1) < 1e-8, r

        # y''=-y on [0,pi], y(0)=y(pi)=0: family A sin x -> reported as non-unique.
        r = shoot(expression="-y", a=0, b=math.pi, left=D(0), right=D(0), sMin=-5, sMax=5)
        assert r["status"] == "non-unique" and r["sol"] == [], r
        # y(pi)=1 instead: no solution.
        r = shoot(expression="-y", a=0, b=math.pi, left=D(0), right=D(1), sMin=-5, sMax=5)
        assert r["status"] == "none-found" and r["sol"] == [], r

        # Bratu y''+e^y=0, y(0)=y(1)=0: two solutions, y'(0) ~ 0.5493 and ~ 10.8469.
        for method in ("rk4", "tr-bdf2"):
            r = shoot(expression="-exp(y)", left=D(0), right=D(0), sMin=0, sMax=15, method=method)
            assert r["status"] == "multiple" and len(r["sol"]) == 2, (method, r)
            slopes = sorted(x["z0"] for x in r["sol"])
            assert abs(slopes[0] - 0.549353) < 1e-4 and abs(slopes[1] - 10.8469) < 2e-3, (method, slopes)
            assert all(abs(x["res"]) < 1e-9 and x["est"] for x in r["sol"]), r

        bad = [
            (dict(a=1, b=1), "greater than left"),
            (dict(a=2, b=1), "greater than left"),
            (dict(left={"type": "cauchy", "value": 0}), "boundary type"),
            (dict(right={"type": "robin", "c0": 0, "c1": 0, "value": 1}), "c₀ or c₁"),
            (dict(left={"type": "dirichlet", "value": ""}), "Left boundary value"),
            (dict(expression="2*+"), "every probe"),
            (dict(expression=""), "f(x, y, yp)"),
            (dict(sMin=1, sMax=1), "Scan maximum"),
            (dict(steps=2000), "RK4 steps"),
            (dict(method="euler"), "Integrator"),
        ]
        for options, word in bad:
            out = shoot(**{"expression": "-y", **options})
            assert "error" in out and word in out["error"], (options, out)

        # UI: panel follows the ODE panels in the Equation workspace.
        page.locator('[data-workspace="editor"]').click()
        page.locator("#workspace-task-select").select_option("ode")
        assert page.evaluate("document.getElementById('bvp-details').parentElement === document.getElementById('ode-details').parentElement")
        assert page.evaluate("document.getElementById('stiff-ode-details').nextElementSibling.id") == "bvp-details"
        panel = page.locator("#bvp-details")
        panel.locator("summary").focus()
        page.keyboard.press("Enter")
        assert panel.evaluate("(e) => e.open")
        out = page.locator("#bvp-output")
        assert out.get_attribute("role") == "status" and out.get_attribute("aria-live") == "polite"
        assert page.locator("#bvp-to-table").is_disabled()
        for sel in ("#bvp-f", "#bvp-a", "#bvp-b", "#bvp-left-type", "#bvp-left-value", "#bvp-right-type",
                    "#bvp-right-value", "#bvp-smin", "#bvp-smax", "#bvp-scan", "#bvp-steps", "#bvp-method"):
            assert page.evaluate("s => !!document.querySelector(s).closest('label')", sel), sel
        assert not page.locator("#bvp-left-c0").is_visible()
        page.locator("#bvp-run").focus()
        page.keyboard.press("Enter")
        text = out.inner_text()
        assert "2 solutions" in text and "not unique" in text and "step-doubling" in text, text
        assert "0.549352" in text and "10.8468" in text and not page.locator("#bvp-output.error").count(), text
        assert page.locator("#bvp-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#bvp-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 2
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).columns") == ["x", "y", "dy/dx"]

        # Robin fields appear; non-unique case through the UI; then error + recovery.
        page.locator('[data-workspace="editor"]').click()
        panel.evaluate("(e) => e.open = true")
        page.locator("#bvp-left-type").select_option("robin")
        assert page.locator("#bvp-left-c0").is_visible() and page.locator("#bvp-left-c1").is_visible()
        page.locator("#bvp-left-type").select_option("dirichlet")
        page.locator("#bvp-f").fill("-y")
        page.locator("#bvp-b").fill(str(math.pi))
        page.locator("#bvp-smin").fill("-5")
        page.locator("#bvp-smax").fill("5")
        page.locator("#bvp-run").click()
        assert "No unique solution" in out.inner_text() and page.locator("#bvp-to-table").is_disabled(), out.inner_text()
        page.locator("#bvp-right-value").fill("1")
        page.locator("#bvp-run").click()
        assert "No solution found" in out.inner_text(), out.inner_text()
        page.locator("#bvp-b").fill("-1")
        page.locator("#bvp-run").click()
        assert page.locator("#bvp-output.error").is_visible() and "Recovery" in out.inner_text()
        assert page.locator("#bvp-to-table").is_disabled()
        page.locator("#bvp-b").fill(str(math.pi / 2))
        page.locator("#bvp-run").click()
        assert not page.locator("#bvp-output.error").count() and "1 solution" in out.inner_text(), out.inner_text()
        assert page.locator("#bvp-to-table").is_enabled()

        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            assert page.locator("#bvp-run").is_visible(), width
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 0, (width, overflow)
            box = panel.bounding_box()
            assert box["x"] >= 0 and box["x"] + box["width"] <= width + 0.5, (width, box)
            for sel in ("#bvp-run", "#bvp-to-table", "#bvp-f", "#bvp-left-type", "#bvp-smax", "#bvp-method"):
                h = page.locator(sel).bounding_box()["height"]
                assert h >= 40, (sel, width, h)
        assert not errors, errors
        browser.close()
    print("PASS: shooting BVP references (sin, cubic, Neumann/Robin sinh, Bratu x2), non-unique, none, failures and UI")


if __name__ == "__main__":
    main()
