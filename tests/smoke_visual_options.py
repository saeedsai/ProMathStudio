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
  assert page.evaluate('MathStudio.graphAppearance.color(0)')=='#536be8'
  assert page.locator('#plot-series-colors input[type=color]').count()==1
  page.locator('#plot-color').fill('#ff8844')
  assert page.evaluate('MathStudio.graphAppearance.color(0)')=='#ff8844'
  page.locator('#graph-input').fill('y=x^2\ny=sin(x)\ny=cos(x)')
  page.locator('#graph-plot').click()
  assert page.locator('#plot-series-colors input[type=color]').count()==3
  colors=page.evaluate('[0,1,2].map(i=>MathStudio.graphAppearance.color(i))')
  assert colors[0]=='#ff8844' and len(set(colors))==3,colors
  page.locator('#plot-series-colors input[data-series="1"]').fill('#123abc')
  assert page.evaluate('MathStudio.graphAppearance.color(1)')=='#123abc'
  page.locator('#plot-palette').select_option('custom')
  assert len(set(page.evaluate('[0,1,2].map(i=>MathStudio.graphAppearance.color(i))')))==3
  page.locator('#plot-series-colors select[aria-label="Line style for y=sin(x)"]').select_option('dotted')
  page.locator('#plot-series-colors select[aria-label="Line weight for y=cos(x)"]').select_option('1.5')
  assert page.evaluate('MathStudio.graphAppearance.state().seriesStyles["1"].line')=='dotted'
  assert page.evaluate('MathStudio.graphAppearance.state().seriesStyles["2"].width')=='1.5'
  assert page.evaluate('MathStudio.graphAppearance.width()')==5
  assert page.evaluate('MathStudio.graphAppearance.dash()')==[12,8]
  with page.expect_download() as download:page.locator('#hub-export-project').click()
  project=json.loads(Path(download.value.path()).read_text())
  assert project['graph']['appearance']['palette']=='custom'
  assert project['graph']['appearance']['seriesStyles']['1']['line']=='dotted'
  assert project['calculator']['format']=='auto'
  page.locator('[data-workspace="data"]').click()
  page.locator('#table-zoom-in').click()
  assert page.locator('#table-zoom-value').inner_text()=='110%'
  assert page.evaluate('MathStudio.tableZoom.value()')==110
  page.locator('#table-zoom').fill('150')
  assert page.locator('#table-zoom-value').inner_text()=='150%'
  page.locator('#table-zoom-reset').click()
  assert page.locator('#table-zoom-value').inner_text()=='100%'
  # Named custom functions are available across numeric workspaces.
  page.locator('#custom-function-panel').evaluate('(e)=>e.open=true')
  page.locator('#cf-name').fill('myfun')
  page.locator('#cf-params').fill('x')
  page.locator('#cf-body').fill('x^2+1')
  page.locator('#cf-save').click()
  assert page.evaluate('MathStudio.customFunctions.evaluate("myfun",[3])')==10
  assert page.evaluate('MathStudio.dataTables.formula("myfun(3)","Data1")')==10
  page.locator('#cf-name').fill('pyfun')
  page.locator('#cf-type').select_option('python')
  page.locator('#cf-body').fill('def pyfun(x): return math.sin(x) + x**2')
  page.locator('#cf-save').click()
  assert abs(page.evaluate('MathStudio.customFunctions.evaluate("pyfun",[2])')-(4+__import__('math').sin(2)))<1e-8
  # Overlay multiple column mappings and a second table without replacing existing data.
  page.evaluate("""() => {
    const plot=MathStudio.graphData;
    plot.clear(false);
    plot.addTable({headers:['x','y','z','w'],rows:[[1,2,3,4],[2,4,6,8]]},'Table1',{x:0,y:1,mode:'2d',style:'points'});
    plot.addTable({headers:['x','y','z','w'],rows:[[1,2,3,4],[2,4,6,8]]},'Table1',{x:0,y:2,mode:'2d',style:'line'});
    plot.addTable({headers:['time','value'],rows:[[1,5],[2,7]]},'Table2',{x:0,y:1,mode:'2d',style:'points'});
  }""")
  assert len(page.evaluate('MathStudio.graphData.legend()'))==4
  assert len(page.evaluate('MathStudio.graphData.exportState().extra'))==3
  assert not errors,errors
  browser.close()
 print('PASS appearance, chart palettes, number formats, project state, table zoom')
if __name__=='__main__': main()
