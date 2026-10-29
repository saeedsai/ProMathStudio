"""Matrix display must retain tiny nonzero scientific values instead of showing zero."""
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
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#mat-rows').select_option('2')
        page.locator('#mat-cols').select_option('2')
        for index,value in enumerate(('1e-14','0','0','1')):
            page.locator('#mat-grid input').nth(index).fill(value)
        page.locator('#mat-transpose').click()
        output=page.locator('#mat-result').inner_text().lower()
        assert '1e-14' in output,output
        assert page.locator('#mat-send').is_enabled()
        for width in (390,768,1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#mat-transpose').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: matrix tiny nonzero numerical display and responsive UI')

if __name__=='__main__': main()
