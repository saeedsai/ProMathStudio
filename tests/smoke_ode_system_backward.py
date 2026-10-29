"""Backward two-state RK4 numerical, input and UI/export regression."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv("CHROMIUM_PATH") or None,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":860})
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"),wait_until="load")
        runs=page.evaluate("""() => [20,80,320].map(steps=>MathStudio.odeTools.solveSystem({
            expression:'z',expressionZ:'-y',t0:Math.PI/2,t1:0,y0:1,z0:0,steps}))""")
        residuals=[abs(r["rows"][-1][1])+abs(r["rows"][-1][2]-1) for r in runs]
        assert residuals[1]<residuals[0]/100 and residuals[2]<residuals[1]/100,residuals
        assert residuals[-1]<1e-9,residuals
        for r in runs:
            assert r["h"]<0 and r["rows"][0][0]==math.pi/2 and r["rows"][-1][0]==0
            assert r["columns"]==["t","y","z"]
            assert all(a[0]>b[0] for a,b in zip(r["rows"],r["rows"][1:]))
        polynomial=page.evaluate("""() => MathStudio.odeTools.solveSystem({
            expression:'t',expressionZ:'y',t0:1,t1:0,y0:.5,z0:1/6,steps:80}).rows.at(-1)""")
        assert abs(polynomial[1])<1e-12 and abs(polynomial[2])<1e-12,polynomial
        forward=page.evaluate("""() => MathStudio.odeTools.solveSystem({
            expression:'z',expressionZ:'-y',t0:0,t1:Math.PI/2,y0:0,z0:1,steps:80}).rows.at(-1)""")
        assert abs(forward[1]-1)<1e-8,forward
        for opts in ({"t0":1,"t1":1},{"t0":1,"t1":0,"steps":3},
                     {"t0":1,"t1":0,"expressionZ":"sqrt(-1)"},
                     {"t0":1,"t1":0,"y0":1e13}):
            assert page.evaluate("""opts => {
                try { MathStudio.odeTools.solveSystem(opts); return false; }
                catch(e) { return !!e.message; }
            }""",opts),opts
        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(e)=>e.open=true")
        page.locator("#ode-method").select_option("rk4-system")
        page.locator("#ode-expression").fill("z")
        page.locator("#ode-system-derivative").fill("-y")
        page.locator("#ode-start").fill(str(math.pi/2))
        page.locator("#ode-end").fill("0")
        page.locator("#ode-initial").fill("1")
        page.locator("#ode-system-initial").fill("0")
        page.locator("#ode-steps").fill("80")
        page.locator("#ode-run").click()
        assert "Coupled" in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_enabled()
        page.locator("#ode-to-table").click()
        table=page.evaluate("() => MathStudio.dataTables.tables.at(-1)")
        assert table["columns"]==["t","y","z"]
        times=[float(row[0]) for row in table["rows"]]
        assert times[0]>times[-1] and times[-1]==0
        assert all(a>b for a,b in zip(times,times[1:]))
        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(e)=>e.open=true")
        page.locator("#ode-run").click()
        page.locator("#ode-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert page.evaluate("MathStudio.graphData.getState().points.length")==81
        page.set_viewport_size({"width":390,"height":844})
        assert not errors,errors
        browser.close()
    print("PASS: backward coupled RK4 numerical, invalid, UI and exports")
if __name__=="__main__":
    main()
