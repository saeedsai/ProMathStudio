"""Coupled two-state RK4 numerical reference, validation and UI/export regression."""
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

        # Harmonic oscillator y'=z, z'=-y, (y,z)(0)=(0,1).
        results = page.evaluate("""() => [20,80,320].map(steps =>
            MathStudio.odeTools.solveSystem({
                expression:'z',expressionZ:'-y',t0:0,t1:Math.PI/2,
                y0:0,z0:1,steps
            }))""")
        errors_rk = [abs(r["rows"][-1][1] - 1) + abs(r["rows"][-1][2]) for r in results]
        assert errors_rk[1] < errors_rk[0] / 100, errors_rk
        assert errors_rk[2] < errors_rk[1] / 100, errors_rk
        assert errors_rk[-1] < 1e-9, errors_rk
        assert results[0]["columns"] == ["t", "y", "z"]
        assert results[0]["rows"][0] == [0, 0, 1]
        assert len(results[0]["rows"]) == 21
        assert all(abs(y*y + z*z - 1) < 1e-6 for _,y,z in results[1]["rows"])

        # Both equations see t, y and z. y'=t, z'=y gives y(1)=1/2, z(1)=1/6.
        driven = page.evaluate("""() => MathStudio.odeTools.solveSystem({
            expression:'t',expressionZ:'y',t0:0,t1:1,y0:0,z0:0,steps:40
        }).rows.at(-1)""")
        assert abs(driven[1] - 0.5) < 1e-12, driven
        assert abs(driven[2] - 1/6) < 1e-12, driven

        invalid = [
            {"expression":""},
            {"expressionZ":""},
            {"expressionZ":"sqrt(-1)"},
            {"expression":"1/0"},
            {"t0":1,"t1":1},
            {"z0":""},
            {"steps":3},
            {"steps":1001},
            {"steps":2.5},
            {"y0":1e13},
        ]
        for options in invalid:
            assert page.evaluate("""opts => {
                try { MathStudio.odeTools.solveSystem(opts); return false; }
                catch(e) { return !!e.message; }
            }""", options), options

        page.locator('[data-workspace="editor"]').click()
        panel = page.locator("#ode-details")
        panel.evaluate("(element) => element.open = true")
        assert page.locator("#ode-system-derivative").is_hidden()
        page.locator("#ode-method").select_option("rk4-system")
        assert page.locator("#ode-system-derivative").is_visible()
        page.locator("#ode-expression").fill("z")
        page.locator("#ode-system-derivative").fill("-y")
        page.locator("#ode-initial").fill("0")
        page.locator("#ode-system-initial").fill("1")
        page.locator("#ode-end").fill(str(math.pi / 2))
        page.locator("#ode-steps").fill("80")
        page.locator("#ode-run").click()
        assert "Coupled" in page.locator("#ode-output").inner_text()
        assert "z ≈" in page.locator("#ode-output").inner_text()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#ode-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).columns") == ["t","y","z"]

        page.locator('[data-workspace="editor"]').click()
        panel.evaluate("(element) => element.open = true")
        page.locator("#ode-run").click()
        page.locator("#ode-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert page.evaluate("MathStudio.graphData.getState().points.length") == 81

        page.locator('[data-workspace="editor"]').click()
        panel.evaluate("(element) => element.open = true")
        page.locator("#ode-system-derivative").fill("sqrt(-1)")
        assert page.locator("#ode-to-table").is_disabled()
        page.locator("#ode-run").click()
        assert page.locator("#ode-output.error").is_visible()
        assert page.locator("#ode-to-graph").is_disabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#ode-run").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: two-state RK4 oscillator, convergence, coupling, invalid inputs and UI exports")


if __name__ == "__main__":
    main()
