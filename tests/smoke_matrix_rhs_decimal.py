"""Ax=b RHS uses decimal/scientific syntax and rejects JS-only numeric literals."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        A=[[1,0],[0,1]]
        for bad in ('0x10','0b10','0o10','Infinity','NaN','1_000','1e','--2'):
            message=page.evaluate("([a,x])=>{try{MathStudio.matrixTools.solve(a,[x,'1']);return ''}catch(e){return e.message}}",[A,bad])
            assert 'Right-hand side b must use decimal or scientific notation.' in message,(bad,message)
        for good,expected in (('1e-6',1e-6),('-0.5',-.5),('+2',2),('.25',.25),('2.',2),(' 3E+2 ',300)):
            result=page.evaluate("([a,x])=>MathStudio.matrixTools.solve(a,[x,'1']).solution",[A,good])
            assert abs(result[0]-expected)<1e-12 and result[1]==1,(good,result)
        assert page.evaluate("MathStudio.matrixTools.solve([[1,0],[0,1]],[2,3]).solution")==[2,3]
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('2')
        page.locator('#mat-cols').select_option('2')
        for i,value in enumerate(('1','0','0','1')):
            page.locator('#mat-grid input').nth(i).fill(value)
        rhs=page.locator('#mat-rhs-grid input')
        rhs.first.evaluate("el=>el.type='text'")
        rhs.first.fill('0x10')
        rhs.last.fill('1')
        page.locator('#mat-solve').click()
        assert 'decimal or scientific notation' in page.locator('#mat-result').inner_text()
        assert not page.locator('#mat-send').is_enabled()
        rhs.first.fill('2e0')
        page.locator('#mat-solve').click()
        assert 'solve:' in page.locator('#mat-result').inner_text()
        assert page.locator('#mat-send').is_enabled()
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-solve').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: decimal/scientific Ax=b RHS, prefix rejection, UI recovery and mobile')

if __name__=='__main__': main()
