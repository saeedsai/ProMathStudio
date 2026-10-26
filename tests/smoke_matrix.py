"""Matrix calculator regression: numerical reference cases, UI and editor routing."""
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
        page.on("pageerror",lambda exc: errors.append(str(exc)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"),wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        panel=page.locator("#matrix-tools")
        panel.evaluate("(e)=>e.open=true")
        assert panel.is_visible()
        # Pure math functions: 2×2 and 3×3, pivoting, singular and non-square.
        assert page.evaluate("MathStudio.matrixTools.determinant([[1,2],[3,4]])")==-2
        assert page.evaluate("MathStudio.matrixTools.determinant([[0,1],[1,0]])")==-1
        assert page.evaluate("MathStudio.matrixTools.determinant([[1,0,0],[0,1,0],[0,0,1]])")==1
        assert page.evaluate("MathStudio.matrixTools.determinant([[1,2,3],[0,1,4],[5,6,0]])")==1
        assert page.evaluate("MathStudio.matrixTools.determinant([[0,0],[0,0]])")==0
        assert page.evaluate("MathStudio.matrixTools.transpose([[1,2,3],[4,5,6]])")==[[1,4],[2,5],[3,6]]
        assert page.evaluate("MathStudio.matrixTools.inverse([[1,2],[3,4]])")==[[-2,1],[1.5,-0.5]]
        assert page.evaluate("MathStudio.matrixTools.inverse([[1,0,0],[0,1,0],[0,0,1]])")==[[1,0,0],[0,1,0],[0,0,1]]
        assert page.evaluate("MathStudio.matrixTools.inverse([[0,1],[1,0]])")==[[0,1],[1,0]]
        assert page.evaluate("MathStudio.matrixTools.notation([[1,2],[3,4]])")=="matrix([1,2],[3,4])"
        for expression in [
            "()=>MathStudio.matrixTools.inverse([[1,2],[2,4]])",
            "()=>MathStudio.matrixTools.inverse([[1,2,3],[4,5,6]])",
            "()=>MathStudio.matrixTools.determinant([[1,2,3],[4,5,6]])",
            "()=>MathStudio.matrixTools.validate([[1,''],[2,3]])",
            "()=>MathStudio.matrixTools.validate([[1,NaN],[2,3]])",
            "()=>MathStudio.matrixTools.validate([[1,1e20],[2,3]])",
        ]:
            assert page.evaluate("(src)=>{try{new Function('return ('+src+')')()();return false}catch(e){return !!e.message}}",expression),expression
        # Interactive determinant and inverse using editable cells.
        entries=page.locator("#mat-grid input")
        assert entries.count()==4
        for index,value in enumerate(["1","2","3","4"]):
            entries.nth(index).fill(value)
        page.locator("#mat-det").click()
        assert "-2" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-inverse").click()
        assert "-2" in page.locator("#mat-result").inner_text()
        page.locator("#mat-send").click()
        assert page.locator('[data-workspace="editor"]').get_attribute("class").find("active")!=-1
        assert "matrix(" in page.locator("#equation-input").input_value()
        assert page.locator("#preview math").count()>0
        # Input edits invalidate stale results, and non-square transpose still works.
        page.locator('[data-workspace="calculator"]').click()
        panel.evaluate("(e)=>e.open=true")
        page.locator("#mat-cols").select_option("3")
        assert page.locator("#mat-grid input").count()==6
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-det").click()
        assert "square" in page.locator("#mat-result").inner_text().lower()
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-transpose").click()
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-rows").select_option("3")
        assert page.locator("#mat-grid input").count()==9
        # Narrow browser viewport should still provide accessible controls.
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#mat-grid input").count()==9
        assert page.locator("#mat-inverse").is_visible()
        assert not errors,errors
        browser.close()
    print("PASS: matrix determinants/inverses/transpose, singular/invalid input, UI and editor transfer")

if __name__=="__main__":
    main()
