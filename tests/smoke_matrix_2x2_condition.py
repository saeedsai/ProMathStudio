"""Numerical and browser QA for real 2x2 pseudoinverse condition diagnostics."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1280,'height':850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'), wait_until='load')
        cases = [
            ([[3,0],[0,1]],2,3,[3,1]),
            ([[1,0],[0,1]],2,1,[1,1]),
            ([[1,0],[0,1e-10]],2,1e10,[1,1e-10]),
            ([[1,2],[2,4]],1,None,None),
            ([[1,0],[0,1e-13]],1,None,[1,1e-13]),
            ([[0,0],[0,0]],0,None,[0,0]),
        ]
        for A,rank,condition,singular in cases:
            before=[row[:] for row in A]
            result=page.evaluate('(A)=>MathStudio.matrixTools.pseudoinverse(A)',A)
            assert A==before and result['rank']==rank,(A,result)
            assert result['residual']<1e-8 and result['symmetryResidual']<1e-8,result
            assert len(result['singularValues'])==2 and result['singularValues'][0]>=result['singularValues'][1]>=0,result
            if condition is None:
                assert result['conditionNumber'] is None,(A,result)
            else:
                assert math.isclose(result['conditionNumber'],condition,rel_tol=1e-8),(A,result)
            if singular is not None:
                for actual,expected in zip(result['singularValues'],singular):
                    assert math.isclose(actual,expected,rel_tol=1e-8,abs_tol=1e-20),(A,result)
        for invalid in ([[1,2,3],[4,5,6]],[[1,''],[0,1]],[[1e13,0],[0,1]]):
            message=page.evaluate('(A)=>{try{MathStudio.matrixTools.pseudoinverse2x2(A);return ""}catch(e){return e.message}}',invalid)
            assert message,invalid
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        for i,value in enumerate(('3','0','0','1')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-pseudoinverse').click()
        out=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 2' in out and 'Condition number: 3' in out,out
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-send').click()
        assert 'matrix(' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        for i,value in enumerate(('1','2','2','4')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-pseudoinverse').click()
        assert 'Condition number: rank deficient' in page.locator('#mat-result').inner_text()
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-pseudoinverse').is_visible()
            assert 'Condition number: rank deficient' in page.locator('#mat-result').inner_text()
        assert not errors,errors
        browser.close()
    print('PASS: 2x2 condition references, cutoff, zero, invalid, editor and mobile')
if __name__=='__main__':
    main()
