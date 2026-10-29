"""Backward-time scalar Dormand-Prince RK45 reference, validation and browser handoff."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 860})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        # y'=y, y(1)=e -> y(0)=1, with accuracy refinement.
        loose = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'y',t0:1,t1:0,y0:Math.E,tolerance:1e-3})""")
        tight = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'y',t0:1,t1:0,y0:Math.E,tolerance:1e-10})""")
        loose_error = abs(loose["rows"][-1][1] - 1)
        tight_error = abs(tight["rows"][-1][1] - 1)
        assert tight_error < 1e-9, (loose_error, tight_error)
        assert tight_error < loose_error, (loose_error, tight_error)
        assert tight["steps"] > loose["steps"], (loose["steps"], tight["steps"])
        assert tight["rows"][0] == [1, math.e]
        assert tight["rows"][-1][0] == 0
        assert tight["attempts"] == tight["steps"] + tight["rejected"]
        assert all(a[0] > b[0] for a, b in zip(tight["rows"], tight["rows"][1:]))
        assert all(math.isfinite(row[1]) for row in tight["rows"])

        # Nonautonomous reference: y'=t, y(1)=1/2 -> y(0)=0.
        parabola = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'t',t0:1,t1:0,y0:0.5,tolerance:1e-9}).rows.at(-1)[1]""")
        assert abs(parabola) < 1e-10, parabola

        # Backward stable exponential with rapidly changing derivative
        # must reject some steps rather than silently bypass tolerance.
        fast = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'100*y',t0:1,t1:0,y0:1,tolerance:1e-9,maxSteps:3000})""")
        assert fast["rejected"] > 0, fast
        assert abs(fast["rows"][-1][1]) < 1e-7, fast

        for options in (
            {"t0": 1, "t1": 1},
            {"t0": 1, "t1": 0, "tolerance": 0},
            {"t0": 1, "t1": 0, "maxSteps": 3},
            {"t0": 1, "t1": 0, "maxSteps": 4, "tolerance": 1e-12},
            {"t0": 1, "t1": 0, "expression": "1/0"},
        ):
            assert page.evaluate("""opts => {
                try { MathStudio.odeTools.solveAdaptive(opts); return false; }
                catch(e) { return !!e.message; }
            }""", options), options

        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(element) => element.open = true")
        page.locator("#ode-method").select_option("rk45")
        page.locator("#ode-start").fill("1")
        page.locator("#ode-end").fill("0")
        page.locator("#ode-initial").fill(str(math.e))
        page.locator("#ode-tolerance").fill("0.0000000001")
        page.locator("#ode-run").click()
        assert "RK45" in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_enabled()
        page.locator("#ode-to-table").click()
        times = page.evaluate("""() => MathStudio.dataTables.tables.at(-1).rows.map(
            row => Number(row[0]))""")
        assert times[0] == 1 and times[-1] == 0
        assert all(a > b for a, b in zip(times, times[1:]))

        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(element) => element.open = true")
        page.locator("#ode-run").click()
        page.locator("#ode-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert page.evaluate("MathStudio.graphData.getState().points.length") > 2

        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(element) => element.open = true")
        page.locator("#ode-end").fill("1")
        assert page.locator("#ode-to-table").is_disabled()
        page.locator("#ode-run").click()
        assert "differ" in page.locator("#ode-output").inner_text().lower()
        assert page.locator("#ode-to-graph").is_disabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert not errors, errors
        browser.close()
    print("PASS: backward RK45 reference, refinement, rejection, invalid input, table/graph and mobile")


if __name__ == "__main__":
    main()
