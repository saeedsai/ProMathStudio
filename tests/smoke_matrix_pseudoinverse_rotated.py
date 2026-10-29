"""Independent Decimal oracles for rotated 3x3 Moore-Penrose inverse and browser UI."""
import os
from decimal import Decimal, localcontext
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
D=Decimal

def transpose(a):
    return [list(row) for row in zip(*a)]

def mul(a,b):
    return [[sum((x*b[k][j] for k,x in enumerate(row)),D(0)) for j in range(len(b[0]))] for row in a]

def max_rel(a,b):
    scale=max(1e-300,*(abs(x) for row in b for x in row))
    return max(abs(a[i][j]-b[i][j])/scale for i in range(len(b)) for j in range(len(b[0])))

def oracle(second,third,scale):
    # Exact rational orthogonal rotations: no numpy or application SVD.
    with localcontext() as ctx:
        ctx.prec=65
        R=[[D(3)/5,-D(4)/5,D(0)],[D(4)/5,D(3)/5,D(0)],[D(0),D(0),D(1)]]
        Q=[[D(5)/13,D(0),-D(12)/13],[D(0),D(1),D(0)],[D(12)/13,D(0),D(5)/13]]
        singular=[D(1),D(second),D(third)]
        factor=D(scale)
        A=mul(mul(R,[[singular[i] if i==j else D(0) for j in range(3)] for i in range(3)]),transpose(Q))
        # Rank truncation uses a relative 1e-12 cutoff, consistent with UI.
        reciprocal=[D(1)/x if x>D('1e-12') else D(0) for x in singular]
        P=mul(mul(Q,[[reciprocal[i] if i==j else D(0) for j in range(3)] for i in range(3)]),transpose(R))
        return [[float(x*factor) for x in row] for row in A],[[float(x/factor) for x in row] for row in P],sum(x>D('1e-12') for x in singular)

def check_identities(a,p):
    def fmul(x,y):
        return [[sum(v*y[k][j] for k,v in enumerate(row)) for j in range(len(y[0]))] for row in x]
    ap,pa=fmul(a,p),fmul(p,a)
    assert max_rel(fmul(ap,a),a)<1e-8
    assert max_rel(fmul(pa,p),p)<1e-8
    assert max_rel(ap,transpose(ap))<1e-8
    assert max_rel(pa,transpose(pa))<1e-8

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        for second,third,scale in [('1e-5','1e-14','1'),('1e-5','1e-14','1e-6'),('1e-5','1e-14','1e6'),('1e-3','1e-6','1')]:
            a,expected,rank=oracle(second,third,scale)
            original=[row[:] for row in a]
            result=page.evaluate('(x)=>MathStudio.matrixTools.pseudoinverse3x3(x)',a)
            assert a==original and result['rank']==rank,(second,third,scale,result)
            assert max_rel(result['matrix'],expected)<1e-7,(second,third,scale,result,expected)
            assert result['residual']<1e-8 and result['symmetryResidual']<1e-8,result
            assert result['singularValues']==sorted(result['singularValues'],reverse=True)
            assert result['conditionNumber'] is None if rank<3 else result['conditionNumber']>1
            check_identities(a,result['matrix'])
        for invalid in ([[1,2],[3,4]],[[1,0,0],[0,'',0],[0,0,1]],[[1e13,0,0],[0,1,0],[0,0,1]]):
            msg=page.evaluate('(x)=>{try{MathStudio.matrixTools.pseudoinverse3x3(x);return ""}catch(e){return e.message}}',invalid)
            assert msg,invalid
        a,expected,rank=oracle('1e-5','1e-14','1')
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('3')
        page.locator('#mat-cols').select_option('3')
        for i,value in enumerate(x for row in a for x in row):
            page.locator('#mat-grid input').nth(i).fill(str(value))
        page.locator('#mat-pseudoinverse').click()
        output=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 2' in output and 'rank deficient' in output,output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-send').click()
        assert 'matrix(' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-pseudoinverse').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: rotated 3x3 high-precision pseudoinverse oracle, scale/rank/MP identities and UI')

if __name__=='__main__': main()
