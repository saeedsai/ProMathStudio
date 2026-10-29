"""Matrix decimal-only input: browser API, UI errors, recovery, mobile."""
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
        for bad in ('0x10','0b10','0o10','Infinity','NaN','1_000','1e','--2'):
            message=page.evaluate("(x)=>{try{MathStudio.matrixTools.validate([[x,'0'],['0','1']]);return ''}catch(e){return e.message}}",bad)
            assert 'decimal or scientific notation' in message,(bad,message)
        for good,expected in (('1e-6',1e-6),('-0.5',-.5),('+2',2),('.25',.25),('2.',2),(' 3E+2 ',300)):
            value=page.evaluate("(x)=>MathStudio.matrixTools.validate([[x,'0'],['0','1']])[0][0]",good)
            assert value==expected,(good,value)
        assert page.evaluate("MathStudio.matrixTools.validate([[2,0],[0,1]])")==[[2,0],[0,1]]
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('2')
        page.locator('#mat-cols').select_option('2')
        fields=page.locator('#mat-grid input')
        for i,v in enumerate(('0x10','0','0','1')):
            fields.nth(i).fill(v)
        page.locator('#mat-pseudoinverse').click()
        assert 'decimal or scientific notation' in page.locator('#mat-result').inner_text()
        assert not page.locator('#mat-send').is_enabled()
        fields.nth(0).fill('1e-6')
        page.locator('#mat-pseudoinverse').click()
        output=page.locator('#mat-result').inner_text()
        assert 'Numerical rank: 2' in output,output
        assert page.locator('#mat-send').is_enabled()
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-pseudoinverse').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: decimal/scientific matrix input, prefix rejection, recovery and responsive UI')

if __name__=='__main__':
    main()
