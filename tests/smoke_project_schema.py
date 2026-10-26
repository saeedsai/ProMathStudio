"""Versioned project import, validation and atomic rollback browser regression."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def upload(page, data, filename='backup.json'):
    raw = data if isinstance(data, bytes) else json.dumps(data).encode('utf-8')
    page.locator('#hub-project-file').set_input_files({
        'name': filename, 'mimeType': 'application/json', 'buffer': raw})


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('dialog', lambda dialog: dialog.accept())
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        original = page.evaluate('window.MathStudio.bridge.export()')
        assert original['version'] == 2
        legacy = dict(original, version=1, working='x+1', origin='editor',
                      notebook=[{'raw': 'x+1'}])
        upload(page, legacy)
        page.wait_for_function("window.MathStudio.bridge.export().working === 'x+1'")
        migrated = page.evaluate('window.MathStudio.bridge.export()')
        assert migrated['version'] == 2
        assert [item['raw'] for item in migrated['notebook']] == ['x+1']
        assert migrated['tables'] == original['tables'], 'legacy table data changed'

        def rejected(candidate):
            page.locator('#hub-status').evaluate("el => el.textContent = ''")
            upload(page, candidate)
            page.wait_for_function("document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
            current = page.evaluate('window.MathStudio.bridge.export()')
            assert current['working'] == migrated['working']
            assert [i['raw'] for i in current['notebook']] == ['x+1']
            assert current['tables'] == migrated['tables']

        rejected(dict(legacy, version=99, working='WRONG'))
        rejected(dict(legacy, working='WRONG', notebook=[{'raw': 42}]))
        bad_tables = {'version': 1, 'selected': 'sheet-1', 'tables': [
            {'id': 'sheet-1', 'name': 'Data1', 'columns': ['A', 'B'], 'rows': [['1']]}]}
        rejected(dict(legacy, working='WRONG', tables=bad_tables))
        upload(page, b' ' * 2_000_001)
        page.wait_for_function("document.querySelector('#hub-status').textContent.includes('exceeds 2 MB')")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'x+1'

        # Simulate a restore-stage failure after notebook mutation. The previous
        # project must be reapplied rather than left half imported.
        page.evaluate("""() => {
          const fit=window.MathStudio.curveFit;
          window.__originalFitRestore=fit.restoreState;
          let once=true;
          fit.restoreState=(value)=>{
            if(once){once=false;throw Error('injected restore failure');}
            return window.__originalFitRestore(value);
          };
        }""")
        upload(page, dict(legacy, working='SHOULD_ROLL_BACK', notebook=[{'raw': 'y^2'}]))
        page.wait_for_function("document.querySelector('#hub-status').textContent.includes('injected restore failure')")
        page.evaluate("window.MathStudio.curveFit.restoreState=window.__originalFitRestore")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'x+1'
        assert [i['raw'] for i in page.evaluate('window.MathStudio.bridge.export().notebook')] == ['x+1']
        assert not errors, errors
        browser.close()
    print('PASS: v1→v2 migration, workbook retention, invalid/future/oversize refusal and transactional rollback')


if __name__ == '__main__':
    main()
