"""Control-theory browser integration: reference values, validation, canvas and mobile."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':850})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  page.locator('[data-workspace="graph"]').click()
  panel=page.locator('#control-theory-toolbox')
  panel.evaluate('(el)=>el.open=true')
  assert panel.is_visible()
  page.locator('#ct-num').fill('1')
  page.locator('#ct-den').fill('1, 1')
  page.locator('#ct-gain').fill('1')
  for mode in ('bode','nyquist','root','routh','feedback'):
   page.locator('#ct-mode').select_option(mode)
   page.locator('#ct-run').click()
   assert 'completed' in page.locator('#ct-status').inner_text(),mode
   assert page.locator('#ct-output').inner_text().strip(),mode
   assert page.evaluate('document.getElementById("ct-canvas").getContext("2d").getImageData(450,195,1,1).data[3]')==255,mode
  assert 'Characteristic polynomial: 1, 2' in page.locator('#ct-output').inner_text()
  page.locator('#ct-den').fill('0, 2')
  page.locator('#ct-run').click()
  assert 'first coefficient nonzero' in page.locator('#ct-status').inner_text()
  for width in (390,768):
   page.set_viewport_size({'width':width,'height':780})
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),width
   assert panel.is_visible()
  assert not errors,errors
  browser.close()
if __name__=='__main__':main()
