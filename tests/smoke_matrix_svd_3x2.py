"""Thin 3x2 real SVD: rank 0-2, independent references, factor transfer and mobile."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def mul(a,b):
    return [[sum(x*b[k][j] for k,x in enumerate(row)) for j in range(len(b[0]))] for row in a]

def transpose(a):
    return [list(col) for col in zip(*a)]

def check(a,result,rank,reference):
    assert result['rank']==rank,(a,result)
    s,u,v=result['S'],result['U'],result['V']
    assert len(s)==2 and s[0]>=s[1]>=0,(a,result)
    assert len(u)==3 and all(len(row)==2 for row in u)
    assert len(v)==2 and all(len(row)==2 for row in v)
    for x,y in zip(s,reference):
        assert math.isclose(x,y,rel_tol=1e-8,abs_tol=1e-20),(a,s,reference)
    reconstruction=mul(mul(u,[[s[0],0],[0,s[1]]]),transpose(v))
    scale=max(1e-300,*(abs(x) for row in a for x in row))
    assert max(abs(reconstruction[i][j]-a[i][j])/scale for i in range(3) for j in range(2))<1e-8,(a,result)
    for factors in (u,v):
        gram=mul(transpose(factors),factors)
        assert max(abs(gram[i][j]-float(i==j)) for i in range(2) for j in range(2))<1e-8,(a,result)
    assert result['residual']<1e-8 and result['orthogonalityU']<1e-8 and result['orthogonalityV']<1e-8,result
    assert (result['conditionNumber'] is None)==(rank<2),result

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        rt=math.sqrt(2)
        cases=[
            ([[0,0],[0,0],[0,0]],0,[0,0]),
            ([[1,2],[2,4],[3,6]],1,[math.sqrt(70),0]),
            ([[3,0],[0,2],[0,0]],2,[3,2]),
            ([[1,0],[0,1],[1,1]],2,[math.sqrt(3),1]),
            ([[3/rt,-2/rt],[3/rt,2/rt],[0,0]],2,[3,2]),
            ([[1e-12,0],[0,2e-12],[0,0]],2,[2e-12,1e-12]),
            ([[1e12,0],[0,1e-9],[0,0]],1,[1e12,1e-9]),
        ]
        for a,rank,reference in cases:
            original=[row[:] for row in a]
            result=page.evaluate('(a)=>MathStudio.matrixTools.svd3x2(a)',a)
            assert a==original
            check(a,result,rank,reference)
        for invalid in ([[1,2],[3,4]],[[1,0,0],[0,1,0],[0,0,1]],[[1,''],[0,1],[0,0]],[[1e13,0],[0,1],[0,0]]):
            msg=page.evaluate('(a)=>{try{MathStudio.matrixTools.svd3x2(a);return ""}catch(e){return e.message}}',invalid)
            assert msg,invalid
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('3')
        page.locator('#mat-cols').select_option('2')
        for i,value in enumerate(('3','0','0','2','0','0')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-svd').click()
        output=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 2' in output and 'U:' in output and 'V:' in output,output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-svd-factor').select_option('S')
        page.locator('#mat-send').click()
        assert 'matrix([3],[2])' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-svd').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: thin 3x2 SVD reference, rank 0-2, orthogonality, transfer and responsive UI')

if __name__=='__main__':
    main()
