"""Browser regression for compact Calculator and Equation Editor actions."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':850})
  errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  assert page.locator('#add-btn').is_visible()
  assert not page.locator('#copy-latex').is_visible()
  page.locator('#equation-input').fill('x^2+1')
  summary=page.locator('#ui-editor-export-actions > summary')
  summary.focus()
  page.keyboard.press('Enter')
  assert page.locator('#ui-editor-export-actions').evaluate('(e)=>e.open')
  for selector in ('#copy-latex','#copy-word','#copy-image','#export-word'):
   assert page.locator(selector).is_visible(),selector
   assert page.locator(selector).count()==1
  page.locator('#copy-latex').click()
  with page.expect_download() as download:
   page.locator('#export-word').click()
  assert download.value.suggested_filename.endswith('.docx')
  summary.click()
  assert not page.locator('#copy-word').is_visible()
  assert page.locator('#equation-input').input_value()=='x^2+1'
  page.locator('#add-btn').click()
  assert page.locator('#counter').inner_text()=='(1)'
  page.locator('[data-workspace="calculator"]').click()
  assert page.locator('#calc-execute').is_visible()
  assert page.locator('#calc-use-editor').is_visible()
  assert not page.locator('#calc-copy').is_visible()
  page.locator('#calc-input').fill('2+3')
  page.locator('#calc-execute').click()
  assert page.locator('#calc-result-plain').inner_text()=='= 5'
  page.locator('#ui-calc-more-actions > summary').click()
  for selector in ('#calc-copy','#hub-calc-result','[data-forward="calculator"][data-destination="solver"]','[data-forward="calculator"][data-destination="graph2d"]'):
   assert page.locator(selector).is_visible(),selector
   assert page.locator(selector).count()==1
  page.locator('#calc-copy').click()
  message=page.locator('#calc-message').inner_text().lower()
  assert 'copied' in message or 'clipboard permissions' in message,message
  page.locator('#hub-calc-result').click()
  assert page.locator('#hub-expression').input_value()=='5'
  page.locator('#ui-calc-more-actions > summary').click()
  assert not page.locator('#calc-copy').is_visible()
  assert page.locator('#calc-input').input_value()=='2+3'
  for width in (390,768,1280):
   page.set_viewport_size({'width':width,'height':850})
   assert page.locator('#calc-execute').is_visible()
   assert page.locator('#ui-calc-more-actions > summary').is_visible()
   assert page.locator('#ui-calc-more-actions').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),width
  assert not errors,errors
  browser.close()
 print('PASS grouped Calculator/Editor actions, keyboard, Word download, result routing, mobile')

if __name__=='__main__':main()
