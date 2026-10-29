"""Scale-safe rectangular SVD diagnostics and near-rank-one 80-digit references."""
import math
import os
from decimal import Decimal, getcontext
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
getcontext().prec = 80

def rotated_matrix(delta, scale):
    # Exact rational orthonormal Q columns (3D Householder) and 2D rotation.
    q0 = [Decimal(7)/9, Decimal(-4)/9, Decimal(-4)/9]
    q1 = [Decimal(-4)/9, Decimal(1)/9, Decimal(-8)/9]
    r0 = [Decimal(5)/13, Decimal(12)/13]
    r1 = [Decimal(-12)/13, Decimal(5)/13]
    a = [[scale*(Decimal(3)*q0[i]*r0[j]+delta*q1[i]*r1[j])
          for j in range(2)] for i in range(3)]
    return [[float(x) for x in row] for row in a]

def check_result(result, a, rank, small, scale):
    s, u, v = result['S'], result['U'], result['V']
    assert result['rank'] == rank, (rank, result)
    assert len(u) == 3 and all(len(row) == 2 for row in u)
    assert len(v) == 2 and all(len(row) == 2 for row in v)
    assert s[0] >= s[1] >= 0
    assert math.isclose(s[0], 3*scale, rel_tol=2e-12), result
    assert math.isclose(result['cutoff'], 3e-12*scale, rel_tol=2e-12), result
    if rank == 2:
        assert math.isclose(s[1], small*scale, rel_tol=5e-4), (small, s)
        assert result['conditionAssessment'] == 'ill-conditioned', result
        assert math.isclose(result['conditionNumber'], 3/small, rel_tol=5e-4), result
    else:
        assert s[1] <= result['cutoff'], result
        assert result['conditionNumber'] is None, result
        assert result['conditionAssessment'] == 'rank deficient', result
    assert result['residual'] < 1e-8 and result['orthogonalityU'] < 1e-8 and result['orthogonalityV'] < 1e-8, result
    reconstructed = [[sum(u[i][k]*s[k]*v[j][k] for k in range(2))
                      for j in range(2)] for i in range(3)]
    assert max(abs(reconstructed[i][j]-a[i][j])/scale for i in range(3) for j in range(2)) < 1e-8, result

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1280, 'height':850})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'), wait_until='load')
        for scale in (Decimal('1e-12'), Decimal('1'), Decimal('1e12')):
            for small, rank in ((Decimal('3e-9'), 2), (Decimal('3e-11'), 2), (Decimal('3e-13'), 1)):
                a = rotated_matrix(small, scale)
                original = [row[:] for row in a]
                result = page.evaluate('(a)=>MathStudio.matrixTools.svd3x2(a)', a)
                assert a == original
                check_result(result, a, rank, float(small), float(scale))
                wide = [list(row) for row in zip(*a)]
                w = page.evaluate('(a)=>MathStudio.matrixTools.svd2x3(a)', wide)
                assert w['rank'] == result['rank'] and w['conditionAssessment'] == result['conditionAssessment'], w
                assert math.isclose(w['cutoff'], result['cutoff'], rel_tol=1e-12)
                assert w['conditionNumber'] == result['conditionNumber']
                assert w['U'] == result['V'] and w['V'] == result['U']
        for a, rank, condition in (
            ([[0,0],[0,0],[0,0]], 0, 'rank deficient'),
            ([[4,0],[0,1],[0,0]], 2, 'well-conditioned'),
            ([[1,0],[0,1e-5],[0,0]], 2, 'moderately conditioned'),
            ([[1,0],[0,1e-9],[0,0]], 2, 'ill-conditioned'),
            ([[1,0],[0,1e-13],[0,0]], 1, 'rank deficient'),
        ):
            r = page.evaluate('(a)=>MathStudio.matrixTools.svd3x2(a)', a)
            assert r['rank'] == rank and r['conditionAssessment'] == condition, r
            assert r['cutoff'] >= 0
        for bad in ([[1,2],[3,4]], [[1,2,3],[4,5,6],[7,8,9]], [[1,''],[0,1],[0,0]], [[1e13,0],[0,1],[0,0]]):
            msg = page.evaluate('(a)=>{try{MathStudio.matrixTools.svd3x2(a);return ""}catch(e){return e.message}}', bad)
            assert msg, bad
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('3')
        page.locator('#mat-cols').select_option('2')
        assert '2×3' in page.locator('#mat-svd').inner_text()
        for i, value in enumerate(('3','0','0','2','0','0')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-svd').click()
        output = page.locator('#mat-result').inner_text()
        assert 'Rank cutoff (absolute):' in output and 'Condition assessment: well-conditioned' in output, output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-svd-factor').select_option('S')
        page.locator('#mat-send').click()
        assert 'matrix([3],[2])' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('2')
        page.locator('#mat-cols').select_option('3')
        for i, value in enumerate(('3','0','0','0','2','0')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-svd').click()
        output = page.locator('#mat-result').inner_text()
        assert 'Rank cutoff (absolute):' in output and 'Condition assessment: well-conditioned' in output, output
        for width in (390, 768, 1280):
            page.set_viewport_size({'width':width, 'height':850})
            assert page.locator('#mat-svd').is_visible()
        assert not errors, errors
        browser.close()
    print('PASS: rectangular SVD cutoff/condition, 80-digit near-rank-one references, transpose parity and mobile UI')

if __name__ == '__main__':
    main()
