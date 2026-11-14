"""Nonlinear least squares: references through the real evaluator, NIST Misra1a, warnings, UI recovery, keyboard, table source, export and responsive layout."""
from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MISRA_X = [77.6, 114.9, 141.1, 190.8, 239.9, 289.0, 332.8, 378.4, 434.8, 477.3, 536.8, 593.1, 689.1, 760.0]
MISRA_Y = [10.07, 14.73, 17.94, 23.93, 29.61, 35.18, 40.02, 44.82, 50.76, 55.05, 61.01, 66.40, 75.47, 81.78]


def has_error(locator):
    return "error" in (locator.get_attribute("class") or "")


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/nonlinear-fit.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")

        # API references through the shared MathStudio.numerical.evaluate parser.
        r = page.evaluate("""(D)=>{const N=MathStudio.nonlinearFit,P=(name,initial,lower,upper)=>({name,initial,lower,upper});
          const xs=[0,0.5,1,1.5,2,3,4,5,6,8];
          const ex=N.fit({expression:'a*exp(-b*x)+c',parameters:[P('a',1),P('b',1),P('c',0)],x:xs,y:xs.map(x=>2*Math.exp(-0.5*x)+1)});
          const t0=performance.now(),mi=N.fit({expression:'b1*(1-exp(-b2*x))',parameters:[P('b1',500),P('b2',1e-4)],x:D.mx,y:D.my}),ms=performance.now()-t0;
          const ni=N.fit({expression:'a*b*x',parameters:[P('a',1),P('b',1)],x:[1,2,3,4],y:[2,4.1,5.9,8]});
          const bd=N.fit({expression:'a*exp(-b*x)+c',parameters:[P('a',1),P('b',0.1,0,0.4),P('c',0)],x:xs,y:xs.map(x=>2*Math.exp(-0.5*x)+1)});
          const errs=[];for(const f of [()=>N.fit({expression:'a*exp(-b*x)+c',parameters:[P('a',1),P('b',1)],x:xs,y:xs}),
            ()=>N.fit({expression:'a*(x',parameters:[P('a',1)],x:xs,y:xs}),()=>N.fit({expression:'a+b*x',parameters:[P('a',1),P('b',1)],x:[1,2],y:[1,2]})]){try{f();errs.push(null)}catch(e){errs.push(e.message)}}
          return {ex:ex.parameters.map(p=>p.value),mi:mi.parameters.map(p=>[p.value,p.standardError]),miConv:mi.converged,ms,ni:ni.warnings,niId:ni.identifiable,bd:bd.parameters.map(p=>p.value),errs}}""",
                          {"mx": MISRA_X, "my": MISRA_Y})
        for got, want in zip(r["ex"], (2, 0.5, 1)):
            assert abs(got - want) < 1e-8, r
        assert r["miConv"] and r["ms"] < 5000, r
        for (v, se), bv, bse in zip(r["mi"], (2.3894212918e02, 5.5015643181e-04), (2.7070075241e00, 7.2668688436e-06)):
            assert abs(v - bv) <= 1e-6 * bv and abs(se - bse) <= 1e-6 * bse, r["mi"]
        assert not r["niId"] and any("not identifiable" in w for w in r["ni"]), r
        assert 0 <= r["bd"][1] <= 0.4, r
        assert all(r["errs"]) and "Initial guess is invalid" in r["errs"][0] and "Initial guess is invalid" in r["errs"][1] and "n > p" in r["errs"][2], r["errs"]

        # A Data Table with a formula column for the table-source path.
        page.evaluate("""()=>MathStudio.dataTables.importData({headers:['t','obs','w'],rows:[[0,'=1+2',1],[1,2.213061319425,1],[2,1.735758882343,2],[3,1.446260320297,1],[4,1.270670566473,3],[5,1.164169997248,1],['note','',''],[6,1.099574136736,1]]},'NLFitData')""")

        for width in (1280, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator('[data-workspace="graph"]').click()
            details = page.locator("#graph-panel #nlfit-details")
            assert details.count() == 1
            details.evaluate("e=>{e.open=false;e.scrollIntoView()}")
            page.locator("#nlfit-details > summary").focus()
            page.keyboard.press("Enter")
            assert details.evaluate("e=>e.open")
            out = page.locator("#nlfit-output")
            assert out.get_attribute("role") == "status" and out.get_attribute("aria-live") == "polite"
            page.locator("#nlfit-source").select_option("lists")
            page.locator("#nlfit-expression").fill("a*exp(-b*x)+c")
            page.locator("#nlfit-params").fill("a 1\nb 1\nc 0")
            page.locator("#nlfit-run").focus()
            page.keyboard.press("Enter")
            text = out.inner_text()
            assert not has_error(out) and "Converged" in text and "a = 2" in text and "b = 0.5" in text and "c = 1" in text, text
            canvas = page.locator("#nlfit-canvas")
            assert canvas.get_attribute("role") == "img" and "7 data points" in canvas.get_attribute("aria-label"), canvas.get_attribute("aria-label")
            assert page.locator("#nlfit-to-table").is_enabled()
            # Error and recovery: unknown parameter in the model.
            page.locator("#nlfit-params").fill("a 1\nb 1")
            assert page.locator("#nlfit-to-table").is_disabled()
            page.locator("#nlfit-run").click()
            assert has_error(out) and "Initial guess is invalid" in out.inner_text(), out.inner_text()
            assert "not computed" in canvas.get_attribute("aria-label")
            page.locator("#nlfit-params").fill("a 1 0 10\nb 1\nc 0")
            page.locator("#nlfit-run").click()
            assert not has_error(out) and "a = 2" in out.inner_text(), out.inner_text()
            # Non-identifiable warning through the UI.
            page.locator("#nlfit-expression").fill("a*b*x")
            page.locator("#nlfit-params").fill("a 1\nb 1")
            page.locator("#nlfit-run").click()
            assert "not identifiable" in out.inner_text() and not has_error(out), out.inner_text()
            # Table source with a formula cell and a non-numeric row.
            page.locator("#nlfit-source").select_option("table")
            assert page.locator("#nlfit-x").is_hidden() and page.locator("#nlfit-table").is_visible()
            tid = page.evaluate("MathStudio.dataTables.tables.find(t=>t.name.startsWith('NLFitData')).id")
            page.locator("#nlfit-table").select_option(tid)
            page.locator("#nlfit-x-col").select_option("0")
            page.locator("#nlfit-y-col").select_option("1")
            page.locator("#nlfit-w-col").select_option("2")
            page.locator("#nlfit-expression").fill("a*exp(-b*x)+c")
            page.locator("#nlfit-params").fill("a 1\nb 1\nc 0")
            page.locator("#nlfit-run").click()
            text = out.inner_text()
            assert not has_error(out) and "n = 7" in text and "(weighted)" in text and "1 non-numeric row(s) skipped" in text, text
            assert "a = 2" in text and "b = 0.5" in text, text
            sizes = page.evaluate("""()=>[...document.querySelectorAll('#nlfit-details summary,#nlfit-details button,#nlfit-details input,#nlfit-details select,#nlfit-details textarea')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height)""")
            assert sizes and min(sizes) >= 40, sizes
            overflow = page.evaluate("()=>{const d=document.getElementById('nlfit-details').getBoundingClientRect();return document.documentElement.scrollWidth>window.innerWidth+1||d.right>window.innerWidth+1}")
            assert not overflow, width
            before = page.evaluate("MathStudio.dataTables.tables.length")
            page.locator("#nlfit-to-table").click()
            assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
            saved = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert saved["name"].startswith("NLFit_Residuals") and saved["columns"] == ["x", "y", "fitted", "residual"] and len(saved["rows"]) == 7, saved
            page.locator("#nlfit-source").select_option("lists")
        assert not errors, errors
        browser.close()
    print("PASS: nonlinear least squares exact/Misra1a references, identifiability and bounds, validation, recovery, keyboard, table source, export and 390/1280 layout")


if __name__ == "__main__":
    main()
