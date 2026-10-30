"""Engineering catalog discipline, search, status, route and mobile regressions."""
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
  tab=page.locator('[data-workspace="engineering"]')
  assert tab.count()==1
  tab.click()
  assert page.locator('#engineering-panel').is_visible()
  catalog=page.evaluate("""() => {
   const c=MathStudio.engineeringCatalog;
   return {ids:c.tools.map(t=>t.id),disciplines:c.disciplines.map(d=>d.id),
    available:c.tools.filter(t=>t.status==='available').map(t=>t.id)}
  }""")
  assert len(catalog['disciplines'])==6,catalog
  assert len(set(catalog['ids']))==len(catalog['ids'])
  assert 'matrix.solve.real.small' in catalog['available']
  assert page.locator('#eng-results article').count()==len(catalog['ids'])
  page.locator('#eng-discipline').select_option('fluids')
  page.locator('#eng-search').fill('pipe')
  assert page.locator('#eng-results article').count()==1
  planned=page.locator('#eng-results article')
  assert planned.get_attribute('data-tool-id')=='fluids.pipe.network'
  assert planned.locator('button').count()==0
  assert 'planned' in planned.inner_text().lower()
  page.locator('#eng-search').fill('no-such-tool')
  assert 'No matching tools' in page.locator('#eng-results').inner_text()
  page.locator('#eng-search').fill('matrix')
  page.locator('#calc-input').evaluate('(e)=>e.value="7+5"')
  page.locator('#eng-results article button').click()
  assert page.locator('#calculator-panel').is_visible()
  page.wait_for_function("document.querySelector('#matrix-tools').open")
  assert page.locator('#calc-input').input_value()=='7+5'
  tab.click()
  page.locator('#eng-discipline').select_option('electrical')
  page.locator('#eng-search').fill('control')
  page.locator('#eng-results article button').click()
  assert page.locator('#graph-panel').is_visible()
  page.wait_for_function("document.querySelector('#ct-equilibrium').open")
  assert page.locator('#control-theory-toolbox').evaluate('(e)=>e.open')
  tab.click()
  page.locator('#eng-discipline').select_option('physics')
  page.locator('#eng-search').fill('ode')
  page.locator('#eng-results article button').click()
  page.wait_for_function("document.querySelector('#ode-details').open")
  assert page.locator('#symbolic-panel').is_visible()
  tab.click()
  for width in (390,768,1280):
   page.set_viewport_size({'width':width,'height':850})
   assert page.locator('#engineering-panel').is_visible()
   assert page.locator('.workspace-bar').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),width
   assert page.locator('#engineering-panel').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),width
  # A session restored to Engineering must activate the dynamically appended tab.
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  page.route('http://promath.test/',lambda route:route.fulfill(status=200,content_type='text/html',body=html))
  page.goto('http://promath.test/',wait_until='load')
  page.evaluate("sessionStorage.setItem('mathstudio-mode','engineering')")
  page.reload(wait_until='load')
  assert page.locator('[data-workspace="engineering"]').get_attribute('aria-current')=='page'
  assert page.locator('#engineering-panel').is_visible()
  assert not errors,errors
  browser.close()
 print('PASS Engineering Toolbox search, six disciplines, honest statuses and routes')
if __name__=='__main__':main()
