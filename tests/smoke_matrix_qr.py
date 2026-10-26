"""Thin QR reference, invalid, editor and responsive browser regression."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def check(A, result):
    m,n=len(A),len(A[0])
    Q,R=result["Q"],result["R"]
    assert len(Q)==m and all(len(row)==n for row in Q)
    assert len(R)==n and all(len(row)==n for row in R)
    assert result["residual"]<1e-8 and result["orthogonality"]<1e-8
    for i in range(n):
        for j in range(n):
            if j<i: assert abs(R[i][j])<1e-12
            dot=sum(Q[k][i]*Q[k][j] for k in range(m))
            assert math.isclose(dot,float(i==j),abs_tol=1e-8)
    for i in range(m):
        for j in range(n):
            actual=sum(Q[i][k]*R[k][j] for k in range(n))
            assert math.isclose(actual,A[i][j],rel_tol=1e-8,abs_tol=1e-8),(A,i,j,actual)

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv("CHROMIUM_PATH") or None,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":850})
        errors=[]
        page.on("pageerror",lambda exc:errors.append(str(exc)))
        page.set_content((ROOT/"index.html").read_text(encoding="utf-8"),wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        for A in (
            [[1,2],[3,4]],[[0,1],[1,0]],[[1,0],[0,1],[1,1]],
            [[1,2],[3,4],[5,7]],[[1e12,0],[0,1]],[[1e-8,0],[0,2e-8]],
            [[1,2,3],[4,5,6],[7,8,10]],
        ):
            original=[row[:] for row in A]
            check(A,page.evaluate("(A)=>MathStudio.matrixTools.qr(A)",A))
            assert A==original
        for A,phrase in (
            ([[1,2,3],[4,5,6]],"rows"),
            ([[1,2],[2,4]],"Rank-deficient"),
            ([[1,1],[1,1+1e-14]],"rank-deficient"),
            ([[0,0],[0,0]],"Rank-deficient"),
        ):
            message=page.evaluate("(A)=>{try{MathStudio.matrixTools.qr(A);return ''}catch(e){return e.message}}",A)
            assert phrase in message,(A,message)
        invalid=page.evaluate("()=>{try{MathStudio.matrixTools.qr([[1,Infinity],[2,3]]);return ''}catch(e){return e.message}}")
        assert "finite" in invalid
        for i,value in enumerate(["0","1","1","0"]):
            page.locator("#mat-grid input").nth(i).fill(value)
        page.locator("#mat-qr").click()
        output=page.locator("#mat-result").inner_text()
        assert "A = Q·R" in output and "Orthogonality residual:" in output,output
        page.locator("#mat-qr-factor").select_option("Q")
        page.locator("#mat-send").click()
        assert "matrix([0,1],[1,0])" in page.locator("#equation-input").input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        page.locator("#mat-grid input").first.fill("2")
        assert page.locator("#mat-send").is_disabled()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#mat-qr").is_visible()
        assert not errors,errors
        browser.close()
    print("PASS: thin QR reference, orthogonality, rank refusal, editor and responsive UI")

if __name__=="__main__":
    main()
