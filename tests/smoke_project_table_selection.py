"""Saved Data Tables selection round-trip, atomic rejection of a stale selection and 390px layout."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def upload(page, data):
    page.locator('#hub-project-file').set_input_files({
        'name': 'backup.json', 'mimeType': 'application/json',
        'buffer': json.dumps(data).encode('utf-8')})


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        base = page.evaluate('window.MathStudio.bridge.export()')
        tables = {'version': 1, 'selected': 'sheet-2', 'tables': [
            {'id': 'sheet-1', 'name': 'Alpha', 'columns': ['z', 'a'], 'rows': [['1', '2']]},
            {'id': 'sheet-2', 'name': 'Beta', 'columns': ['q', 'r'], 'rows': [['3', '4']]}]}
        good = dict(base, working='SEL_OK', tables=tables)
        upload(page, good)
        page.wait_for_function("window.MathStudio.bridge.export().working === 'SEL_OK'")
        exported = page.evaluate('window.MathStudio.bridge.export()')['tables']
        assert [t['name'] for t in exported['tables']] == ['Alpha', 'Beta']
        assert [t['columns'] for t in exported['tables']] == [['z', 'a'], ['q', 'r']]
        assert page.evaluate('window.MathStudio.dataTables.active.name') == 'Beta'
        assert exported['selected'] == exported['tables'][1]['id']

        # A selection naming no table must be refused before any state mutation.
        bad = dict(base, working='SEL_BAD', tables=dict(tables, selected='sheet-9'))
        upload(page, bad)
        page.wait_for_function(
            "document.querySelector('#hub-status').textContent.includes('selected table does not exist')")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'SEL_OK'
        assert page.evaluate('window.MathStudio.dataTables.active.name') == 'Beta'

        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors, errors
        browser.close()
    print('PASS saved table selection round-trip, stale-selection rollback, mobile')


if __name__ == '__main__':
    main()
