"""3x3 SVD condition diagnostics: high-precision rotated references, rank cutoff and UI."""
import math
import os
from decimal import Decimal, localcontext
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def mm(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]

def tr(a):
    return [list(col) for col in zip(*a)]

def rotation(p,q,c,s):
    out=[[Decimal(i==j) for j in range(3)] for i in range(3)]
    out[p][p]=out[q][q]=Decimal(c[0])/Decimal(c[1])
    out[p][q]=-Decimal(s[0])/Decimal(s[1])
    out[q][p]=Decimal(s[0])/Decimal(s[1])
    return out

def diagonal(values):
    return [[values[i] if i==j else type(values[0])(0) for j in range(3)] for i in range(3)]

def check_factors(a,result):
    s,u,v=result['S'],result['U'],result['V']
    assert len(s)==3 and s[0]>=s[1]>=s[2]>=0,result
    norm=max(abs(x) for row in a for x in row)
    reconstruction=mm(mm(u,diagonal(s)),tr(v))
    assert max(abs(reconstruction[i][j]-a[i][j])/norm for i in range(3) for j in range(3))<1e-8,result
    for factor in (u,v):
        gram=mm(tr(factor),factor)
        assert max(abs(gram[i][j]-float(i==j)) for i in range(3) for j in range(3))<1e-8,result
    assert result['residual']<1e-8 and result['orthogonalityU']<1e-8 and result['orthogonalityV']<1e-8,result

def main():
    with localcontext() as ctx:
        ctx.prec=75
        left=mm(rotation(0,1,(3,5),(4,5)),rotation(1,2,(5,13),(12,13)))
        right=mm(rotation(0,2,(8,17),(15,17)),rotation(0,1,(3,5),(4,5)))
        exact=mm(mm(left,diagonal([Decimal(1),Decimal('1e-6'),Decimal('1e-9')])),tr(right))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        for scale in (1e-12,1,1e12):
            a=[[float(x)*scale for x in row] for row in exact]
            original=[row[:] for row in a]
            result=page.evaluate('(a)=>MathStudio.matrixTools.svd3x3(a)',a)
            assert a==original
            assert result['rank']==3 and result['conditionAssessment']=='ill-conditioned',result
            assert math.isclose(result['conditionNumber'],1e9,rel_tol=2e-6),result
            assert math.isclose(result['cutoff'],1e-12*scale,rel_tol=1e-8),result
            for actual,expected in zip(result['S'],[scale,1e-6*scale,1e-9*scale]):
                assert math.isclose(actual,expected,rel_tol=2e-6),result
            check_factors(a,result)
        for a,rank,assessment in (
            (diagonal([1.,1e-12,0.]),1,'rank deficient'),
            (diagonal([1.,1.01e-12,0.]),2,'rank deficient'),
            (diagonal([1.,1e-5,1e-6]),3,'moderately conditioned'),
            (diagonal([3.,2.,1.]),3,'well-conditioned'),
            (diagonal([0.,0.,0.]),0,'rank deficient'),
        ):
            result=page.evaluate('(a)=>MathStudio.matrixTools.svd3x3(a)',a)
            assert result['rank']==rank and result['conditionAssessment']==assessment,(a,result)
            assert result['cutoff']==(1e-12*max(abs(x) for row in a for x in row)),(a,result)
            assert (result['conditionNumber'] is None)==(rank<3),(a,result)
            if rank>0:
                check_factors(a,result)
        for invalid in ([[1,0],[0,1]],[[1,0,0],[0,'',0],[0,0,1]],[[1e13,0,0],[0,1,0],[0,0,1]]):
            message=page.evaluate('(a)=>{try{MathStudio.matrixTools.svd3x3(a);return ""}catch(e){return e.message}}',invalid)
            assert message,invalid
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('3')
        page.locator('#mat-cols').select_option('3')
        for i,value in enumerate(('1','0','0','0','1e-8','0','0','0','1e-9')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-svd').click()
        output=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 3' in output and 'Condition assessment: ill-conditioned' in output,output
        assert 'Rank cutoff (absolute): 1.000e-12' in output,output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-svd-factor').select_option('S')
        page.locator('#mat-send').click()
        assert 'matrix([1],[1e-8],[1e-9])' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-svd').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: 3x3 SVD 75-digit rotated references, cutoff boundaries, condition risk, UI and mobile')

if __name__=='__main__': main()
