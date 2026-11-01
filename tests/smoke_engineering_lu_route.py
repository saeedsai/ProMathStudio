"""Engineering catalog LU route: keyboard, mobile, numerical reference and error recovery."""
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TOOL = 'matrix.lu.real.small'


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'),
                         wait_until='load')
        catalog = page.evaluate("""() => {
            const c = MathStudio.engineeringCatalog;
            return c.tools.filter(t => t.id === 'matrix.lu.real.small')
                .map(t => ({status:t.status,route:t.route,disciplines:t.disciplines}));
        }""")
        assert len(catalog) == 1, catalog
        assert catalog[0]['status'] == 'available', catalog
        assert catalog[0]['route'] == {
            'mode': 'calculator', 'target': 'matrix', 'focusId': 'mat-lu'}, catalog
        assert 'aerospace' in catalog[0]['disciplines']

        for width in (390, 1280):
            page.set_viewport_size({'width': width, 'height': 844})
            page.locator('[data-workspace="engineering"]').click()
            page.locator('#eng-discipline').select_option('aerospace')
            page.locator('#eng-search').fill('LU factorization')
            card = page.locator('#eng-results article[data-tool-id="' + TOOL + '"]')
            assert card.count() == 1
            assert card.locator('button').count() == 1
            assert page.locator('#engineering-panel').evaluate(
                '(e) => e.scrollWidth <= e.clientWidth + 1'), width
            card.locator('button').focus()
            page.keyboard.press('Enter')
            page.wait_for_function("document.activeElement?.id === 'mat-lu'")
            assert page.locator('#calculator-panel').is_visible()
            assert page.locator('#matrix-tools').evaluate('(e) => e.open')
            assert page.locator('#mat-lu').is_visible()

            grid = page.locator('#mat-grid')
            for row, col, value in [(0, 0, '1'), (0, 1, '2'),
                                    (1, 0, '2'), (1, 1, '4')]:
                grid.locator(f'[data-row="{row}"][data-col="{col}"]').fill(value)
            page.locator('#mat-lu').focus()
            page.keyboard.press('Enter')
            assert 'Singular' in page.locator('#mat-result').inner_text()
            assert page.locator('#mat-result').evaluate(
                "(e) => e.classList.contains('error')")

            # A row-swap reference matrix has a valid P*A=L*U factorization.
            grid.locator('[data-row="0"][data-col="0"]').fill('0')
            grid.locator('[data-row="1"][data-col="0"]').fill('3')
            page.locator('#mat-lu').focus()
            page.keyboard.press('Enter')
            output = page.locator('#mat-result').inner_text()
            assert 'P·A = L·U' in output, output
            assert not page.locator('#mat-result').evaluate(
                "(e) => e.classList.contains('error')")
            match = re.search(r'Relative reconstruction residual:\s*([0-9.eE+-]+)', output)
            assert match and float(match.group(1)) < 1e-10, output
        assert not errors, errors
        browser.close()
    print('PASS Engineering LU canonical route, keyboard, 390/1280, singular recovery and residual')


if __name__ == '__main__':
    main()
