"""Moore-Penrose 2x2 pseudoinverse: reference matrices, identities, UI and mobile."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def mul(A, B):
    return [[sum(x * B[k][j] for k, x in enumerate(row)) for j in range(len(B[0]))] for row in A]

def close(A, B, tol=1e-8):
    scale = max(1e-300, *(abs(x) for row in B for x in row))
    return max(abs(A[i][j] - B[i][j]) / scale for i in range(2) for j in range(2)) <= tol

def check(A, expected, rank, result):
    B = result['matrix']
    assert result['rank'] == rank, (A, result)
    assert result['residual'] < 1e-8 and result['symmetryResidual'] < 1e-8, (A, result)
    assert close(B, expected), (A, B, expected)
    AB, BA = mul(A, B), mul(B, A)
    assert close(mul(AB, A), A), (A, result)
    assert close(mul(BA, B), B), (A, result)
    assert close(AB, [list(x) for x in zip(*AB)])
    assert close(BA, [list(x) for x in zip(*BA)])

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1280,'height':850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'), wait_until='load')
        cases = [
            ([[1,2],[3,4]],[[-2,1],[1.5,-0.5]],2),
            ([[1,2],[2,4]],[[.04,.08],[.08,.16]],1),
            ([[0,0],[0,0]],[[0,0],[0,0]],0),
            ([[0,1],[1,0]],[[0,1],[1,0]],2),
            ([[-2,0],[0,3]],[[-.5,0],[0,1/3]],2),
            ([[1e12,0],[0,1e-9]],[[1e-12,0],[0,0]],1),
            ([[1e-12,0],[0,1e-12]],[[1e12,0],[0,1e12]],2),
        ]
        for A, expected, rank in cases:
            original = [row[:] for row in A]
            result = page.evaluate('(A)=>MathStudio.matrixTools.pseudoinverse2x2(A)', A)
            assert A == original, (A, original)
            check(A, expected, rank, result)
        for A, phrase in [
            ([[1,2,3],[4,5,6]],'2×2'),
            ([[1,0,0],[0,1,0],[0,0,1]],'2×2'),
            ([[1,''],[0,1]],'Enter a number'),
            ([[1,True],[0,1]],'Enter a number'),
            ([[1e13,0],[0,1]],'finite'),
        ]:
            message = page.evaluate('(A)=>{try{MathStudio.matrixTools.pseudoinverse2x2(A);return "";}catch(e){return e.message;}}', A)
            assert phrase in message, (A, message)
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        assert page.locator('#matrix-tools').evaluate('(e)=>e.open')
        for i, value in enumerate(['1','2','2','4']):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-pseudoinverse').click()
        output = page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 1' in output and 'Moore-Penrose' in output, output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-send').click()
        assert 'matrix([0.04,0.08],[0.08,0.16])' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-grid input').first.fill('')
        assert page.locator('#mat-send').is_disabled()
        page.locator('#mat-pseudoinverse').click()
        assert 'Enter a number' in page.locator('#mat-result').inner_text()
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-pseudoinverse').is_visible()
        assert not errors, errors
        browser.close()
    print('PASS 2x2 Moore-Penrose pseudoinverse references, identities, validation, UI and mobile')

if __name__ == '__main__':
    main()
