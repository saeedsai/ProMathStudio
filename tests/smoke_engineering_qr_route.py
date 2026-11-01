"""Engineering QR route: keyboard/mobile, rank and shape errors, 3x2 reference residuals."""
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TOOL = 'matrix.qr.real.small'


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        catalog = page.evaluate("""() => MathStudio.engineeringCatalog.tools
            .filter(t=>t.id==='matrix.qr.real.small')
            .map(t=>({status:t.status,route:t.route,disciplines:t.disciplines}))""")
        assert len(catalog) == 1, catalog
        assert catalog[0]['status'] == 'available', catalog
        assert catalog[0]['route'] == {
            'mode': 'calculator', 'target': 'matrix', 'focusId': 'mat-qr'}, catalog
        assert 'aerospace' in catalog[0]['disciplines']
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 844})
            page.locator('[data-workspace="engineering"]').click()
            page.locator('#eng-discipline').select_option('aerospace')
            page.locator('#eng-search').fill('QR factorization')
            card = page.locator('#eng-results article[data-tool-id="' + TOOL + '"]')
            assert card.count() == 1 and card.locator('button').count() == 1
            assert page.locator('#engineering-panel').evaluate(
                '(e) => e.scrollWidth <= e.clientWidth + 1'), width
            page.locator('#calc-input').evaluate('(e) => e.value="9+2"')
            card.locator('button').focus()
            page.keyboard.press('Enter')
            page.wait_for_function("document.activeElement?.id === 'mat-qr'")
            assert page.locator('#calculator-panel').is_visible()
            assert page.locator('#matrix-tools').evaluate('(e) => e.open')
            assert page.locator('#calc-input').input_value() == '9+2'
            page.locator('#mat-rows').select_option('3')
            page.locator('#mat-cols').select_option('2')
            grid = page.locator('#mat-grid')

            # Dependent columns must fail without silently returning a misleading QR.
            for row, col, value in [(0, 0, '1'), (0, 1, '2'),
                                    (1, 0, '2'), (1, 1, '4'),
                                    (2, 0, '3'), (2, 1, '6')]:
                grid.locator(f'[data-row="{row}"][data-col="{col}"]').fill(value)
            page.locator('#mat-qr').focus()
            page.keyboard.press('Enter')
            assert 'Rank-deficient' in page.locator('#mat-result').inner_text()
            assert page.locator('#mat-result').evaluate(
                "(e) => e.classList.contains('error')")

            # Full-rank 3x2 economy QR: A = [[1,0],[0,1],[1,1]].
            for row, col, value in [(0, 0, '1'), (0, 1, '0'),
                                    (1, 0, '0'), (1, 1, '1'),
                                    (2, 0, '1'), (2, 1, '1')]:
                grid.locator(f'[data-row="{row}"][data-col="{col}"]').fill(value)
            page.locator('#mat-qr').focus()
            page.keyboard.press('Enter')
            output = page.locator('#mat-result').inner_text()
            assert 'qr: A = Q·R' in output, output
            assert not page.locator('#mat-result').evaluate(
                "(e) => e.classList.contains('error')")
            for label in ('Relative reconstruction residual:', 'Orthogonality residual:'):
                match = re.search(re.escape(label) + r'\s*([0-9.eE+-]+)', output)
                assert match and float(match.group(1)) < 1e-10, (label, output)

            # QR's documented economy shape excludes a wide 2x3 input.
            page.locator('#mat-rows').select_option('2')
            page.locator('#mat-cols').select_option('3')
            page.locator('#mat-qr').click()
            assert 'rows to be at least its columns' in page.locator('#mat-result').inner_text()
            assert page.locator('#mat-result').evaluate(
                "(e) => e.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print('PASS Engineering QR canonical route, 390/768/1280 keyboard, rank/shape and 3x2 residuals')


if __name__ == '__main__':
    main()
