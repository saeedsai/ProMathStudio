"""Brent-Dekker reference, endpoint, failure and browser integration checks."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    html=(ROOT/"index.html").read_text(encoding="utf-8")
    assert (ROOT/"src/brent-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium",args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":850})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.set_content(html,wait_until="load")
        run=lambda o:page.evaluate("o=>MathStudio.brentTools.refine(o)",o)
        cubic=run({"expression":"x^3-x-2","lo":1,"hi":2})
        assert abs(cubic["x"]-1.5213797068045676)<1e-8 and abs(cubic["residual"])<1e-7,cubic
        trig=run({"expression":"cos(x)-x","lo":0,"hi":1})
        assert abs(trig["x"]-.7390851332151607)<1e-8,trig
        assert run({"expression":"x-1","lo":1,"hi":3})["iterations"]==0
        assert run({"expression":"x-3","lo":1,"hi":3})["x"]==3
        invalid=[{"expression":""},{"expression":"x","lo":1,"hi":1},
                 {"expression":"x^2+1","lo":-2,"hi":2},
                 {"expression":"1/(x-1)","lo":0,"hi":2},
                 {"expression":"x","lo":"NaN","hi":2},
                 {"expression":"x","lo":0,"hi":2,"tolerance":0},
                 {"expression":"x","lo":0,"hi":2,"maxIterations":2},
                 {"expression":"x^7-0.1","lo":0,"hi":1,"maxIterations":8,"tolerance":1e-12}]
        for o in invalid:
            assert page.evaluate("o=>{try{MathStudio.brentTools.refine(o);return false}catch(e){return !!e.message}}",o),o
        page.locator('[data-workspace="solver"]').click()
        page.locator("#brent-details").evaluate("(e)=>e.open=true")
        page.locator("#brent-run").click()
        assert "Brent-Dekker" in page.locator("#brent-output").inner_text()
        assert page.locator("#brent-to-table").is_enabled()
        before=page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#brent-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length")==before+1
        page.locator('[data-workspace="solver"]').click()
        page.locator("#brent-details").evaluate("(e)=>e.open=true")
        page.locator("#brent-hi").fill("1")
        assert page.locator("#brent-to-table").is_disabled()
        page.locator("#brent-run").click()
        assert "Upper bound" in page.locator("#brent-output").inner_text()
        assert page.locator("#brent-to-table").is_disabled()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#brent-run").is_visible()
        assert not errors,errors
        browser.close()
    print("PASS: Brent-Dekker references, endpoints, discontinuity, budget, UI and export")
if __name__=="__main__":main()
