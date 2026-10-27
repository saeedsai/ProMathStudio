"""SymPy first-order ODE initial conditions: exact references, worker and project validation."""
import json,os,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def main():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    match=re.search(r'<script id="mathstudio-sympy-python" type="text/plain">(.*?)</script>',html,re.S)
    assert match
    scope={}
    exec(compile(match.group(1),'<sympy>','exec'),scope)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':900},accept_downloads=True)
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('dialog',lambda dialog:dialog.accept())
        page.set_content(html,wait_until='load')
        ast=lambda expression:page.evaluate('(s)=>MathStudio.parse(s).ast',expression)
        ode=ast('diff(y(t),t)=y(t)')
        def solve(conditions):
            return json.loads(scope['_ms_process'](json.dumps({'ast':ode,'operation':'ode','variable':'t','icsAsts':[ast(x) for x in conditions]})))
        assert solve(['y(0)=1'])['items'][0]['plain']=='Eq(y(t), exp(t))'
        assert solve(['y(0)=0'])['items'][0]['plain']=='Eq(y(t), 0)'
        assert solve(['y(0)=1','y(1)=e'])['items'][0]['plain']=='Eq(y(t), exp(t))'
        assert 'arbitrary' in solve([])['note']
        for conditions in [['y(0)=1','y(1)=2'],['z(0)=1'],['y(t)=1'],['y(0)=x'],['y(oo)=1'],['y(0)=1','y(0)=2']]:
            try:solve(conditions);assert False,conditions
            except scope['MathStudioSympyError']:pass
        for bad in [None,{},[ast('y(0)=1')]*3]:
            try:scope['_ms_process'](json.dumps({'ast':ode,'operation':'ode','variable':'t','icsAsts':bad}));assert False,bad
            except scope['MathStudioSympyError']:pass
        page.locator('[data-workspace="solver"]').click()
        page.locator('#cas-operation').select_option('ode')
        assert page.locator('#cas-ode-ic').is_visible()
        page.locator('#cas-variable').fill('t')
        page.locator('#equation-input').fill('diff(y(t),t)=y(t)')
        page.locator('#cas-ode-ic').fill('y(0)=1; y(1)=e')
        page.evaluate("""() => {
          window.Worker=class {
            postMessage(m){
              window.__odePayload=m.payload;
              queueMicrotask(()=>this.onmessage({data:{id:m.id,type:'result',data:{
                operation:'ode',version:'1.14.0',note:'Initial conditions applied',
                items:[{plain:'Eq(y(t), exp(t))',latex:'y(t)=e^t',mathml:'<math><mi>y</mi></math>',approx:''}]
              }}}));
            }
            terminate(){}
          };
        }""")
        page.locator('#cas-run').click()
        page.wait_for_function('() => !!window.__odePayload')
        assert len(page.evaluate('window.__odePayload.icsAsts'))==2
        page.wait_for_function("() => document.querySelector('#cas-python').textContent.includes('initial_conditions')")
        backup=page.evaluate('MathStudio.bridge.export()')
        assert backup['solver']['odeInitialCondition']=='y(0)=1; y(1)=e'
        page.locator('#cas-ode-ic').fill('')
        page.locator('#hub-project-file').set_input_files({'name':'ode.json','mimeType':'application/json','buffer':json.dumps(backup).encode('utf-8')})
        page.wait_for_function("() => document.querySelector('#cas-ode-ic').value==='y(0)=1; y(1)=e'")
        bad=json.loads(json.dumps(backup))
        bad['solver']['odeInitialCondition']='x'*161
        try:page.evaluate('(data)=>MathStudio.projectSchema.migrate(data)',bad);assert False
        except Exception as ex:assert 'ODE initial condition' in str(ex)
        page.locator('#cas-operation').select_option('simplify')
        assert not page.locator('#cas-ode-ic').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS ODE initial conditions reference, rejection, worker and project')

if __name__=='__main__':
    main()
