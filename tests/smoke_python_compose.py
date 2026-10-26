"""Regression: composed Python custom functions remain worker-isolated and cancellable."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv("CHROMIUM_PATH") or None,args=["--no-sandbox"])
        page=browser.new_page()
        errors=[]
        page.on("pageerror",lambda exc: errors.append(str(exc)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"),wait_until="load")
        page.locator("#custom-function-panel").evaluate("(e)=>e.open=true")
        for name,source in [
            ("pyfun","def pyfun(x):\n    return x*x"),
            ("bad","def bad(x):\n    return float('nan')"),
            ("slow","def slow(x):\n    return x"),
        ]:
            page.locator("#cf-name").fill(name)
            page.locator("#cf-params").fill("x")
            page.locator("#cf-type").select_option("python")
            page.locator("#cf-body").fill(source)
            page.locator("#cf-save").click()
            assert any(f["name"]==name and f["type"]=="python" for f in page.evaluate("MathStudio.customFunctions.list()")),page.locator("#cf-message").inner_text()
        page.evaluate("""() => {
          window.__RealWorker=window.Worker;
          window.__pyCalls=[];window.__terminated=0;
          window.Worker=class {
            constructor(){this.dead=false;}
            postMessage(msg){
              window.__pyCalls.push({name:msg.name,args:msg.args});
              const reply=()=>{
                if(this.dead)return;
                const x=msg.args[0];
                const value=msg.name==='bad'?NaN:msg.name==='pyfun'?x*x:x;
                this.onmessage({data:{ok:true,value}});
              };
              setTimeout(reply,msg.name==='slow'?300:0);
            }
            terminate(){this.dead=true;window.__terminated++;}
          };
        }""")
        page.locator('[data-workspace="calculator"]').click()
        def check(expression,expected):
            page.locator("#calc-input").fill(expression)
            page.locator("#calc-execute").click()
            page.wait_for_function("expected => document.querySelector('#calc-result-plain').textContent === '= '+expected",str(expected))
        check("pyfun(3)",9)                 # existing direct-call compatibility
        check("2*pyfun(3)+1",19)           # composed arithmetic
        check("pyfun(pyfun(2)+1)",25)     # nested async calls
        check("pyfun(2)+pyfun(3)",13)     # sequential worker calls
        count=page.evaluate("__pyCalls.length")
        check("if(1,pyfun(3),pyfun(100))",9)
        assert page.evaluate("__pyCalls.length")==count+1,"Inactive branch must not execute Python"
        check("1+2",3)                    # formula-only path stays offline
        page.locator("#calc-input").fill("pyfun(1,2)")
        page.locator("#calc-execute").click()
        assert "requires 1 arguments" in page.locator("#calc-result-plain").inner_text()
        page.locator("#calc-input").fill("pyfun(i)")
        page.locator("#calc-execute").click()
        assert "real numbers" in page.locator("#calc-result-plain").inner_text()
        page.locator("#calc-input").fill("bad(2)")
        page.locator("#calc-execute").click()
        page.wait_for_function("document.querySelector('#calc-result-plain').textContent.includes('finite real number')")
        page.locator("#calc-input").fill("slow(8)")
        page.locator("#calc-execute").click()
        page.locator("#calc-input").fill("2+2")
        page.locator("#calc-execute").click()
        page.wait_for_timeout(400)
        assert page.locator("#calc-result-plain").inner_text()=="= 4","Stale worker must not overwrite newer result"
        assert page.evaluate("__terminated")>=1
        page.evaluate("window.Worker=window.__RealWorker")
        assert not errors,errors
        browser.close()
    print("PASS: Python custom functions in calculator AST, nested/lazy calls, errors and cancellation")

if __name__=="__main__":
    main()
