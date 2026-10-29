"""Data Tables column filters must use the displayed spreadsheet row number."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="data"]').click()
        page.locator('#dt-import').set_input_files({
            'name': 'filter_alignment.csv', 'mimeType': 'text/csv',
            'buffer': b'id,category,amount\n1,red,10\n2,blue,20\n3,red,30\n4,blue,40\n'})
        page.wait_for_function("() => !document.querySelector('#dt-import-preview').hidden")
        page.locator('#dt-import-confirm').evaluate('(e) => e.click()')
        page.wait_for_function("() => MathStudio.dataTables.active.name === 'filter_alignment'")
        page.get_by_role('button', name='Filter rows', exact=True).click()
        page.locator('#dt-filter-column').select_option('1')
        page.locator('#dt-filter-op').select_option('eq')
        page.locator('#dt-filter-value').fill('red')
        page.locator('#dt-filter-apply').click()

        def visible_rows(expected):
            page.wait_for_function(
                "expected => JSON.stringify([...document.querySelectorAll('#dt-sheet tbody tr')].filter(r => !r.hidden).map(r => r.querySelector('th').textContent.trim())) === JSON.stringify(expected)",
                arg=[str(n) for n in expected])
            return [row.strip() for row in page.locator('#dt-sheet tbody tr:visible th.dt-rownum').all_text_contents()]

        assert visible_rows([1, 3]) == ['1', '3'], 'first and middle matches must align with their own row values'
        assert page.locator('#dt-filter-report').inner_text().startswith('2 visible rows')
        assert page.evaluate('MathStudio.dataTables.active.rows.map(row => row[1])') == ['red', 'blue', 'red', 'blue']

        # The final spreadsheet row must be included, not shifted to its predecessor.
        page.locator('#dt-filter-value').fill('blue')
        page.locator('#dt-filter-apply').click()
        assert visible_rows([2, 4]) == ['2', '4']

        # Numeric predicates use evaluated values and must include the final row.
        page.locator('#dt-filter-column').select_option('2')
        page.locator('#dt-filter-op').select_option('gt')
        page.locator('#dt-filter-value').fill('20')
        page.locator('#dt-filter-apply').click()
        assert visible_rows([3, 4]) == ['3', '4']

        # Combining text search with a column filter must never shift row identity.
        page.locator('#dt-filter').fill('blue')
        assert visible_rows([4]) == ['4']
        page.locator('#dt-filter').fill('')
        assert visible_rows([3, 4]) == ['3', '4']

        # Re-render after a sort must apply the rule to the new physical row order.
        page.locator('#dt-sortcol').select_option('2')
        page.locator('#dt-sortdir').select_option('desc')
        page.locator('#dt-sort').click()
        assert visible_rows([1, 2]) == ['1', '2']
        page.locator('#dt-filter-reset').click()
        assert visible_rows([1, 2, 3, 4]) == ['1', '2', '3', '4']
        assert not errors, errors
        browser.close()
    print('PASS column filter first/last row, search intersection, sort and reset')


if __name__ == '__main__':
    main()
