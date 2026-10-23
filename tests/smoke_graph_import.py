"""Browser test of CSV/JSON graph import, 2D/3D mapping and project restore."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page=browser.new_page(accept_downloads=True,viewport={'width':1366,'height':900})
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        page.locator('[data-workspace="graph"]').click()
        page.locator('#graph-data-file').set_input_files({
            'name':'data.csv','mimeType':'text/csv',
            'buffer':b'time,value,note\n0,3,"a,b"\n1,4,ok\n2,5,last\n'})
        page.wait_for_function('()=>MathStudio.graphData.hasData()')
        assert page.evaluate('MathStudio.graphData.getState().points.length')==3
        assert page.locator('#graph-data-preview td').nth(2).inner_text()=='a,b'
        page.locator('#graph-data-fit').click()
        assert float(page.locator('#graph-xmax').input_value())>2
        page.locator('#graph-input').fill('')
        page.locator('#graph-plot').click()
        assert page.locator('#graph-legend .graph-legend-line').count()==1
        page.locator('[data-graph-mode="3d"]').click()
        data={'data':[{'x':x,'y':y,'z':x*y}
             for x in [-1,0,1] for y in [-1,0,1]]}
        page.locator('#graph-data-file').set_input_files({
            'name':'grid.json','mimeType':'application/json',
            'buffer':json.dumps(data).encode()})
        page.wait_for_function('()=>MathStudio.graphData.getState()?.name==="grid.json"')
        page.locator('#graph-data-style').select_option('grid')
        page.locator('#graph-data-fit').click()
        assert page.evaluate('MathStudio.graphData.getState().points.length')==9
        assert not page.locator('#graph-status').evaluate('(e)=>e.classList.contains("error")')
        with page.expect_download() as download:
            page.locator('#hub-export-project').click()
        project=json.loads(Path(download.value.path()).read_text(encoding='utf-8'))
        assert project['graph']['dataset']['name']=='grid.json'
        page.locator('#graph-data-clear').click()
        assert not page.evaluate('MathStudio.graphData.hasData()')
        page.evaluate('window.confirm=()=>true')
        page.locator('#hub-project-file').set_input_files({
            'name':'project.json','mimeType':'application/json',
            'buffer':json.dumps(project).encode()})
        page.wait_for_function('()=>MathStudio.graphData.hasData()')
        assert page.evaluate('MathStudio.graphData.getState().points.length')==9
        page.locator('#graph-data-file').set_input_files({
            'name':'bad.csv','mimeType':'text/csv','buffer':b'x,y\n0,1\n1\n'})
        assert 'Import failed' in page.locator('#graph-data-status').inner_text()
        assert errors==[],errors
        browser.close()
    print('PASS: CSV, JSON, column mapping, 2D and 3D, project restore, errors')

if __name__=='__main__':main()
