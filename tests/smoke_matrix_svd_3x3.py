"""3x3 real Jacobi SVD: rank 0-3, independent references, UI and mobile."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def matmul(a,b):
    return [[sum(x*b[k][j] for k,x in enumerate(row)) for j in range(len(b[0]))] for row in a]

def transpose(a):
    return [list(col) for col in zip(*a)]

def check(a,result,rank,reference=None):
    assert result['rank']==rank,(a,result)
    s=result['S']
    assert len(s)==3 and all(s[i]>=s[i+1] for i in range(2)),result
    if reference is not None:
        for actual,expected in zip(s,reference):
            assert math.isclose(actual,expected,rel_tol=1e-8,abs_tol=1e-12),(a,s,reference)
    u,v=result['U'],result['V']
    reconstruction=matmul(matmul(u,[[s[i] if i==j else 0 for j in range(3)] for i in range(3)]),transpose(v))
    scale=max(1e-300,*(abs(x) for row in a for x in row))
    assert max(abs(reconstruction[i][j]-a[i][j])/scale for i in range(3) for j in range(3))<1e-8,(a,result)
    for q in (u,v):
        gram=matmul(transpose(q),q)
        assert max(abs(gram[i][j]-(i==j)) for i in range(3) for j in range(3))<1e-8,(a,result)
    assert result['residual']<1e-8 and result['orthogonalityU']<1e-8 and result['orthogonalityV']<1e-8,result
    assert (result['conditionNumber'] is None)==(rank<3),result

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        cases=[
            ([[0,0,0],[0,0,0],[0,0,0]],0,[0,0,0]),
            ([[1,2,3],[2,4,6],[3,6,9]],1,[14,0,0]),
            ([[3,0,0],[0,2,0],[0,0,0]],2,[3,2,0]),
            ([[0,-3,0],[2,0,0],[0,0,1]],3,[3,2,1]),
            ([[1,2,0],[0,1,1],[1,0,1]],3,None),
            ([[1,0,0],[0,1e-10,0],[0,0,1e-13]],2,[1,1e-10,1e-13]),
            ([[1e-12,0,0],[0,2e-12,0],[0,0,3e-12]],3,[3e-12,2e-12,1e-12]),
        ]
        for a,rank,reference in cases:
            original=[row[:] for row in a]
            result=page.evaluate('(a)=>MathStudio.matrixTools.svd3x3(a)',a)
            assert a==original,a
            check(a,result,rank,reference)
        for invalid in ([[1,2],[3,4]],[[1,0,0],[0,'',0],[0,0,1]],[[1e13,0,0],[0,1,0],[0,0,1]]):
            message=page.evaluate('(a)=>{try{MathStudio.matrixTools.svd3x3(a);return ""}catch(e){return e.message}}',invalid)
            assert message,invalid
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('3')
        page.locator('#mat-cols').select_option('3')
        for i,value in enumerate(('0','-3','0','2','0','0','0','0','1')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-svd').click()
        output=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 3' in output and 'Singular values' in output and 'U:' in output and 'V:' in output,output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-svd-factor').select_option('S')
        page.locator('#mat-send').click()
        assert 'matrix([3],[2],[1])' in page.locator('#equation-input').input_value()
        # Equation transfer changes workspace; return to Matrix before visibility checks.
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-svd').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: 3x3 Jacobi SVD rank 0-3, references, reconstruction, UI transfer and mobile')

if __name__=='__main__': main()
