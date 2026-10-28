"""Formula-source CSV round-trip must not silently flatten spreadsheet formulas."""
import csv
import io
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(accept_downloads=True, viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="data"]').click()
        original = 'id,note,calc\n1,"Ångström, one",=SUM(A1:A2)\n2,"two\nlines",=IF(A2>0,42,0)\n'
        page.locator('#dt-import').set_input_files({
            'name': 'formula_source.csv', 'mimeType': 'text/csv',
            'buffer': original.encode('utf-8')})
        page.wait_for_function('() => MathStudio.dataTables.tables.some(t => t.name === "formula_source")')
        rows = page.evaluate('MathStudio.dataTables.active.rows')
        assert rows == [['1', 'Ångström, one', '=SUM(A1:A2)'],
                        ['2', 'two\nlines', '=IF(A2>0,42,0)']], rows

        # Existing evaluated export stays value-only, preserving its old contract.
        page.locator('#data-menu-navigation > details').nth(3).evaluate('(e) => e.open = true')
        with page.expect_download() as result:
            page.locator('#dt-export-csv').click()
        values = list(csv.reader(io.StringIO(Path(result.value.path()).read_text(encoding='utf-8'))))
        assert values[1][2] == '3', values
        assert values[2][2] == '42', values

        page.locator('#data-menu-navigation > details').nth(3).evaluate('(e) => e.open = true')
        with page.expect_download() as result:
            page.locator('#dt-export-source-csv').click()
        downloaded = result.value
        assert downloaded.suggested_filename.endswith('_formulas.csv')
        raw = Path(downloaded.path()).read_bytes()
        assert list(csv.reader(io.StringIO(raw.decode('utf-8')))) == [
            ['id', 'note', 'calc'], *rows]
        page.locator('#dt-import').set_input_files({
            'name': 'roundtrip.csv', 'mimeType': 'text/csv', 'buffer': raw})
        page.wait_for_function('() => MathStudio.dataTables.tables.some(t => t.name === "roundtrip")')
        assert page.evaluate('MathStudio.dataTables.active.rows') == rows
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#dt-export-source-csv').count() == 1
        assert not errors, errors
        browser.close()
    print('PASS formula-source CSV round-trip, Unicode/multiline quoting, evaluated CSV unchanged')


if __name__ == '__main__':
    main()
