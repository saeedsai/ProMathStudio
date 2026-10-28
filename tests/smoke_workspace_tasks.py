"""Task-first, progressive workspace UI regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':850})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  assert page.locator('#workspace-task-guide').is_visible()
  assert page.locator('#workspace-task-select').input_value()=='basic'
  assert page.locator('#workspace-task-guide button').count()==0
  page.locator('#workspace-task-select').select_option('python')
  assert page.locator('#ui-editor-python').evaluate('(e)=>e.open')
  page.locator('#equation-input').fill('x^2+1')
  assert page.locator('#preview math').count()>0
  page.locator('[data-workspace="calculator"]').click()
  assert not page.locator('#ui-calc-settings').evaluate('(e)=>e.open')
  page.locator('#workspace-task-select').select_option('precision')
  assert page.locator('#precision-details').evaluate('(e)=>e.open')
  page.locator('#workspace-task-select').select_option('settings')
  assert page.locator('#ui-calc-settings').evaluate('(e)=>e.open')
  page.locator('#calc-number-format').select_option('scientific')
  page.locator('#calc-input').fill('1234');page.locator('#calc-execute').click()
  assert 'e+' in page.locator('#calc-result-plain').inner_text()
  page.locator('#workspace-task-select').select_option('history')
  assert page.locator('#ui-calc-history').evaluate('(e)=>e.open')
  page.locator('[data-workspace="editor"]').click()
  page.locator('#workspace-task-select').select_option('numerical')
  assert page.locator('#num-details').evaluate('(e)=>e.open')
  assert page.locator('#symbolic-panel .cas-wrap').is_hidden() and page.locator('#num-details').is_visible()
  page.locator('#workspace-task-select').select_option('basic')
  assert page.locator('#symbolic-panel .cas-wrap').is_visible()
  page.locator('#workspace-task-select').select_option('assumptions')
  assert page.locator('#ui-solver-assumptions').evaluate('(e)=>e.open')
  page.locator('[data-workspace="graph"]').click()
  assert not page.locator('#ui-graph-table').evaluate('(e)=>e.open')
  page.locator('#workspace-task-select').select_option('table')
  assert page.locator('#ui-graph-table').evaluate('(e)=>e.open')
  page.locator('#workspace-task-select').select_option('axes')
  assert page.locator('#ui-graph-axes').evaluate('(e)=>e.open')
  page.locator('[data-workspace="data"]').click()
  assert page.locator('#dt-sheet').is_visible()
  page.locator('#workspace-task-select').select_option('combine')
  assert page.locator('#data-menu-navigation > details:nth-child(3)').evaluate('(e)=>e.open')
  for width in (390,1280):
   page.set_viewport_size({'width':width,'height':850})
   assert page.locator('#workspace-task-guide').is_visible()
   assert page.locator('#workspace-task-select option').count()==5
   assert page.locator('#workspace-task-guide button').count()==0
  assert not errors,errors
  browser.close()
 print('PASS task-first workspace navigation, progressive disclosure, desktop/mobile')
if __name__=='__main__':main()
