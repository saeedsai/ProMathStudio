"""Near-dependent 3x2/2x3 pseudoinverse reference, negative and responsive regression."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def close(a,b):
    return math.isclose(a,b,rel_tol=1e-7,abs_tol=1e-7)
def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        for eps in (1e-8,1e-10):
            p=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse3x2(a)',[[1,1],[0,eps],[0,0]])
            m=p['matrix']
            assert p['rank']==2 and close(m[0][0],1) and close(m[1][0],0),(eps,p)
            assert close(m[0][1],-1/eps) and close(m[1][1],1/eps),(eps,p)
            assert p['conditionNumber']>1e8 and p['residual']<1e-8 and p['symmetryResidual']<1e-8,p
            w=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse2x3(a)',[[1,0,0],[1,eps,0]])
            assert w['rank']==2 and close(w['matrix'][0][0],1),(eps,w)
            for i in range(3):
                for j in range(2):
                    assert close(w['matrix'][i][j],m[j][i]),(eps,w,m)
        scaled=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse(a)',[[1e-6,1e-6],[0,1e-14],[0,0]])
        assert scaled['rank']==2 and close(scaled['matrix'][0][0],1e6),scaled
        assert close(scaled['matrix'][0][1],-1e14) and close(scaled['matrix'][1][1],1e14)
        near=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse(a)',[[1,1],[0,1e-13],[0,0]])
        assert near['rank']==1 and near['conditionNumber'] is None
        assert close(near['matrix'][0][0],.5) and close(near['matrix'][1][0],.5)
        zero=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse(a)',[[0,0],[0,0],[0,0]])
        assert zero['rank']==0 and zero['conditionNumber'] is None
        assert all(x==0 for row in zero['matrix'] for x in row)
        unstable=page.evaluate('(a)=>{try{MathStudio.matrixTools.pseudoinverse(a);return ""}catch(e){return e.message}}',[[1,1],[1,1+1e-9],[1,1-1e-9]])
        assert 'numerically unstable' in unstable,unstable
        invalid=page.evaluate('(a)=>{try{MathStudio.matrixTools.pseudoinverse(a);return ""}catch(e){return e.message}}',[[1e13,0],[0,1],[0,0]])
        assert 'finite' in invalid,invalid
        # Existing 2x2 rank-one case reports the same rank-deficient diagnostic.
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        for i,value in enumerate(['1','2','2','4']):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-pseudoinverse').click()
        prior=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 1' in prior and 'Condition number: rank deficient' in prior,prior
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('3')
        for i,value in enumerate(['1','1','0','0.00000001','0','0']):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-pseudoinverse').click()
        out=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 2' in out and 'Condition number:' in out,out
        assert page.locator('#mat-send').is_enabled()
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-pseudoinverse').is_visible()
            assert 'Condition number:' in page.locator('#mat-result').inner_text()
        assert not errors,errors
        browser.close()
    print('PASS: near-dependent QR pseudoinverse, wide duality, rank cutoff, UI and mobile')
if __name__=='__main__':
    main()
