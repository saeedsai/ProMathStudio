"""Reduced task buttons in each workspace, with all tools available."""
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
  routes={'editor':['basic','examples','notebook','python','numerical','ode','assumptions'],'calculator':['basic','matrix','variables','precision','settings','history'],'graph':['basic','table','axes','appearance'],'data':['basic','filter','combine','files','python']}
  picker=page.locator('#workspace-task-select')
  for workspace,expected in routes.items():
   page.locator('[data-workspace="'+workspace+'"]').click()
   assert picker.is_visible(),workspace
   assert page.locator('#workspace-task-guide button').count()==0,workspace
   actual=picker.locator('option').evaluate_all('(xs)=>xs.map(e=>e.value)')
   assert actual==expected,(workspace,actual)
   assert picker.input_value()=='basic',workspace
  assert picker.get_attribute('aria-describedby')=='task-description'
  page.locator('[data-workspace="calculator"]').click()
  picker.select_option('precision')
  assert page.locator('#precision-details').evaluate('(e)=>e.open')
  assert page.locator('#precision-run').is_visible()
  picker.select_option('matrix')
  assert page.locator('#matrix-tools').evaluate('(e)=>e.open')
  page.locator('[data-workspace="editor"]').click()
  picker.select_option('ode')
  assert page.locator('#ode-details').evaluate('(e)=>e.open')
  assert page.locator('#symbolic-panel .cas-wrap').is_hidden()
  picker.select_option('basic')
  assert page.locator('#symbolic-panel .cas-wrap').is_visible()
  page.locator('[data-workspace="graph"]').click()
  picker.select_option('appearance')
  assert page.locator('#graph-appearance').evaluate('(e)=>e.open')
  assert page.locator('#graph-input').is_visible()
  page.locator('[data-workspace="data"]').click()
  picker.select_option('files')
  assert page.locator('#data-menu-navigation > details:nth-child(4)').evaluate('(e)=>e.open')
  picker.select_option('python')
  assert page.locator('#data-menu-navigation > details:nth-child(5)').evaluate('(e)=>e.open')
  page.locator('[data-workspace="editor"]').click()
  picker.select_option('python')
  assert page.locator('#ui-editor-python').evaluate('(e)=>e.open')
  assert page.locator('#add-btn').is_visible()
  page.locator('[data-workspace="calculator"]').click()
  assert picker.input_value()=='matrix'
  # A newly selected tool closes the previous tool form, without losing drafts.
  page.locator('[data-workspace="calculator"]').click()
  picker.select_option('precision')
  picker.select_option('matrix')
  assert not page.locator('#precision-details').evaluate('(e)=>e.open')
  picker.select_option('basic')
  assert not page.locator('#matrix-tools').evaluate('(e)=>e.open')
  page.locator('[data-workspace="graph"]').click()
  graph_input=page.locator('#graph-input')
  graph_input.fill('y = x^2')
  picker.select_option('axes')
  assert page.locator('#ui-graph-axes').evaluate('(e)=>e.open')
  picker.select_option('appearance')
  assert not page.locator('#ui-graph-axes').evaluate('(e)=>e.open')
  picker.select_option('basic')
  assert not page.locator('#graph-appearance').evaluate('(e)=>e.open')
  assert graph_input.input_value()=='y = x^2'
  page.locator('[data-workspace="data"]').click()
  picker.select_option('filter')
  picker.select_option('combine')
  assert not page.locator('#data-menu-navigation > details:nth-child(2)').evaluate('(e)=>e.open')
  picker.select_option('basic')
  assert not page.locator('#data-menu-navigation > details:nth-child(3)').evaluate('(e)=>e.open')
  for width in (390,768,1280):
   page.set_viewport_size({'width':width,'height':850})
   assert picker.is_visible()
   size=page.locator('#workspace-task-guide').evaluate('(e)=>[e.scrollWidth,e.clientWidth]')
   assert size[0]<=size[1]+1,size
  assert not errors,errors
  browser.close()
 print('PASS compact workspace tasks, routing and desktop/mobile')
if __name__=='__main__':main()
