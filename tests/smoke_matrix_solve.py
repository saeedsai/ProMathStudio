"""Regression for bounded real Ax=b: pivots, residuals, errors and UI."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def close(a, b):
    return len(a) == len(b) and all(math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-9) for x, y in zip(a, b))

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":1280,"height":850})
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        for A,b,want in [
            ([[1,2],[3,4]],[5,11],[1,2]),
            ([[0,2,1],[1,1,1],[2,1,0]],[7,6,4],[1,2,3]),
            ([[1e12,0],[0,1]],[1e12,2],[1,2]),
            ([[0,1],[1,0]],[4,7],[7,4]),
            ([[1e-8,0],[0,2e-8]],[3e-8,8e-8],[3,4]),
        ]:
            result = page.evaluate("([A,b])=>MathStudio.matrixTools.solve(A,b)", [A,b])
            assert close(result["solution"],want),(A,b,result)
            assert result["residual"] <= 1e-8, result
        for A,b,expected in [
            ([[1,1],[2,2]],[2,5],"Inconsistent"),
            ([[1,1],[2,2]],[2,4],"Singular"),
            ([[1,1],[1,1+1e-14]],[2,2+1e-14],"Singular"),
            ([[1,2,3],[4,5,6]],[1,2],"square"),
            ([[1,2],[3,4]],[1],"2 values"),
            ([[1,2],[3,4]],["",1],"Enter a number"),
        ]:
            message = page.evaluate("([A,b])=>{try{MathStudio.matrixTools.solve(A,b);return '';}catch(e){return e.message;}}", [A,b])
            assert expected in message,(A,b,message)
        message = page.evaluate("()=>{try{MathStudio.matrixTools.solve([[1,2],[3,4]],[Infinity,1]);return '';}catch(e){return e.message;}}")
        assert "finite" in message
        for i,value in enumerate(["1","2","3","4"]):
            page.locator("#mat-grid input").nth(i).fill(value)
        for i,value in enumerate(["5","11"]):
            page.locator("#mat-rhs-grid input").nth(i).fill(value)
        page.locator("#mat-solve").click()
        output = page.locator("#mat-result").inner_text()
        assert "solve:" in output and "Relative residual:" in output,output
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-send").click()
        assert "matrix([1],[2])" in page.locator("#equation-input").input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        page.locator("#mat-rhs-grid input").first.fill("7")
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-rows").select_option("3")
        page.locator("#mat-cols").select_option("3")
        assert page.locator("#mat-rhs-grid input").count() == 3
        page.locator("#mat-rhs-grid input").last.fill("")
        page.locator("#mat-solve").click()
        assert "Enter a number" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#mat-solve").is_visible()
        assert not errors,errors
        browser.close()
    print("PASS: Ax=b numeric references, pivots, errors, UI, editor, mobile")

if __name__ == "__main__":
    main()
