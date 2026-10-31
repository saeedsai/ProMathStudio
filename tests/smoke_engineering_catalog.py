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
  assert len(catalog['disciplines'])==9,catalog
  assert len(set(catalog['ids']))==len(catalog['ids'])
  assert 'matrix.solve.real.small' in catalog['available']
  assert page.locator('#eng-results article').count()==len(catalog['ids'])
  for discipline, tool_id in [('gnss','gnss.positioning.least.squares'),
                              ('signals','signals.spectral.analysis'),
                              ('control','control.frequency.response')]:
   page.locator('#eng-discipline').select_option(discipline)
   page.locator('#eng-search').fill(tool_id.split('.')[0])
   card=page.locator('#eng-results article[data-tool-id="'+tool_id+'"]')
   assert card.count()==1,tool_id
   assert card.locator('button').count()==0,'Planned feature must not open a fake tool'
   assert 'planned' in card.inner_text().lower()
  page.locator('#eng-search').fill('')
  # Readable discipline labels are searchable, not just terse IDs or tool titles.
  page.locator('#eng-discipline').select_option('')
  page.locator('#eng-search').fill('Aerospace engineering')
  assert page.locator('#eng-results article').count()>0
  assert page.locator('#eng-results article[data-tool-id="matrix.solve.real.small"]').count()==1
  # Multiword search matches all tokens independently of their order.
  page.locator('#eng-search').fill('equilibrium control')
  assert page.locator('#eng-results article[data-tool-id="control.equilibrium.real.small"]').count()==1
  page.locator('#eng-search').fill('control orbit')
  assert page.locator('#eng-results article').count()==0
  page.locator('#eng-search').fill('GNSS positioning')
  assert page.locator('#eng-results article[data-tool-id="gnss.positioning.least.squares"]').count()==1
  assert page.locator('#eng-results article button').count()==0
  page.locator('#eng-search').fill('')
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
  page.locator('#eng-results article[data-tool-id="control.equilibrium.real.small"] button').click()
  assert page.locator('#graph-panel').is_visible()
  page.wait_for_function("document.querySelector('#ct-equilibrium').open")
  assert page.locator('#control-theory-toolbox').evaluate('(e)=>e.open')
  # Existing numerical tools route to their real, visible controls.
  for tool_id, selector in [('signals.fft.1d', '#fft-run'), ('numerical.root.brent', '#brent-run'),
                            ('matrix.eigen.symmetric.small', '#matrix-tools')]:
   tab.click()
   page.locator('#eng-discipline').select_option('')
   page.locator('#eng-search').fill(tool_id)
   card = page.locator('#eng-results article[data-tool-id="' + tool_id + '"]')
   assert card.count() == 1 and card.locator('button').count() == 1, tool_id
   card.locator('button').click()
   page.wait_for_function("(s) => { const e = document.querySelector(s); return e && e.getClientRects().length > 0; }", arg=selector)
  # Existing stability and transient tools route to their real panels (no duplicate solver or fake action).
  for tool_id, panel in [('control.stability.symmetric', 'ct-equilibrium'),
                         ('control.transient.two.state', 'ct-eq-transient')]:
   tab.click()
   page.locator('#eng-discipline').select_option('control')
   page.locator('#eng-search').fill('control')
   card = page.locator('#eng-results article[data-tool-id="' + tool_id + '"]')
   assert card.count() == 1 and 'planned' not in card.inner_text().lower()[:40], tool_id
   page.evaluate("()=>{const d=document.getElementById('control-theory-toolbox');d.open=false;"
                 "for(const id of ['ct-equilibrium','ct-eq-transient'])document.getElementById(id).open=false}")
   card.locator('button').click()
   page.wait_for_function("document.getElementById('%s').open && document.getElementById('ct-equilibrium').open" % panel)
   assert page.locator('#graph-panel').is_visible()
   assert page.evaluate("document.activeElement && document.getElementById('%s').contains(document.activeElement)" % panel)
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
 print('PASS Engineering Toolbox search, nine disciplines, honest statuses and routes')
if __name__=='__main__':main()
