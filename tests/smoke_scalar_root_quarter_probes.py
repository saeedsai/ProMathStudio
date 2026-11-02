"""Quarter-grid recovery, jump rejection, zero plateau and responsive browser regression."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":390,"height":844})
        errors=[]
        page.on("pageerror",lambda e: errors.append(str(e)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"),wait_until="load")
        def solve(expr):
            return page.evaluate("""expr => window.MathStudio.numerical.scalarRoots(
                expr,'x',0,1,{samples:20,tolerance:1e-10})""",expr)
        paired=solve("(x-0.205)*(x-0.218)")
        assert paired["midpointProbes"]==20 and paired["quarterProbes"]==40,paired
        assert paired["quarterSignReversals"]>=2,paired
        for target in (0.205,0.218):
            assert any(abs(x-target)<1e-5 for x in paired["roots"]),paired
        assert all(math.isfinite(r) and r<=1e-10 for r in paired["residuals"]),paired
        assert "not globally complete" in paired["note"],paired
        jump=solve("((x-0.205)*(x-0.218))/sqrt(((x-0.205)*(x-0.218))^2)")
        assert jump["quarterProbes"]==40 and jump["quarterSignReversals"]>=2,jump
        assert jump["roots"]==[] and jump["maxResidual"] is None,jump
        plateau=solve("x-x")
        assert plateau["rootStatus"]=="sampled-zero-plateau" and plateau["roots"]==[],plateau
        assert plateau["quarterProbes"]==40,plateau
        assert any(abs(x-0.123456789)<1e-5 for x in solve("x-0.123456789")["roots"])
        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(e)=>e.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("(x-0.205)*(x-0.218)")
        for key,value in (("start","0"),("end","1"),("samples","20"),("tolerance","1e-10")):
            page.locator("#num-"+key).fill(value)
        output=page.locator("#num-output")
        for width in (390,768,1280):
            page.set_viewport_size({"width":width,"height":844})
            page.locator("#num-run").focus()
            page.keyboard.press("Enter")
            displayed=output.inner_text()
            assert "Quarter-grid probes: 40; sign-changing subintervals:" in displayed,displayed
            shown=[float(v.strip()) for v in displayed.splitlines()[0].split(":",1)[1].split(",")]
            for target in (0.205,0.218):
                assert any(abs(x-target)<1e-5 for x in shown),(target,shown)
            assert not output.evaluate("(e)=>e.classList.contains('error')"),displayed
            assert not page.evaluate("document.documentElement.scrollWidth>innerWidth+1"),width
        page.locator("#num-samples").fill("1601")
        page.locator("#num-run").click()
        assert output.evaluate("(e)=>e.classList.contains('error')")
        assert page.evaluate("document.activeElement.id")=="num-samples"
        page.locator("#num-samples").fill("20")
        page.locator("#num-run").click()
        assert not output.evaluate("(e)=>e.classList.contains('error')")
        assert not errors,errors
        browser.close()
    print("PASS quarter-grid roots, jumps, plateau and responsive recovery")

if __name__=="__main__":
    main()
