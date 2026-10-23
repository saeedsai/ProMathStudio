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
