"""Chromium desktop/mobile stability classification and stale-output recovery."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'),
                         wait_until='load')
        page.locator('[data-workspace="graph"]').click()
        page.locator('#control-theory-toolbox').evaluate('(e) => e.open=true')
        page.locator('#ct-equilibrium').evaluate('(e) => e.open=true')
        button = page.locator('#ct-eq-stability-run')
        button.click()
        assert 'asymptotically stable' in page.locator('#ct-eq-stability-output').inner_text()
        assert 'Equilibrium existence/uniqueness' in page.locator('#ct-eq-stability-output').inner_text()
        page.locator('#ct-eq-matrix').fill('-2,0;0,3')
        assert 'No current stability result' in page.locator('#ct-eq-stability-output').inner_text()
        button.click()
        assert 'unstable' in page.locator('#ct-eq-stability-output').inner_text()
        page.locator('#ct-eq-matrix').fill('0,0;0,2')
        button.click()
        assert 'marginal' in page.locator('#ct-eq-stability-output').inner_text()
        page.locator('#ct-eq-matrix').fill('1,2;0,3')
        button.click()
        assert 'symmetric' in page.locator('#ct-eq-stability-status').inner_text()
        assert 'No valid stability classification' in page.locator('#ct-eq-stability-output').inner_text()
        page.locator('#ct-eq-matrix').fill('1e-14,0;0,2')
        button.click()
        assert 'indeterminate' in page.locator('#ct-eq-stability-output').inner_text()
        page.locator('#ct-eq-size').select_option('3')
        page.locator('#ct-eq-matrix').fill('3,0,0;0,2,0;0,0,1')
        button.click()
        assert 'asymptotically stable' in page.locator('#ct-eq-stability-output').inner_text()
        page.set_viewport_size({'width': 390, 'height': 844})
        assert button.is_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
        assert not errors, errors
        browser.close()
    print('PASS symmetric Control stability, invalid/recovery, 390px')


if __name__ == '__main__':
    main()
