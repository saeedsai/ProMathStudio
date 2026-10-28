"""Data Tables JSON export rejects duplicate headers without silent cell loss."""
import csv
import io
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(accept_downloads=True, viewport={'width': 1280, 'height': 850})
        errors, downloads = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('download', lambda download: downloads.append(download.suggested_filename))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="data"]').click()
        page.locator('#data-menu-navigation > details').nth(3).evaluate('(e) => e.open = true')

        def restore(headers, rows):
            page.evaluate("""(payload) => MathStudio.dataTables.restoreState({
                version: 1, selected: 'sheet-1',
                tables: [{id: 'sheet-1', name: 'Export', columns: payload[0], rows: payload[1]}]
            })""", [headers, rows])

        restore(['amount', 'amount'], [['10', '20'], ['30', '40']])
        before = page.evaluate('MathStudio.dataTables.exportState()')
        page.locator('#dt-export-json').click()
        assert 'JSON export requires unique column headers' in page.locator('#dt-status').inner_text()
        assert downloads == [], downloads
        assert page.evaluate('MathStudio.dataTables.exportState()') == before

        # Duplicate columns remain representable in CSV without losing either value.
        with page.expect_download() as result:
            page.locator('#dt-export-csv').click()
        csv_rows = list(csv.reader(io.StringIO(Path(result.value.path()).read_text())))
        assert csv_rows == [['amount', 'amount'], ['10', '20'], ['30', '40']], csv_rows

        # JSON property names are case-sensitive; differently cased headers are valid.
        restore(['Amount', 'amount'], [['10', '=A1*2']])
        with page.expect_download() as result:
            page.locator('#dt-export-json').click()
        assert json.loads(Path(result.value.path()).read_text()) == [
            {'Amount': '10', 'amount': 20}]
        assert result.value.suggested_filename == 'Export.json'

        # A single empty header is legal JSON, while two empty headers are not.
        restore(['', 'value'], [['a', 'b']])
        with page.expect_download() as result:
            page.locator('#dt-export-json').click()
        assert json.loads(Path(result.value.path()).read_text()) == [{'': 'a', 'value': 'b'}]
        restore(['', ''], [['a', 'b']])
        page.locator('#dt-export-json').click()
        assert 'unique column headers' in page.locator('#dt-status').inner_text()

        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#dt-export-json').count() == 1
        assert not errors, errors
        browser.close()
    print('PASS Data Tables duplicate JSON header rejection, CSV preservation, formulas, case and responsive')


if __name__ == '__main__':
    main()
