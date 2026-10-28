"""Graph action disclosure, task panels, navigation, PNG and transfer regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(accept_downloads=True, viewport={'width':1280,'height':850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="graph"]').click()
        assert page.locator('#graph-plot').is_visible()
        assert page.locator('#graph-save').is_visible()
        assert page.locator('[data-graph-mode="2d"]').is_visible()
        assert page.locator('[data-graph-mode="3d"]').is_visible()
        assert page.locator('#ui-graph-share-actions > summary').is_visible()
        assert not page.locator('[data-forward="graph"][data-destination="editor"]').is_visible()
        assert not page.locator('[data-forward="graph"][data-destination="solver"]').is_visible()
        original = 'y=x^2\ny=sin(x)'
        page.locator('#graph-input').fill(original)
        page.locator('#graph-plot').click()
        assert page.locator('#graph-legend .graph-legend-line').count() == 2
        page.locator('#workspace-task-select').select_option('appearance')
        assert page.locator('#graph-appearance').evaluate('(e)=>e.open')
        page.locator('#plot-palette').select_option('bright')
        page.locator('#workspace-task-select').select_option('axes')
        assert not page.locator('#graph-appearance').evaluate('(e)=>e.open')
        assert page.locator('#ui-graph-axes').evaluate('(e)=>e.open')
        assert page.locator('#graph-xmin').is_visible()
        page.locator('#graph-xmin').fill('-7')
        page.locator('#graph-xmax').fill('7')
        page.locator('#graph-plot').click()
        bounds = page.evaluate('MathStudio.advanced.getGraphState().bounds')
        assert bounds['xmin'] == -7 and bounds['xmax'] == 7, bounds
        with page.expect_download() as download:
            page.locator('#graph-save').click()
        assert download.value.suggested_filename.endswith('_2d_graph.png')
        page.locator('[data-graph-mode="3d"]').click()
        page.locator('#graph-input').fill('z=x^2+y^2')
        page.locator('#graph-plot').click()
        assert page.locator('#graph-legend .graph-legend-line').count() == 1
        page.locator('[data-graph-mode="2d"]').click()
        assert page.locator('#graph-input').input_value() == original
        summary = page.locator('#ui-graph-share-actions > summary')
        summary.focus()
        page.keyboard.press('Enter')
        assert page.locator('#ui-graph-share-actions').evaluate('(e)=>e.open')
        assert page.locator('[data-forward="graph"][data-destination="editor"]').is_visible()
        assert page.locator('[data-forward="graph"][data-destination="solver"]').is_visible()
        page.locator('[data-forward="graph"][data-destination="editor"]').click()
        assert 'x^2' in page.locator('#equation-input').input_value()
        page.locator('[data-workspace="graph"]').click()
        assert page.locator('#graph-input').input_value() == original
        page.locator('#workspace-task-select').select_option('table')
        assert page.locator('#ui-graph-table').evaluate('(e)=>e.open')
        assert page.locator('#graph-plot').is_visible()
        for width in (390, 768, 1280):
            page.set_viewport_size({'width':width,'height':850})
            assert page.locator('#ui-graph-share-actions > summary').is_visible(), width
            assert page.locator('#graph-plot').is_visible(), width
        assert not errors, errors
        browser.close()
    print('PASS graph action disclosure, axes, appearance, 2D/3D, PNG, transfer, mobile')

if __name__ == '__main__':
    main()
