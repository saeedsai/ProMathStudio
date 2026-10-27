"""Adaptive Dormand-Prince RK45: reference accuracy, error limits and UI exports."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 860})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        # y'=y, y(0)=1 -> e, with decreasing tolerance.
        loose = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'y',t0:0,t1:1,y0:1,tolerance:1e-3})""")
        tight = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'y',t0:0,t1:1,y0:1,tolerance:1e-10})""")
        assert abs(tight["rows"][-1][1] - math.e) < 1e-9, tight
        assert abs(tight["rows"][-1][1] - math.e) < abs(loose["rows"][-1][1] - math.e), (loose, tight)
        assert tight["steps"] > loose["steps"], (loose["steps"], tight["steps"])
        assert tight["rows"][0] == [0, 1]
        assert tight["rows"][-1][0] == 1
        assert tight["attempts"] == tight["steps"] + tight["rejected"]
        assert tight["columns"] == ["t", "y"]
        assert all(a[0] < b[0] for a, b in zip(tight["rows"], tight["rows"][1:]))

        # Non-autonomous y'=t -> y(1)=1/2, and a rapidly varying equation
        # should produce rejected steps rather than silently ignore tolerance.
        parabola = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'t',t0:0,t1:1,y0:0,tolerance:1e-9}).rows.at(-1)[1]""")
        assert abs(parabola - 0.5) < 1e-9, parabola
        stiffish = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'-100*y',t0:0,t1:1,y0:1,tolerance:1e-9,maxSteps:2000})""")
        assert stiffish["rejected"] > 0, stiffish
        assert abs(stiffish["rows"][-1][1]) < 1e-7, stiffish

        invalid = [
            {"t0": 1, "t1": 1},
            {"t0": 1, "t1": 0},
            {"tolerance": 0},
            {"tolerance": 1e-13},
            {"tolerance": 0.1},
            {"maxSteps": 3},
            {"maxSteps": 10001},
            {"maxSteps": 2.5},
            {"tolerance": 1e-12, "maxSteps": 4},
            {"expression": "sqrt(-1)"},
            {"expression": "1/0"},
            {"expression": ""},
        ]
        for options in invalid:
            assert page.evaluate("""opts => {
                try { MathStudio.odeTools.solveAdaptive(opts); return false; }
                catch(e) { return !!e.message; }
            }""", options), options

        # UI: RK45 selection, error diagnostics, Data Tables and Graphs handoffs.
        page.locator('[data-workspace="solver"]').click()
        panel = page.locator("#ode-details")
        panel.evaluate("(element) => element.open = true")
        page.locator("#ode-method").select_option("rk45")
        page.locator("#ode-tolerance").fill("0.000000001")
        page.locator("#ode-run").click()
        output = page.locator("#ode-output").inner_text()
        assert "RK45" in output and "rejected" in output and "tolerance" in output, output
        assert page.locator("#ode-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#ode-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1

        page.locator('[data-workspace="solver"]').click()
        panel.evaluate("(element) => element.open = true")
        page.locator("#ode-run").click()
        page.locator("#ode-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert page.evaluate("MathStudio.graphData.getState().points.length") > 2

        page.locator('[data-workspace="solver"]').click()
        panel.evaluate("(element) => element.open = true")
        page.locator("#ode-tolerance").fill("0")
        assert page.locator("#ode-to-table").is_disabled()
        page.locator("#ode-run").click()
        assert "tolerance" in page.locator("#ode-output").inner_text().lower()
        assert page.locator("#ode-to-graph").is_disabled()
        assert not errors, errors
        browser.close()
    print("PASS: RK45 references, refinement, rejection, limits, UI and exports")


if __name__ == "__main__":
    main()
