"""Bounded pivoted LU regression: PA=LU, swaps, singularity and editor integration."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def near(a, b, tol=1e-9):
    return math.isclose(a, b, abs_tol=tol, rel_tol=tol)

def check(A, result):
    n = len(A)
    P, L, U = (result[key] for key in ("P", "L", "U"))
    assert len(P) == len(L) == len(U) == n
    assert sorted(result["permutation"]) == list(range(n))
    assert result["residual"] < 1e-8
    for i in range(n):
        assert sum(P[i]) == 1
        assert P[i][result["permutation"][i]] == 1
        for j in range(n):
            assert near(L[i][j], 0) if j > i else near(L[i][i], 1) if j == i else True
            assert near(U[i][j], 0) if j < i else True
            left = sum(P[i][k] * A[k][j] for k in range(n))
            right = sum(L[i][k] * U[k][j] for k in range(n))
            assert near(left, right, tol=1e-7), (A, result, i, j)

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":1280,"height":850})
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        for A in [
            [[1,2],[3,4]],
            [[0,1],[1,0]],
            [[0,2,1],[1,1,1],[2,1,0]],
            [[1e12,0],[0,1]],
            [[1e-8,0],[0,2e-8]],
            [[2,0,0],[0,3,0],[0,0,4]],
        ]:
            original = [row[:] for row in A]
            result = page.evaluate("(A)=>MathStudio.matrixTools.lu(A)", A)
            check(A, result)
            assert A == original
        for A, phrase in [
            ([[1,2],[2,4]], "Singular"),
            ([[1,1],[1,1+1e-14]], "Singular"),
            ([[0,0],[0,0]], "Singular"),
            ([[1,2,3],[4,5,6]], "square"),
            ([[1,2],[3,float("inf")]], "finite"),
        ]:
            if math.isinf(A[-1][-1]):
                message = page.evaluate("()=>{try{MathStudio.matrixTools.lu([[1,2],[3,Infinity]]);return ''}catch(e){return e.message}}")
            else:
                message = page.evaluate("(A)=>{try{MathStudio.matrixTools.lu(A);return ''}catch(e){return e.message}}", A)
            assert phrase in message, (A, message)
        for i, value in enumerate(["0","1","1","0"]):
            page.locator("#mat-grid input").nth(i).fill(value)
        page.locator("#mat-lu").click()
        output = page.locator("#mat-result").inner_text()
        assert "P·A = L·U" in output and "Relative reconstruction residual:" in output, output
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-lu-factor").select_option("P")
        page.locator("#mat-send").click()
        assert "matrix([0,1],[1,0])" in page.locator("#equation-input").input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#matrix-tools").evaluate("(e)=>e.open=true")
        page.locator("#mat-grid input").first.fill("2")
        assert page.locator("#mat-send").is_disabled()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#mat-lu").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: pivoted LU, PA=LU, rank/finite guards, UI/editor, stale result and mobile")

if __name__ == "__main__":
    main()
