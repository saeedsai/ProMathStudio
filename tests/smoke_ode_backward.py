"""Backward-time scalar RK4 numerical reference and browser regression."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":1280,"height":860})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"), wait_until="load")
        runs = page.evaluate("""() => [20,80,320].map(steps => MathStudio.odeTools.solve({
            expression:'y',t0:1,t1:0,y0:Math.E,steps
        }))""")
        residuals = [abs(r["rows"][-1][1]-1) for r in runs]
        assert residuals[1] < residuals[0]/100, residuals
        assert residuals[2] < residuals[1]/100, residuals
        assert residuals[-1] < 1e-10, residuals
        for run in runs:
            assert run["h"] < 0 and run["rows"][0][0] == 1 and run["rows"][-1][0] == 0
            assert all(a[0] > b[0] for a,b in zip(run["rows"],run["rows"][1:]))
        parabola = page.evaluate("""() => MathStudio.odeTools.solve({
            expression:'t',t0:1,t1:0,y0:0.5,steps:20
        }).rows.at(-1)[1]""")
        assert abs(parabola) < 1e-12, parabola
        for options in ({"t0":1,"t1":1},{"t0":1,"t1":0,"steps":3},{"t0":1,"t1":0,"expression":"1/0"}):
            assert page.evaluate("""opts => {
                try { MathStudio.odeTools.solve(opts); return false; }
                catch(e) { return !!e.message; }
            }""", options), options
        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(e) => e.open = true")
        page.locator("#ode-start").fill("1")
        page.locator("#ode-end").fill("0")
        page.locator("#ode-initial").fill(str(math.e))
        page.locator("#ode-steps").fill("80")
        page.locator("#ode-run").click()
        assert "Runge" in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_enabled()
        page.locator("#ode-to-table").click()
        times = page.evaluate("""() => MathStudio.dataTables.tables.at(-1).rows.map(row => Number(row[0]))""")
        assert times[0] == 1 and times[-1] == 0
        assert all(a > b for a,b in zip(times,times[1:]))
        page.set_viewport_size({"width":390,"height":844})
        assert not errors, errors
        browser.close()
    print("PASS: backward RK4 reference, invalid inputs, UI and table export")

if __name__ == "__main__":
    main()
