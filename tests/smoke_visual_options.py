"""Visual styling, spreadsheet zoom and calculator number formatting smoke tests."""
from pathlib import Path
import json,os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1360,'height':900},accept_downloads=True)
  errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  page.locator('[data-workspace="calculator"]').click()
  page.locator('#calc-number-format').select_option('scientific')
  page.locator('#calc-input').fill('123456789.125')
  page.locator('#calc-execute').click()
  assert 'e+8' in page.locator('#calc-result-plain').inner_text()
  page.locator('#calc-number-format').select_option('engineering')
  page.locator('#calc-execute').click()
  assert 'e+6' in page.locator('#calc-result-plain').inner_text()
  page.locator('#calc-number-format').select_option('auto')
  page.locator('#calc-input').fill('1/2');page.locator('#calc-execute').click()
  assert page.locator('#calc-result-plain').inner_text()=='= 0.5'
  page.locator('[data-workspace="graph"]').click()
  page.locator('#graph-appearance').evaluate('(e)=>e.open=true')
  page.locator('#plot-palette').select_option('bright')
  page.locator('#plot-line-style').select_option('dashed')
  page.locator('#plot-line-width').select_option('5')
  page.locator('#graph-input').fill('y=x^2')
  page.locator('#graph-plot').click()
  assert page.evaluate('MathStudio.graphAppearance.color(0)')=='#ee394c'
  assert page.evaluate('MathStudio.graphAppearance.width()')==5
  assert page.evaluate('MathStudio.graphAppearance.dash()')==[12,8]
  with page.expect_download() as download:page.locator('#hub-export-project').click()
  project=json.loads(Path(download.value.path()).read_text())
  assert project['graph']['appearance']['palette']=='bright'
  assert project['calculator']['format']=='auto'
  page.locator('[data-workspace="data"]').click()
  page.locator('#table-zoom-in').click()
  assert page.locator('#table-zoom-value').inner_text()=='110%'
  assert page.evaluate('MathStudio.tableZoom.value()')==110
  page.locator('#table-zoom').fill('150')
  assert page.locator('#table-zoom-value').inner_text()=='150%'
  page.locator('#table-zoom-reset').click()
  assert page.locator('#table-zoom-value').inner_text()=='100%'
  assert not errors,errors
  browser.close()
 print('PASS appearance, chart palettes, number formats, project state, table zoom')
if __name__=='__main__': main()
