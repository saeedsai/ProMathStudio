"""Browser regression for Data Tables and integration with 2D/3D graphs."""
from pathlib import Path
import json, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(accept_downloads=True,viewport={'width':1350,'height':920})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  page.locator('[data-workspace="data"]').click()
  assert page.locator('#data-panel').is_visible()
  page.evaluate("""() => {MathStudio.dataTables.active.rows[0]=['3','2','=A1*B1'];}""")
  assert page.locator('#dt-sheet tbody tr:first-child th.dt-rownum').inner_text()=='1'
  assert page.evaluate('MathStudio.dataTables.calculate()[0][2]')==6
  assert page.evaluate('MathStudio.dataTables.formula("SUM(A1:A3)+IF(A1>2,5,0)","Data1")')==11
  page.evaluate("""() => {MathStudio.dataTables.active.rows[0][2]='=C1';}""")
  assert page.evaluate('MathStudio.dataTables.calculate()[0][2]')=='#CYCLE'
  page.locator('#dt-import').set_input_files({'name':'orders.csv','mimeType':'text/csv','buffer':b'id,sku,amount\n1,A,10\n2,B,25\n3,C,15\n'})
  page.wait_for_function("() => !document.querySelector('#dt-import-preview').hidden")
  page.locator('#dt-import-confirm').evaluate('(e) => e.click()')
  page.wait_for_function('()=>MathStudio.dataTables.tables.some(t=>t.name==="orders")')
  page.locator('#dt-import').set_input_files({'name':'products.json','mimeType':'application/json','buffer':json.dumps([{'id':1,'name':'alpha','price':2},{'id':2,'name':'beta','price':5}]).encode()})
  page.wait_for_function("() => !document.querySelector('#dt-import-preview').hidden")
  page.locator('#dt-import-confirm').evaluate('(e) => e.click()')
  page.wait_for_function('()=>MathStudio.dataTables.tables.some(t=>t.name==="products")')
  # The Combine menu contains native selects. Set their values through DOM
  # without relying on Chromium rendering of the OS-native dropdown popup.
  menu=page.locator('#data-menu-navigation > details').nth(2)
  menu.evaluate('(e)=>e.open=true')
  assert menu.evaluate('(e)=>e.open')
  page.evaluate("""() => {
    const select=(id,label)=>{
      const el=document.getElementById(id);
      const option=[...el.options].find(o=>o.textContent.trim()===label);
      if(!option)throw Error('Missing '+label+' in '+id);
      el.value=option.value;
      el.dispatchEvent(new Event('change',{bubbles:true}));
    };
    select('dt-left','orders');select('dt-right','products');
  }""")
  page.evaluate("""() => {document.getElementById('dt-op').value='left';document.getElementById('dt-run').click()}""")
  assert len(page.evaluate('MathStudio.dataTables.tables.at(-1).rows'))==3
  page.evaluate("""() => {document.getElementById('dt-op').value='unionall';document.getElementById('dt-run').click()}""")
  assert page.evaluate('MathStudio.dataTables.tables.at(-1).rows.length')==5
  page.locator('[data-workspace="graph"]').click()
  page.locator('#workspace-task-select').select_option('table')
  assert page.locator('#ui-graph-table').evaluate('(e)=>e.open')
  page.locator('#dt-graph-table').select_option(label='orders')
  page.locator('#dt-chart-type').select_option('bar')
  page.locator('#dt-graph-x').select_option('1')
  page.locator('#dt-graph-y').select_option('2')
  page.locator('#dt-plot-table').click();assert page.locator('#dt-graph-chart').is_visible()
  page.locator('#dt-chart-type').select_option('pie')
  page.locator('#dt-plot-table').click();assert page.locator('#dt-graph-chart').is_visible()
  page.locator('#dt-chart-type').select_option('scatter')
  page.locator('#dt-graph-x').select_option('0')
  page.locator('#dt-graph-y').select_option('2')
  page.locator('#dt-plot-table').click()
  assert page.evaluate('MathStudio.graphData.getState().points.length')==3
  with page.expect_download() as d:page.locator('#hub-export-project').click()
  project=json.loads(Path(d.value.path()).read_text())
  assert len(project['tables']['tables'])>=5
  page.evaluate('window.confirm=()=>true')
  page.locator('#hub-project-file').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':json.dumps(project).encode()})
  page.wait_for_function('()=>MathStudio.dataTables.tables.length>=5')
  assert 'Saeedmsalehi1990@gmail.com' in page.locator('#about-panel').text_content()
  assert not errors,errors
  browser.close()
 print('PASS Data Tables formulas, join, union, CSV/JSON, bar, pie, graph, backup')
if __name__=='__main__':main()
