"""Root secant boundary, invalid real domain, and responsive UI regressions."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":390,"height":844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        def solve(expr,lo,hi):
            return page.evaluate("""([expr,lo,hi]) => window.MathStudio.numerical.scalarRoots(expr,'x',lo,hi,{samples:350,tolerance:1e-9})""",[expr,lo,hi])
        forward = solve("sqrt(x)",-1,1)
        i = min(range(len(forward["roots"])),key=lambda j:abs(forward["roots"][j]))
        assert abs(forward["roots"][i])<1e-10 and forward["localSlopeMethods"][i]=="forward", forward
        assert math.isfinite(forward["localSlopeMagnitudes"][i]) and forward["localSlopeMagnitudes"][i]>100, forward
        backward = solve("sqrt(-x)",-1,1)
        i = min(range(len(backward["roots"])),key=lambda j:abs(backward["roots"][j]))
        assert abs(backward["roots"][i])<1e-10 and backward["localSlopeMethods"][i]=="backward", backward
        assert backward["localSlopeMagnitudes"][i]>100, backward
        boundary = solve("x",0,1)
        assert boundary["roots"] and boundary["localSlopeMethods"][0]=="forward", boundary
        interior = solve("x-0.5",0,1)
        assert interior["roots"] and "central" in interior["localSlopeMethods"], interior
        assert len(interior["roots"])==len(interior["localSlopeMethods"]), interior
        plateau = solve("x-x",-1,1)
        assert plateau["localSlopeMethods"]==[], plateau
        jump = solve("0.00001*(x-0.12345)/sqrt((x-0.12345)^2)",-1,1)
        assert jump["roots"]==[], jump
        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el)=>el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("sqrt(x)")
        page.locator("#num-start").fill("-1")
        page.locator("#num-end").fill("1")
        page.locator("#num-run").click()
        out = page.locator("#num-output")
        assert "One-sided local slope estimates: 1" in out.inner_text()
        assert "not proof of differentiability" in out.inner_text()
        assert out.get_attribute("aria-live")=="polite"
        page.locator("#num-end").fill("-2")
        page.locator("#num-run").click()
        assert out.evaluate("(el)=>el.classList.contains('error')")
        page.locator("#num-end").fill("1")
        for width in (390,768,1280):
            page.set_viewport_size({"width":width,"height":844})
            page.locator("#num-run").click()
            assert "One-sided local slope estimates: 1" in out.inner_text()
            assert not out.evaluate("(el)=>el.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS one-sided scalar root sensitivity and responsive recovery")
if __name__=="__main__":
    main()
