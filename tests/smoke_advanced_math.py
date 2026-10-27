"""Regression: curve fits, embedded SymPy transforms/ODE/PDE, physics and floating UI."""
from pathlib import Path
import json, math, os, re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    source=(ROOT/'index.html').read_text(encoding='utf-8')
    sympy_source=re.search(r'<script id="mathstudio-sympy-python" type="text/plain">(.*?)</script>',source,re.S)
    assert sympy_source, 'Embedded SymPy code missing'
    context={}
    exec(compile(sympy_source.group(1),'<embedded-sympy>','exec'),context)
    physics=json.loads(re.search(r'examples\.push\(\.\.\.(\[\{.*?\}\])\);\n  const input=',source,re.S).group(1))
    assert len(physics)>=72
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':900},accept_downloads=True)
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content(source,wait_until='load')
        for sample in physics:
            page.evaluate('(raw)=>MathStudio.parse(raw)',sample['code'])
        assert r'\mathcal{L}' in page.evaluate("MathStudio.latex(MathStudio.parse('laplace(exp(-2*t),t,s)').ast)")
        examples=[
            ('laplace','exp(-2*t)','t','s','1/(s + 2)'),
            ('fourier','exp(-x^2)','x','k','sqrt(pi)'),
            ('ode','diff(y(t),t)+y(t)=0','t','s','C1*exp(-t)'),
            ('ode','diffn(y(t),t,2)+4*y(t)=0','t','s','cos(2*t)'),
            ('pde','pdiff(u(x,t),t)+pdiff(u(x,t),x)=0','x','s','F('),
        ]
        for op,expr,var,target,expected in examples:
            ast=page.evaluate('(x)=>MathStudio.parse(x).ast',expr)
            result=json.loads(context['_ms_process'](json.dumps({'ast':ast,'operation':op,'variable':var,'target':target})))
            assert result['items'] and expected in result['items'][0]['plain'],(op,result)
        # Solve several symbolic equations together without writing Python in the UI.
        equations=['x = 2x + 2z','y = x - z']
        asts=[page.evaluate('(src)=>MathStudio.parse(src).ast',expr) for expr in equations]
        solved=json.loads(context['_ms_system'](json.dumps({'equations':asts,'unknowns':['x','y','z']})))
        assert solved['operation']=='system'
        assert len(solved['items'])==3
        assert '-2*z' in solved['items'][0]['plain'],solved
        assert '-3*z' in solved['items'][1]['plain'],solved
        impossible=[page.evaluate('(src)=>MathStudio.parse(src).ast',expr) for expr in ['x=1','x=2']]
        empty=json.loads(context['_ms_system'](json.dumps({'equations':impossible,'unknowns':['x']})))
        assert 'No solution' in empty['note'],empty
        page.locator('[data-workspace="solver"]').click()
        page.locator('#cas-operation').select_option('system')
        assert page.locator('#cas-system-fields').is_visible()
        assert 'x = 2x + 2z' in page.locator('#cas-system-input').input_value()
        assert page.locator('#cas-system-vars').input_value()=='x,y,z'
        # P0-SYMBOLIC-SYSTEMS: nonlinear symbolic polynomial systems, preserving
        # the existing general linear/free-parameter solver and safe failures.
        nonlinear_equations=['x^2+y^2=5','x-y=1']
        nonlinear_asts=[page.evaluate('(src)=>MathStudio.parse(src).ast',q) for q in nonlinear_equations]
        nonlinear=json.loads(context['_ms_system'](json.dumps({
            'equations':nonlinear_asts,'unknowns':['x','y'],'method':'auto'})))
        assert len(nonlinear['items'])==2,nonlinear
        assert {item['plain'] for item in nonlinear['items']}=={
            'Eq((x, y), (-1, -2))','Eq((x, y), (2, 1))'},nonlinear
        assert 'Nonlinear polynomial' in nonlinear['note'],nonlinear
        explicit=json.loads(context['_ms_system'](json.dumps({
            'equations':nonlinear_asts,'unknowns':['x','y'],'method':'nonlinear'})))
        assert explicit['items']==nonlinear['items']
        try:
            context['_ms_system'](json.dumps({
                'equations':nonlinear_asts,'unknowns':['x','y'],'method':'linear'}))
            assert False,'Nonlinear equations cannot be silently accepted as linear'
        except ValueError as exc:
            assert 'nonlinear' in str(exc).lower(),exc
        inconsistent_asts=[page.evaluate('(src)=>MathStudio.parse(src).ast',q)
                           for q in ['x^2=1','x^2=4']]
        inconsistent=json.loads(context['_ms_system'](json.dumps({
            'equations':inconsistent_asts,'unknowns':['x'],'method':'auto'})))
        assert 'No solution' in inconsistent['note'],inconsistent
        high_degree=[page.evaluate('(src)=>MathStudio.parse(src).ast','x^5=1')]
        try:
            context['_ms_system'](json.dumps({'equations':high_degree,'unknowns':['x']}))
            assert False,'Large-degree nonlinear inputs must be bounded'
        except ValueError as exc:
            assert 'degree-4' in str(exc),exc
        # Changing the system method in the UI must affect the submitted job.
        assert page.locator('#cas-system-method').input_value()=='auto'
        page.locator('#cas-system-method').select_option('linear')
        assert page.locator('#cas-system-method').input_value()=='linear'
        page.locator('#cas-system-method').select_option('nonlinear')
        assert page.locator('#cas-system-method').input_value()=='nonlinear'
        page.locator('#cas-system-method').select_option('auto')
        fits={
            'linear':[[x,3+2*x] for x in range(5)],
            'poly':[[x,2*x*x+3*x+1] for x in range(-3,4)],
            'exp':[[x,4*math.exp(.4*x)] for x in range(6)],
            'log':[[x,2+3*math.log(x)] for x in range(1,7)],
            'power':[[x,2*x**1.8] for x in range(1,7)],
            'gaussian':[[x,3*math.exp(-((x-2)/1.3)**2)] for x in range(-2,7)]
        }
        for model,points in fits.items():
            result=page.evaluate('([a,b])=>MathStudio.curveFit.analyze(a,b,2)',[points,model])
            assert result['r2']>.999999 and result['rmse']<.00001,(model,result)
        page.locator('[data-workspace="graph"]').click()
        page.get_by_role('button',name='Plot table data').click()
        assert page.locator('#ui-graph-table').evaluate('(e)=>e.open')
        page.locator('#dt-chart-type').select_option('scatter')
        page.locator('#fit-model').select_option('poly')
        page.locator('#fit-run').click()
        assert 'R²' in page.locator('#fit-result').inner_text()
        assert not page.locator('#graph-status').evaluate('(e)=>e.classList.contains("error")')
        with page.expect_download() as downloaded:page.locator('#hub-export-project').click()
        backup=json.loads(Path(downloaded.value.path()).read_text(encoding='utf-8'))
        assert backup['fit']['model']=='poly'
        page.locator('[data-workspace="editor"]').click()
        page.locator('#quick-symbols').click()
        assert page.locator('body').evaluate('(x)=>x.classList.contains("library-open")')
        page.locator('#quick-help').click()
        assert page.locator('#help-dialog').is_visible()
        assert 'Solving ODEs and PDEs' in page.locator('#help-topics').inner_text()
        page.locator('#close-help').click()
        page.locator('#quick-examples').click()
        page.locator('#example-category').select_option('Physics · Mechanics')
        assert page.locator('#examples-list button').count()>=15
        page.locator('#ui-overlay').click(position={'x':5,'y':5},force=True)
        page.set_viewport_size({'width':390,'height':844})
        assert page.locator('#quick-help').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: 72 physics examples; 6 regressions; Laplace, Fourier, ODE/PDE; fitting and UI')

if __name__=='__main__':
    main()
