"""ProMathStudio numerical + Data Tables / Python integration QA.
Core methods run offline. Actual CDN fetch of Pyodide/pandas requires live-browser follow-up.
"""
from pathlib import Path
import json, math, os, subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]


def run():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert '<script id="promath-numerical-data">' in html
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':860})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='load')
        root=page.evaluate("MathStudio.numerical.scalarRoots('sin(x)-x/2=0','x',-4,4).roots")
        assert len(root)==3 and abs(root[0]+1.895494267)<1e-5 and abs(root[1])<1e-6 and abs(root[2]-1.895494267)<1e-5,root
        tangent=page.evaluate("MathStudio.numerical.scalarRoots('(x-1)^2=0','x',-2,3).roots")
        assert len(tangent)==1 and abs(tangent[0]-1)<1e-5,tangent
        system=page.evaluate("MathStudio.numerical.systemRoots('x^2+y^2=5; x-y=1','x,y','1,1')")
        assert system['converged'] and abs(system['values'][0]-2)<1e-8 and abs(system['values'][1]-1)<1e-8
        poisson=page.evaluate("MathStudio.numerical.poisson1D({nx:60,a:0,b:1,source:'pi^2*sin(pi*x)'})")
        assert max(abs(z-math.sin(math.pi*x)) for x,z in poisson['rows'])<0.0003
        heat=page.evaluate("MathStudio.numerical.heat1D({nx:40,nt:200,endTime:0.1,alpha:0.1,initial:'sin(pi*x)'})")
        mid=min(heat['rows'],key=lambda row: abs(row[0]-.5)+abs(row[1]-.1))
        assert abs(mid[2]-math.exp(-.1*math.pi**2*.1))<.002,mid
        assert abs(heat['cfl']-.08)<1e-6
        assert page.evaluate("()=>{try{MathStudio.numerical.heat1D({nx:100,nt:1,alpha:1,endTime:1});return false;}catch(e){return /Unstable/.test(e.message)}}")
        for expr,expected in [('diff(sin(x),x,0)',1),('int(x^2,x,0,3)',9),('sum(k^2,k,1,10)',385),('prod(k,k,1,5)',120)]:
            actual=page.evaluate('(s)=>MathStudio.advanced.numeric(s).re',expr)
            assert abs(actual-expected)<1e-6,(expr,actual,expected)
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#calc-variable-panel').evaluate('(e)=>e.open=true')
        page.locator('#calc-variables').fill('x=2\ny=3')
        page.locator('#calc-variable-apply').click()
        page.locator('#calc-input').fill('x^2+y^2')
        page.locator('#calc-execute').click()
        assert '= 13' in page.locator('#calc-result-plain').inner_text()
        page.locator('[data-workspace="solver"]').click()
        assert page.locator('#numerical-panel').is_visible()
        page.locator('#num-open').click()
        page.locator('#num-method').select_option('poisson')
        page.locator('#num-expression').fill('pi^2*sin(pi*x)')
        page.locator('#num-start').fill('0')
        page.locator('#num-end').fill('1')
        page.locator('#num-run').click()
        assert 'finite differences' in page.locator('#num-output').inner_text()
        before=page.evaluate('MathStudio.dataTables.tables.length')
        page.locator('#num-to-table').click()
        assert page.locator('#data-panel').is_visible()
        assert page.evaluate('MathStudio.dataTables.tables.length')==before+1
        assert page.locator('#dt-sheet tbody tr').count()>0
        # Data Tables is primarily the grid, and actions are in submenus.
        assert page.locator('#data-menu-navigation > details').count()==5
        assert page.locator('#data-menu-navigation > details[open]').count()==0
        assert page.locator('#dt-sheet').is_visible()
        page.locator('#data-menu-navigation > details').nth(1).evaluate('(e)=>e.open=true')
        page.locator('#dt-filter-column').select_option('0')
        page.locator('#dt-filter-op').select_option('gt')
        page.locator('#dt-filter-value').fill('0.5')
        page.locator('#dt-filter-apply').click()
        filtered=page.evaluate('MathStudio.dataTools.getFilteredRows()')
        visible=page.locator('#dt-sheet tbody tr').count()
        assert 0<filtered<visible,(filtered,visible)
        page.locator('#dt-filter-reset').click()
        assert page.evaluate('MathStudio.dataTools.getFilteredRows()')==visible
        # Python worker creation is explicit. Mock the worker only to inspect safely constructed code.
        page.locator('#data-menu-navigation > details').nth(4).evaluate('(e)=>e.open=true')
        worker_src=page.evaluate('''async()=>{window.__py_url='';window.Worker=class{constructor(url){window.__py_url=url;}postMessage(){}terminate(){}};document.querySelector('#dt-python-run').click();return await(await fetch(window.__py_url)).text();}''')
        assert page.evaluate('(src)=>{try{new Function(src);return true}catch{return false}}',worker_src)
        py_code=page.evaluate('''async src=>{
          let code='';const dummy={postMessage:()=>{}};
          const runtime={globals:{set:()=>{}},loadPackage:async()=>{},runPythonAsync:async value=>{code=value;return JSON.stringify({stdout:'ok',tables:[]})}};
          const make=new Function('loadPyodide','importScripts','self',src+';return self.onmessage;');
          const handler=make(async()=>runtime,()=>{},dummy);await handler({data:{code:'result=None',workbook:[]}});return code;
        }''',worker_src)
        compile(py_code,'embedded-data-worker.py','exec')
        assert 'pd.to_numeric' in py_code
        page.locator('#dt-python-stop').click()
        page.set_viewport_size({'width':390,'height':844})
        assert page.locator('#dt-sheet').is_visible()
        assert page.locator('#data-menu-navigation').is_visible()
        assert errors==[],errors
        browser.close()
    print('PASS: numerical roots and systems, 1D heat/Poisson, numerical calculus, data menus/filter, Python worker build')

if __name__=='__main__':run()
