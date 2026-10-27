"""Graph UX regressions: labeled 3D surfaces, axis control, view navigation and edit preservation."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':900})
        errors=[]
        page.on('pageerror',lambda error: errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
        page.locator('[data-workspace="graph"]').click()
        original='y=x^2\ny=cos(x)'
        page.locator('#graph-input').fill(original)
        page.locator('#graph-plot').click()
        page.get_by_role('button',name='Axes & grid').click()
        assert page.locator('#ui-graph-axes').evaluate('(e)=>e.open')
        page.locator('#graph-xmin').fill('-8')
        page.locator('#graph-xmax').fill('8')
        page.locator('#graph-ymin').fill('-4')
        page.locator('#graph-ymax').fill('4')
        page.locator('#graph-grid-step').fill('2')
        page.locator('#graph-grid-step').dispatch_event('change')
        assert not page.locator('#graph-status').evaluate('(e)=>e.classList.contains("error")')
        state=page.evaluate('MathStudio.advanced.getGraphState()')
        assert state['bounds']['xmin']==-8 and state['bounds']['ymax']==4,state
        page.locator('[data-graph-mode="3d"]').click()
        surfaces='z = sin(sqrt(x^2+y^2))\nz2 = x^2\nz3 = y^2'
        page.locator('#graph-input').fill(surfaces)
        page.locator('#graph-plot').click()
        assert page.locator('#graph-legend .graph-legend-line').count()==3
        assert 'Displaying 3 functions' in page.locator('#graph-status').inner_text()
        assert not page.locator('#graph-status').evaluate('(e)=>e.classList.contains("error")')
        # A second request to select the current mode must never replace typed equations.
        page.evaluate("MathStudio.advanced.plot3D()")
        assert page.locator('#graph-input').input_value()==surfaces
        rect=page.locator('#graph-canvas').bounding_box()
        x=rect['x']+rect['width']*.45
        y=rect['y']+rect['height']*.50
        page.get_by_role('button',name='Pan 3D: off').click()
        page.mouse.move(x,y)
        page.mouse.down()
        page.mouse.move(x+65,y+35,steps=5)
        page.mouse.up()
        panned=page.evaluate('MathStudio.advanced.getGraphState()')
        assert abs(panned['panX3d'])>1 and abs(panned['panY3d'])>1,panned
        page.mouse.move(x+80,y+40)
        page.mouse.wheel(0,-280)
        zoomed=page.evaluate('MathStudio.advanced.getGraphState()')
        assert zoomed['zoom3d']>panned['zoom3d'] and zoomed['panX3d']!=panned['panX3d'],zoomed
        page.locator('#graph-plot').click()
        assert page.locator('#graph-input').input_value()==surfaces
        page.locator('[data-graph-mode="2d"]').click()
        assert page.locator('#graph-input').input_value()==original
        assert page.locator('#graph-xmin').input_value()=='-8'
        page.locator('[data-graph-mode="3d"]').click()
        assert page.locator('#graph-input').input_value()==surfaces
        # Invalid spacing reports an error instead of freezing canvas rendering.
        page.locator('#graph-grid-step').fill('-1')
        page.locator('#graph-plot').click()
        assert 'Grid spacing must be' in page.locator('#graph-status').inner_text()
        page.locator('#graph-grid-step').fill('2')
        page.locator('#graph-reset').click()
        assert page.locator('#graph-input').input_value()==surfaces
        assert not page.locator('#graph-status').evaluate('(e)=>e.classList.contains("error")')
        assert not errors,errors
        browser.close()
    print('PASS graph axes/grid, three named 3D surfaces, pan/zoom and per-mode draft preservation')

if __name__=='__main__':
    main()
