"""3x3 pseudoinverse independent reference oracles, identities, UI and mobile."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
def mul(a,b):
    return [[sum(x*b[k][j] for k,x in enumerate(row)) for j in range(len(b[0]))] for row in a]
def trans(a):
    return [list(col) for col in zip(*a)]
def close(a,b,tol=1e-8):
    scale=max(1e-300,*(abs(x) for row in b for x in row))
    return max(abs(a[i][j]-b[i][j])/scale for i in range(3) for j in range(3))<=tol

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        cases=[
            ([[1,0,0],[0,1,0],[0,0,1]],[[1,0,0],[0,1,0],[0,0,1]],3),
            ([[3,0,0],[0,2,0],[0,0,1]],[[1/3,0,0],[0,1/2,0],[0,0,1]],3),
            ([[1,2,3],[2,4,6],[3,6,9]],[[x/196 for x in row] for row in [[1,2,3],[2,4,6],[3,6,9]]],1),
            ([[1,0,0],[0,1,0],[0,0,0]],[[1,0,0],[0,1,0],[0,0,0]],2),
            ([[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],0),
            ([[1e-12,0,0],[0,1e-12,0],[0,0,1e-12]],[[1e12,0,0],[0,1e12,0],[0,0,1e12]],3),
            ([[1,0,0],[0,1e-10,0],[0,0,1e-13]],[[1,0,0],[0,1e10,0],[0,0,0]],2),
        ]
        for a,expected,rank in cases:
            original=[row[:] for row in a]
            result=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse3x3(a)',a)
            assert a==original and result['rank']==rank,(a,result)
            p=result['matrix']
            assert close(p,expected,1e-7),(a,p,expected)
            assert result['residual']<=1e-8 and result['symmetryResidual']<=1e-8,result
            ap,pa=mul(a,p),mul(p,a)
            assert close(mul(ap,a),a) and close(mul(pa,p),p)
            assert close(ap,trans(ap)) and close(pa,trans(pa))
            assert close(page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse(a).matrix',a),expected,1e-7)
            assert result['singularValues']==sorted(result['singularValues'],reverse=True)
            assert result['conditionNumber'] is None if rank<3 else result['conditionNumber']>=1
        # Non-symmetric full-rank oracle from independent exact inverse.
        a=[[1,2,0],[0,1,1],[1,0,1]]
        expected=[[1/3,-2/3,2/3],[1/3,1/3,-1/3],[-1/3,2/3,1/3]]
        result=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse(a)',a)
        assert close(result['matrix'],expected,1e-8),result
        for invalid in ([[1,2],[3,4]],[[1,'',0],[0,1,0],[0,0,1]],[[1e13,0,0],[0,1,0],[0,0,1]]):
            msg=page.evaluate('(a)=>{try{MathStudio.matrixTools.pseudoinverse3x3(a);return ""}catch(e){return e.message}}',invalid)
            assert msg,invalid
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('3')
        page.locator('#mat-cols').select_option('3')
        for i,value in enumerate(('3','0','0','0','2','0','0','0','1')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-pseudoinverse').click()
        output=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 3' in output and 'Condition number: 3' in output,output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-send').click()
        assert 'matrix(' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-grid input').first.fill('')
        assert page.locator('#mat-send').is_disabled()
        page.locator('#mat-pseudoinverse').click()
        assert 'Enter a number' in page.locator('#mat-result').inner_text()
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-pseudoinverse').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: 3x3 pseudoinverse rank 0-3, references, identities, validation, editor, mobile')
if __name__=='__main__':
    main()
