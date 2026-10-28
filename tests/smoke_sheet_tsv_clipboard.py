"""Spreadsheet clipboard TSV quoting, transactional paste and responsive regression."""
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
        page.evaluate("Object.defineProperty(navigator, 'clipboard', {value: undefined, configurable: true})")
        page.locator('[data-workspace="data"]').click()
        page.locator('#dt-import').set_input_files({
            'name': 'clipboard_tsv.csv', 'mimeType': 'text/csv',
            'buffer': b'a,b,c,d\n1,2,3,4\n5,6,7,8\n9,10,11,12\n13,14,15,16\n'})
        page.wait_for_function("() => MathStudio.dataTables.active.name === 'clipboard_tsv'")
        menu = page.locator('#workspace-context-menu')

        def row_menu(index):
            page.locator('#dt-sheet tbody tr').nth(index).locator('th.dt-rownum').click(button='right')

        def cell_menu(index):
            page.locator('#dt-sheet tbody tr').nth(index).locator('td').first.click(button='right')

        source = ['tab\tvalue', 'line1\nline2', 'quote "here"', '=2+3']
        page.evaluate("""values => {
            MathStudio.dataTables.active.rows[0] = values;
            MathStudio.dataTables.refresh();
        }""", source)
        row_menu(0)
        menu.get_by_text('Copy row (tab-separated)', exact=True).click()
        assert page.evaluate('MathStudio.contextActions.clipboard()') == (
            '"tab\tvalue"\t"line1\nline2"\t"quote ""here"""\t=2+3')
        row_menu(1)
        menu.get_by_text('Paste row', exact=True).click()
        assert page.evaluate('MathStudio.dataTables.active.rows[1]') == source

        # Quote-only fields must be escaped, not mistaken for formatting on paste.
        quoted = ['"literal quotes"', 'plain', '', 'end']
        page.evaluate("""values => {
            MathStudio.dataTables.active.rows[2] = values;
            MathStudio.dataTables.refresh();
        }""", quoted)
        row_menu(2)
        menu.get_by_text('Copy row (tab-separated)', exact=True).click()
        row_menu(3)
        menu.get_by_text('Paste row', exact=True).click()
        assert page.evaluate('MathStudio.dataTables.active.rows[3]') == quoted

        # A broken quoted cell must not change the destination row or its formulas.
        original = page.evaluate('MathStudio.dataTables.active.rows[3].slice()')
        page.evaluate("""value => {
            MathStudio.dataTables.active.rows[0][0] = value;
            MathStudio.dataTables.refresh();
        }""", '"unfinished')
        cell_menu(0)
        menu.get_by_text('Copy cell (formula)', exact=True).click()
        cell_menu(3)
        menu.get_by_text('Paste into cell / range', exact=True).click()
        assert 'Unterminated quoted clipboard cell' in page.locator('#dt-status').inner_text()
        assert page.evaluate('MathStudio.dataTables.active.rows[3]') == original

        # An oversized paste cannot create extra columns or overwrite existing cells.
        page.evaluate("""value => {
            MathStudio.dataTables.active.rows[0][0] = value;
            MathStudio.dataTables.refresh();
        }""", '\t'.join(['x'] * 33))
        cell_menu(0)
        menu.get_by_text('Copy cell (formula)', exact=True).click()
        cell_menu(3)
        menu.get_by_text('Paste into cell / range', exact=True).click()
        assert 'too many columns' in page.locator('#dt-status').inner_text()
        assert page.evaluate('MathStudio.dataTables.active.rows[3]') == original
        assert page.evaluate('MathStudio.dataTables.active.columns.length') == 4

        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#dt-sheet').count() == 1
            assert page.evaluate('MathStudio.dataTables.active.rows[1]') == source
        assert not errors, errors
        browser.close()
    print('PASS quoted TSV row copy/paste, multiline and formula cells, rollback, mobile')


if __name__ == '__main__':
    main()
