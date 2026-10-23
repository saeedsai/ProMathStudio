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
