"""Offline RK4 IVP regression: reference accuracy, failure paths and UI handoffs."""
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

        # y'=y, y(0)=1, y(1)=e. Classical RK4 is fourth-order.
        values = page.evaluate("""() => [4, 8, 32, 100].map(steps =>
          MathStudio.odeTools.solve({expression:'y',t0:0,t1:1,y0:1,steps})
        )""")
        exact = math.e
        errors_rk = [abs(result["rows"][-1][1] - exact) for result in values]
        assert errors_rk[1] < errors_rk[0] / 10, errors_rk
        assert errors_rk[2] < errors_rk[1] / 100, errors_rk
        assert errors_rk[-1] < 1e-9, errors_rk
        assert values[0]["columns"] == ["t", "y"]
        assert len(values[0]["rows"]) == 5
        assert values[0]["rows"][0] == [0, 1]
        assert values[0]["rows"][-1][0] == 1

        # Non-autonomous RHS y'=t, y(0)=0 -> y(1)=1/2.
        parabola = page.evaluate("""() => MathStudio.odeTools.solve(
          {expression:'t',t0:0,t1:1,y0:0,steps:20}).rows.at(-1)[1]""")
        assert abs(parabola - 0.5) < 1e-12, parabola

        # Reject invalid intervals, invalid work limits and singular/non-real values.
        invalid = [
            {"expression": "y", "t0": 1, "t1": 1, "y0": 1, "steps": 20},
            {"expression": "y", "t0": 1, "t1": 0, "y0": 1, "steps": 20},
            {"expression": "y", "t0": 0, "t1": 1, "y0": 1, "steps": 3},
            {"expression": "y", "t0": 0, "t1": 1, "y0": 1, "steps": 1001},
            {"expression": "y", "t0": 0, "t1": 1, "y0": 1, "steps": 2.5},
            {"expression": "y", "t0": 0, "t1": 1, "y0": "", "steps": 20},
            {"expression": "sqrt(-1)", "t0": 0, "t1": 1, "y0": 1, "steps": 20},
            {"expression": "1/0", "t0": 0, "t1": 1, "y0": 1, "steps": 20},
            {"expression": "", "t0": 0, "t1": 1, "y0": 1, "steps": 20},
        ]
        for options in invalid:
            assert page.evaluate("""opts => {
              try { MathStudio.odeTools.solve(opts); return false; }
              catch(e) { return !!e.message; }
            }""", options), options

        # Real UI: solve, import table, and route a second solve to a 2D graph.
        page.locator('[data-workspace="solver"]').click()
        panel = page.locator("#ode-details")
        panel.evaluate("(element) => element.open = true")
        assert panel.is_visible()
        page.locator("#ode-steps").fill("20")
        page.locator("#ode-run").click()
        assert "Runge" in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_enabled()
        assert page.locator("#ode-to-graph").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#ode-to-table").click()
        assert page.locator("#data-panel").is_visible()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        assert page.locator("#dt-sheet tbody tr").count() == 21

        page.locator('[data-workspace="solver"]').click()
        panel.evaluate("(element) => element.open = true")
        page.locator("#ode-run").click()
        page.locator("#ode-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert "Plotted" in page.locator("#dt-chart-status").inner_text()
        assert page.evaluate("MathStudio.graphData.getState().points.length") == 21

        page.locator('[data-workspace="solver"]').click()
        panel.evaluate("(element) => element.open = true")
        page.locator("#ode-end").fill("0")
        assert page.locator("#ode-to-table").is_disabled()
        page.locator("#ode-run").click()
        assert "greater" in page.locator("#ode-output").inner_text().lower()
        assert page.locator("#ode-to-graph").is_disabled()

        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#ode-run").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: RK4 reference accuracy/refinement, invalid conditions, table and graph handoff")


if __name__ == "__main__":
    main()
