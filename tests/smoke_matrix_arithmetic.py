"""Playwright regression for bounded real A/B matrix arithmetic."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def close(a,b):
    return len(a)==len(b) and all(len(x)==len(y) and all(math.isclose(i,j,rel_tol=1e-12,abs_tol=1e-12) for i,j in zip(x,y)) for x,y in zip(a,b))
def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv("CHROMIUM_PATH") or None,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":850})
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"),wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        assert close(page.evaluate("MathStudio.matrixTools.add([[1,2],[3,4]],[[5,6],[7,8]])"),[[6,8],[10,12]])
        assert close(page.evaluate("MathStudio.matrixTools.subtract([[1,2],[3,4]],[[5,6],[7,8]])"),[[-4,-4],[-4,-4]])
        assert close(page.evaluate("MathStudio.matrixTools.multiply([[1,2],[3,4]],[[5,6],[7,8]])"),[[19,22],[43,50]])
        assert close(page.evaluate("MathStudio.matrixTools.multiply([[5,6],[7,8]],[[1,2],[3,4]])"),[[23,34],[31,46]])
        assert close(page.evaluate("MathStudio.matrixTools.multiply([[1,2,3],[4,5,6]],[[7,8],[9,10],[11,12]])"),[[58,64],[139,154]])
        assert close(page.evaluate("MathStudio.matrixTools.multiply([[1,2],[3,4],[5,6]],[[1,0,2],[0,1,3]])"),[[1,2,8],[3,4,18],[5,6,28]])
        cases=[
            ("add",[[1,2,3],[4,5,6]],"same matrix dimensions"),
            ("subtract",[[1,2,3],[4,5,6]],"same matrix dimensions"),
            ("multiply",[[1,2],[3,4],[5,6]],"columns"),
            ("add",[[1,float("nan")],[3,4]],"finite"),
            ("multiply",[[1,float("inf")],[3,4]],"finite"),
            ("add",[[1,""],[3,4]],"Enter a number"),
        ]
        for op,b,expected in cases:
            # JSON cannot encode nonfinite floats; select fixed invalid fixtures in the browser.
            kind=0 if len(b[0])==3 else 1 if len(b)==3 else 2 if isinstance(b[0][1],float) and math.isnan(b[0][1]) else 3 if isinstance(b[0][1],float) and math.isinf(b[0][1]) else 4
            message=page.evaluate("""([op,kind])=>{
                const A=[[1,2],[3,4]];
                const B=kind===0?[[1,2,3],[4,5,6]]:kind===1?[[1,2],[3,4],[5,6]]:
                    kind===2?[[1,NaN],[3,4]]:kind===3?[[1,Infinity],[3,4]]:[[1,''],[3,4]];
                try{MathStudio.matrixTools[op](A,B);return '';}catch(e){return e.message;}
            }""",[op,kind])
            assert expected in message,(op,kind,message)
        for i,v in enumerate(["1","2","3","4"]):
            page.locator("#mat-grid input").nth(i).fill(v)
        for i,v in enumerate(["5","6","7","8"]):
            page.locator("#mat-b-grid input").nth(i).fill(v)
        page.locator("#mat-multiply").click()
        assert "19" in page.locator("#mat-result").inner_text()
        assert "50" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-add").click()
        assert "12" in page.locator("#mat-result").inner_text()
        page.locator("#mat-subtract").click()
        assert "-4" in page.locator("#mat-result").inner_text()
        page.locator("#mat-send").click()
        assert "matrix(" in page.locator("#equation-input").input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        page.locator("#mat-b-cols").select_option("3")
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-add").click()
        assert "same matrix dimensions" in page.locator("#mat-result").inner_text()
        page.locator("#mat-multiply").click()
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-b-rows").select_option("3")
        page.locator("#mat-multiply").click()
        assert "columns" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-cols").select_option("3")
        page.locator("#mat-multiply").click()
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-b-grid input").first.fill("9")
        assert page.locator("#mat-send").is_disabled()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#mat-b-grid input").count()==9
        assert page.locator("#mat-multiply").is_visible()
        assert not errors,errors
        browser.close()
    print("PASS: matrix arithmetic, dimensions, invalid inputs, editor routing and responsive UI")
if __name__=="__main__":
    main()
