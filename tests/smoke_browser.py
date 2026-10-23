"""Browser smoke test. Requires: pip install playwright; python -m playwright install chromium."""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    # Initialize the DOM directly: avoids external network and a local HTTP port.
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(accept_downloads=True, viewport={'width': 1440, 'height': 960})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')

        assert page.locator('[data-workspace="editor"]').count() == 1
        assert page.locator('#connected-hub').is_visible()
        # Connected Workspace is a single shared footer for every tab and screen size.
        for width, height in [(1440, 960), (390, 844)]:
            page.set_viewport_size({'width': width, 'height': height})
            for mode, last in [('editor', '#examples'),
                               ('calculator', '#calculator-panel'),
                               ('solver', '#symbolic-panel'),
                               ('graph', '#graph-panel')]:
                page.locator(f'[data-workspace="{mode}"]').click()
                panel = page.locator(last).bounding_box()
                hub = page.locator('#connected-hub').bounding_box()
                assert panel is not None and hub is not None, (mode, width)
                assert hub['y'] >= panel['y'] + panel['height'] - 1, (mode, width, panel, hub)
                assert page.locator('#connected-hub').count() == 1
        page.set_viewport_size({'width': 1440, 'height': 960})
        page.locator('[data-workspace="editor"]').click()
        page.locator('#equation-input').fill('(x-1)^2')
        assert page.locator('#preview math').count() > 0
        page.locator('#add-btn').click()
        assert page.locator('#counter').inner_text() == '(1)'

        page.locator('[data-workspace="solver"]').click()
        assert page.locator('#symbolic-panel').is_visible()
        page.locator('#equation-input').fill('(x-1)^2')
        page.locator('#cas-engine').select_option('offline')
        page.locator('#cas-operation').select_option('expand')
        page.locator('#cas-run').click()
        assert page.locator('#cas-results .cas-equation').count() > 0, page.locator('#cas-status').inner_text()

        page.locator('[data-workspace="calculator"]').click()
        page.locator('#calc-input').fill('5!+3^2')
        page.locator('#calc-execute').click()
        assert '129' in page.locator('#calc-result-plain').inner_text()

        page.locator('#hub-expression').fill('x^2')
        page.locator('[data-hub-to="graph2d"]').click()
        assert page.locator('#graph-panel').is_visible()
        page.locator('#graph-plot').click()
        assert page.locator('#graph-legend').is_visible()

        page.locator('[data-graph-mode="3d"]').click()
        page.locator('#graph-input').fill('z=x^2+y^2')
        page.locator('#graph-plot').click()
        assert page.locator('#graph-canvas').is_visible()

        # Paired 3D graph y=f(x) on z=g(x,y), Unicode multiplication and uppercase Y.
        page.locator('#graph-input').fill('Y=x×x\nz=sin(x×y)')
        page.locator('#graph-plot').click()
        assert not page.locator('#graph-status').evaluate('(e) => e.classList.contains("error")')
        assert '1 surface(s) and 1 constrained 3D curve(s)' in page.locator('#graph-status').inner_text()
        assert page.evaluate('window.MathStudio.advanced.graphCompile().map(f => f.kind)') == ['surface', 'trace']
        assert page.locator('#graph-legend .graph-legend-line').count() == 2
        # Verify the highlighted trace is drawn on the canvas, not only in legend.
        pixels = page.evaluate("""() => {
            const c=document.querySelector('#graph-canvas'), data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
            let total=0;
            for(let i=0;i<data.length;i+=4) if(data[i+2]>data[i]+50 && data[i+2]>data[i+1]+25 && data[i+2]>140)total++;
            return total;
        }""")
        assert pixels > 100, pixels
        # Existing multiple 3D surfaces still work, as does a lone y=f(x) curve.
        page.locator('#graph-input').fill('z=x^2+y^2\nz=sin(x)')
        page.locator('#graph-plot').click()
        assert page.evaluate('window.MathStudio.advanced.graphCompile().map(f => f.kind)') == ['surface','surface']
        page.locator('#graph-input').fill('y=x^2')
        page.locator('#graph-plot').click()
        assert page.evaluate('window.MathStudio.advanced.graphCompile().map(f => f.kind)') == ['trace']
        page.locator('#hub-expression').fill('Y=x×x\nz=sin(x×y)')
        page.locator('[data-hub-to="graph3d"]').click()
        assert page.locator('#graph-input').input_value() == 'Y=x×x\nz=sin(x×y)'
        assert '1 constrained 3D curve(s)' in page.locator('#graph-status').inner_text()

        with page.expect_download() as download_info:
            page.locator('#hub-export-project').click()
        assert download_info.value.suggested_filename.endswith('.json')
        assert not errors, errors
        browser.close()
    print('PASS: editor, offline CAS, calculator, shared routing, 2D/3D graphs, JSON project export')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Browser smoke failure:', repr(error), file=sys.stderr)
        raise
