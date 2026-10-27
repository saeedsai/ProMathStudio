"""Bounded real 2x2 SVD: numerical references, rank, residuals, UI and editor."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def check(A, result, expected, rank):
    assert result['rank'] == rank and len(result['S']) == 2
    assert result['S'][0] >= result['S'][1] >= 0
    for actual, reference in zip(result['S'], expected):
        assert math.isclose(actual, reference, rel_tol=1e-8, abs_tol=1e-12*max(abs(reference), 1e-12)), (A, result, expected)
    assert result['residual'] < 1e-8
    assert result['orthogonalityU'] < 1e-8 and result['orthogonalityV'] < 1e-8
    for i in range(2):
        for j in range(2):
            value = sum(result['U'][i][k]*result['S'][k]*result['V'][j][k] for k in range(2))
            assert math.isclose(value, A[i][j], rel_tol=1e-8, abs_tol=1e-8*max(abs(x) for row in A for x in row, default=1)), (A, result)
            for key in ('U','V'):
                dot = sum(result[key][k][i]*result[key][k][j] for k in range(2))
                assert math.isclose(dot, float(i == j), abs_tol=1e-8)

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1280,'height':850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'), wait_until='load')
        cases = [
            ([[1,2],[3,4]],[5.4649857042190435,0.36596619062625774],2),
            ([[1,2],[2,4]],[5,0],1),
            ([[0,0],[0,0]],[0,0],0),
            ([[0,1],[1,0]],[1,1],2),
            ([[-2,0],[0,3]],[3,2],2),
            ([[1e12,0],[0,1e-9]],[1e12,1e-9],1),
            ([[1e-12,0],[0,1e-12]],[1e-12,1e-12],2),
        ]
        for A, expected, rank in cases:
            original = [row[:] for row in A]
            result = page.evaluate('(A)=>MathStudio.matrixTools.svd2x2(A)', A)
            assert A == original
            check(A, result, expected, rank)
        for A, phrase in [
            ([[1,2,3],[4,5,6]],'2×2'),
            ([[1,0,0],[0,1,0],[0,0,1]],'2×2'),
            ([[1,''],[0,1]],'Enter a number'),
            ([[1,True],[0,1]],'Enter a number'),
            ([[1e13,0],[0,1]],'finite'),
        ]:
            message = page.evaluate('(A)=>{try{MathStudio.matrixTools.svd2x2(A);return "";}catch(e){return e.message;}}', A)
            assert phrase in message, (A, message)
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-guide .task-choice[data-task="matrix"]').click()
        assert page.locator('#matrix-tools').evaluate('(e)=>e.open')
        for i, value in enumerate(['3','0','0','2']):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-svd').click()
        output = page.locator('#mat-result').inner_text()
        assert 'Singular values (descending): 3, 2' in output and 'orthogonality residual' in output, output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-svd-factor').select_option('S')
        page.locator('#mat-send').click()
        assert 'matrix([3],[2])' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-guide .task-choice[data-task="matrix"]').click()
        page.locator('#mat-grid input').first.fill('')
        assert page.locator('#mat-send').is_disabled()
        page.locator('#mat-svd').click()
        assert 'Enter a number' in page.locator('#mat-result').inner_text()
        page.set_viewport_size({'width':390,'height':844})
        assert page.locator('#mat-svd').is_visible()
        assert not errors, errors
        browser.close()
    print('PASS real 2x2 SVD, rank/zero/scaled references, reconstruction, UI, editor, invalid inputs')

if __name__ == '__main__':
    main()
