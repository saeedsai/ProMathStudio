"""QR-based 3x2 least squares numerical, validation, browser and editor regression."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv("CHROMIUM_PATH") or None,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":850})
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"),wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(el)=>el.open=true")
        A=[[1,0],[0,1],[1,1]]
        for rhs,expected,norm in (([2,-1,1],[2,-1],0),([1,2,4],[4/3,7/3],math.sqrt(1/3))):
            original=[row[:] for row in A]
            result=page.evaluate("({A,b})=>MathStudio.matrixTools.leastSquares(A,b)",{"A":A,"b":rhs})
            assert A==original and result["rank"]==2 and result["normalResidual"]<1e-8
            assert all(math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-9) for x,y in zip(result["solution"],expected))
            assert math.isclose(result["residual"],norm,rel_tol=1e-9,abs_tol=1e-9)
        scaled=page.evaluate("()=>MathStudio.matrixTools.leastSquares([[1e12,0],[0,1],[0,0.5]],[1e12,1,0.5])")
        assert all(math.isclose(x,1,rel_tol=1e-9,abs_tol=1e-9) for x in scaled["solution"])
        for matrix,rhs,phrase in (
            ([[1,0],[0,1]],[1,2],"tall"),
            ([[1,0,0],[0,1,0]],[1,2],"tall"),
            ([[1,2],[2,4],[3,6]],[1,2,3],"Rank-deficient"),
            ([[1,1],[1,1+1e-14],[1,1-1e-14]],[1,2,3],"rank-deficient"),
            ([[1,0],[0,1],[1,1]],[1,2],"3 values"),
            ([[1,0],[0,1],[1,1]],[1,"",3],"Enter a number"),
            ([[1,0],[0,1],[1,1]],[1,True,3],"Enter a number"),
            ([[1,0],[0,1],[1,1]],[1,1e15,3],"finite numbers"),
        ):
            msg=page.evaluate("({A,b})=>{try{MathStudio.matrixTools.leastSquares(A,b);return ''}catch(e){return e.message}}",{"A":matrix,"b":rhs})
            assert phrase in msg,(matrix,rhs,msg)
        page.locator("#mat-rows").select_option("3")
        for i,value in enumerate(["1","0","0","1","1","1"]):page.locator("#mat-grid input").nth(i).fill(value)
        for i,value in enumerate(["1","2","4"]):page.locator("#mat-rhs-grid input").nth(i).fill(value)
        page.locator("#mat-least-squares").click()
        output=page.locator("#mat-result").inner_text()
        assert "leastSquares:" in output and "Residual norm:" in output and "orthogonality" in output,output
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-send").click()
        editor=page.locator("#equation-input").input_value()
        assert "matrix([1.33333333333],[2.33333333333])" in editor,editor
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(el)=>el.open=true")
        page.locator("#mat-rhs-grid input").first.fill("")
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-least-squares").click()
        assert "Enter a number" in page.locator("#mat-result").inner_text()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#mat-least-squares").is_visible()
        assert not errors,errors
        browser.close()
    print("PASS: QR least squares reference, orthogonality, invalid inputs, UI and editor")

if __name__=="__main__":
    main()
