"""2×3 Moore–Penrose pseudoinverse: reference, duality, validation, UI and mobile."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def transpose(a):
    return [list(col) for col in zip(*a)]

def mul(a,b):
    return [[sum(x*b[k][j] for k,x in enumerate(row)) for j in range(len(b[0]))] for row in a]

def close(a,b,tol=1e-8):
    assert len(a)==len(b) and len(a[0])==len(b[0]),(a,b)
    scale=max(1e-300,*(abs(x) for row in b for x in row))
    return max(abs(a[i][j]-b[i][j])/scale for i in range(len(a)) for j in range(len(a[0])))<=tol

def check(a,expected,rank,result):
    p=result['matrix']
    assert result['rank']==rank,(a,result)
    assert len(p)==3 and all(len(row)==2 for row in p),p
    assert close(p,expected),(a,p,expected)
    assert result['residual']<=1e-8 and result['symmetryResidual']<=1e-8,result
    ap,pa=mul(a,p),mul(p,a)
    assert close(mul(ap,a),a) and close(mul(pa,p),p)
    assert close(ap,transpose(ap)) and close(pa,transpose(pa))

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        cases=[
            ([[1,0,1],[0,1,1]],[[2/3,-1/3],[-1/3,2/3],[1/3,1/3]],2),
            ([[1,2,3],[2,4,6]],[[1/70,2/70],[2/70,4/70],[3/70,6/70]],1),
            ([[0,0,0],[0,0,0]],[[0,0],[0,0],[0,0]],0),
            ([[1,0,0],[0,1,0]],[[1,0],[0,1],[0,0]],2),
            ([[1e12,0,0],[0,1e-9,0]],[[1e-12,0],[0,0],[0,0]],1),
            ([[1e-12,0,0],[0,1e-12,0]],[[1e12,0],[0,1e12],[0,0]],2),
        ]
        for a,expected,rank in cases:
            original=[row[:] for row in a]
            result=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse2x3(a)',a)
            assert a==original
            check(a,expected,rank,result)
            dispatched=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse(a)',a)
            assert close(dispatched['matrix'],expected)
            dual=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse3x2(a)',transpose(a))
            assert close(result['matrix'],transpose(dual['matrix']))
        a=[[1,0,1],[0,1,1]]
        p=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse(a).matrix',a)
        assert close(mul(p,[[1],[2]]),[[0],[1],[1]]) # minimum-norm exact solution
        for a,phrase in (
            ([[1,0,0],[0,1,0],[0,0,1]],'2×2, 3×2 or 2×3'),
            ([[1,'',0],[0,1,0]],'Enter a number'),
            ([[1,True,0],[0,1,0]],'Enter a number'),
            ([[1e13,0,0],[0,1,0]],'finite'),
        ):
            msg=page.evaluate('(a)=>{try{MathStudio.matrixTools.pseudoinverse(a);return ""}catch(e){return e.message}}',a)
            assert phrase in msg,(a,msg)
        assert close(page.evaluate('()=>MathStudio.matrixTools.pseudoinverse([[1,2],[3,4]]).matrix'),[[-2,1],[1.5,-.5]])
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-cols').select_option('3')
        for i,v in enumerate(['1','0','1','0','1','1']):
            page.locator('#mat-grid input').nth(i).fill(v)
        page.locator('#mat-pseudoinverse').click()
        output=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 2' in output and 'Moore-Penrose' in output,output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-send').click()
        editor=page.locator('#equation-input').input_value()
        assert 'matrix(' in editor and '0.666666666667' in editor,editor
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
    print('PASS: wide 2x3 pseudoinverse, duality, identities, least-norm, UI, responsive')

if __name__=='__main__':
    main()
