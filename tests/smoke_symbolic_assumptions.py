"""Selected-variable assumptions: SymPy references, worker payload and project rollback."""
import json, os, re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=(ROOT/'index.html').read_text(encoding='utf-8')
    m=re.search(r'<script id="mathstudio-sympy-python" type="text/plain">(.*?)</script>',source,re.S)
    assert m
    scope={}
    exec(compile(m.group(1),'<sympy>','exec'),scope)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':900},accept_downloads=True)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('dialog',lambda d:d.accept())
        page.set_content(source,wait_until='load')
        def ast(s):return page.evaluate('(s)=>MathStudio.parse(s).ast',s)
        def run(s,op,flags):
            return json.loads(scope['_ms_process'](json.dumps({'ast':ast(s),'operation':op,'variable':'x','assumptions':flags})))
        assert 'Abs(x)' in run('sqrt(x^2)','simplify',{'real':True})['items'][0]['plain']
        assert run('sqrt(x^2)','simplify',{'positive':True})['items'][0]['plain']=='x'
        assert run('x^2=1','solve',{'positive':True})['items'][0]['plain']=='Eq(x, 1)'
        assert run('x^2=1','solve',{'negative':True})['items'][0]['plain']=='Eq(x, -1)'
        assert {i['plain'] for i in run('x^2=1','solve',{'integer':True})['items']}=={'Eq(x, -1)','Eq(x, 1)'}
        for flags,op in [({'positive':True,'negative':True},'simplify'),({'real':'yes'},'simplify'),({'other':True},'simplify'),({'integer':True},'numeric')]:
            try:run('x^2=1',op,flags);assert False,(flags,op)
            except scope['MathStudioSympyError']:pass
        page.locator('[data-workspace="solver"]').click()
        page.locator('#cas-operation').select_option('simplify')
        page.locator('#equation-input').fill('sqrt(x^2)')
        page.get_by_role('button',name='Assumptions').click()
        assert page.locator('#ui-solver-assumptions').evaluate('(e)=>e.open')
        page.locator('#cas-assume-positive').check()
        page.evaluate("""() => {
          window.Worker=class {
            postMessage(m){
              window.__assumptionPayload=m.payload;
              queueMicrotask(()=>this.onmessage({data:{id:m.id,type:'result',data:{
                operation:'simplify',version:'1.14.0',note:'Assumptions applied',
                items:[{plain:'x',latex:'x',mathml:'<math><mi>x</mi></math>',approx:''}]
              }}}));
            }
            terminate(){}
          };
        }""")
        page.locator('#cas-run').click()
        page.wait_for_function('() => !!window.__assumptionPayload')
        assert page.evaluate('window.__assumptionPayload.assumptions.positive') is True
        page.wait_for_function("() => document.querySelector('#cas-python').textContent.includes('positive=True')")
        page.locator('#cas-assume-negative').check()
        assert page.locator('#cas-save').is_disabled()
        page.locator('#cas-run').click()
        assert 'Contradictory assumptions' in page.locator('#cas-status').inner_text()
        page.locator('#cas-assume-negative').uncheck()
        page.locator('#cas-engine').select_option('offline')
        page.locator('#cas-run').click()
        assert 'require SymPy' in page.locator('#cas-status').inner_text()
        page.locator('#cas-engine').select_option('auto')
        backup=page.evaluate('MathStudio.bridge.export()')
        assert backup['solver']['assumptions']['positive'] is True
        page.locator('#cas-assume-positive').uncheck()
        def upload(data):
            page.locator('#hub-project-file').set_input_files({'name':'assumptions.json','mimeType':'application/json','buffer':json.dumps(data).encode('utf-8')})
        upload(backup)
        page.wait_for_function("() => document.querySelector('#cas-assume-positive').checked")
        bad=json.loads(json.dumps(backup));bad['solver']['assumptions']={'positive':True,'negative':True}
        upload(bad)
        page.wait_for_function("() => document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
        assert page.locator('#cas-assume-positive').is_checked()
        assert not errors,errors
        browser.close()
    print('PASS: assumptions references, contradictions, worker payload, project rollback')
if __name__=='__main__':main()
