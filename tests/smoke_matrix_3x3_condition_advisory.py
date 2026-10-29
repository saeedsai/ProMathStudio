"""3x3 condition-risk numerical references, instability rejection and browser UI."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
def mm(a,b):
    return [[sum(x*b[k][j] for k,x in enumerate(row)) for j in range(len(b[0]))] for row in a]
def tr(a):
    return [list(col) for col in zip(*a)]
def rot(t,p,q):
    m=[[float(i==j) for j in range(3)] for i in range(3)]
    c,s=math.cos(t),math.sin(t)
    m[p][p]=m[q][q]=c
    m[p][q],m[q][p]=-s,s
    return m
def diag(a,b,c):
    return [[a,0,0],[0,b,0],[0,0,c]]
def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        cases=[
            (diag(3,2,1),3,'well-conditioned',3),
            (diag(1,1e-5,1e-6),3,'moderately conditioned',1e6),
            (diag(1,1e-8,1e-9),3,'ill-conditioned',1e9),
            (diag(1e-12,1e-18,1e-21),3,'ill-conditioned',1e9),
            (diag(1,1e-10,1e-13),2,'rank deficient',None),
            (diag(0,0,0),0,'rank deficient',None),
        ]
        for a,rank,assessment,condition in cases:
            original=[row[:] for row in a]
            result=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse3x3(a)',a)
            assert a==original and result['rank']==rank,(a,result)
            assert result['conditionAssessment']==assessment,(a,result)
            assert result['residual']<=1e-8 and result['symmetryResidual']<=1e-8,result
            assert result['singularValues']==sorted(result['singularValues'],reverse=True),result
            assert math.isclose(result['cutoff'],result['singularValues'][0]*1e-12,rel_tol=1e-12,abs_tol=1e-300),result
            if condition is None:
                assert result['conditionNumber'] is None,(a,result)
            else:
                assert math.isclose(result['conditionNumber'],condition,rel_tol=1e-8),(a,result)
            assert page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse(a).conditionAssessment',a)==assessment
        # Independent orthogonal-factor oracle for a rotated, nearly dependent matrix.
        u=mm(rot(.6,0,1),rot(-.7,1,2))
        v=mm(rot(.3,0,2),rot(-.8,0,1))
        a=mm(mm(u,diag(1,1e-6,5e-7)),tr(v))
        expected=mm(mm(v,diag(1,1e6,2e6)),tr(u))
        result=page.evaluate('(a)=>MathStudio.matrixTools.pseudoinverse3x3(a)',a)
        scale=max(abs(x) for row in expected for x in row)
        error=max(abs(result['matrix'][i][j]-expected[i][j]) for i in range(3) for j in range(3))/scale
        assert result['rank']==3 and result['conditionAssessment']=='moderately conditioned',(result,error)
        assert math.isclose(result['conditionNumber'],2e6,rel_tol=1e-7),result
        assert error<1e-8,(error,result)
        # The existing strict stability gate must reject an unreliable inverse.
        unstable=mm(mm(u,diag(1,1e-9,5e-10)),tr(v))
        message=page.evaluate('(a)=>{try{MathStudio.matrixTools.pseudoinverse3x3(a);return ""}catch(e){return e.message}}',unstable)
        assert 'numerically unstable' in message,message
        for invalid in ([[1,0],[0,1]],[[1,'',0],[0,1,0],[0,0,1]],diag(1e13,1,1)):
            message=page.evaluate('(a)=>{try{MathStudio.matrixTools.pseudoinverse3x3(a);return ""}catch(e){return e.message}}',invalid)
            assert message,invalid
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('3')
        page.locator('#mat-cols').select_option('3')
        for i,value in enumerate(('1','0','0','0','1e-8','0','0','0','1e-9')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-pseudoinverse').click()
        output=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 3' in output and 'Condition assessment: ill-conditioned' in output,output
        assert 'Singular values: 1.000000e+0, 1.000000e-8, 1.000000e-9' in output,output
        assert 'Rank cutoff (absolute): 1.000e-12' in output,output
        assert page.locator('#mat-send').is_enabled()
        page.locator('#mat-send').click()
        assert 'matrix(' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        for i,value in enumerate(('1','0','0','0','1e-10','0','0','0','1e-13')):
            page.locator('#mat-grid input').nth(i).fill(value)
        page.locator('#mat-pseudoinverse').click()
        assert 'Condition assessment: rank deficient' in page.locator('#mat-result').inner_text()
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-pseudoinverse').is_visible()
            assert 'Condition assessment: rank deficient' in page.locator('#mat-result').inner_text()
        assert not errors,errors
        browser.close()
    print('PASS: 3x3 risk levels, scale, rotated oracle, instability, UI and mobile')
if __name__=='__main__':
    main()
