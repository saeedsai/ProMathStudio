"""Backwards-compatible truss studio: original SI reference values, CSV export and UI.
The upgraded page uses an editable table UI but retains the prior solver interface."""
from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'tools' / 'truss-studio.html').read_text(encoding='utf-8')
HTML = HTML.replace('<script defer src="truss-fem.js"></script>', '')
HTML = HTML.replace('<script defer src="truss-fem-ui.js"></script>', '')
HTML = HTML.replace('</body>', '<script>' + (ROOT / 'tools' / 'truss-fem.js').read_text(encoding='utf-8') + '</script>'
                    + '<script>' + (ROOT / 'tools' / 'truss-fem-ui.js').read_text(encoding='utf-8') + '</script></body>')


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(HTML, wait_until='load')
        assert 'Analysis complete' in page.locator('#status').inner_text()
        result = page.evaluate('() => TrussStudio.solve(TrussStudio.example)')
        assert result['residual'] < 1e-9
        forces = {m['id']: m['force'] for m in result['members']}
        assert abs(forces['AC'] + 10000 / 2**0.5) < 1e-7, forces
        assert abs(forces['BC'] + 10000 / 2**0.5) < 1e-7, forces
        assert abs(forces['AB'] - 5000) < 1e-7, forces
        reactions = {n['id']: n for n in result['nodes']}
        assert abs(reactions['A']['ry'] - 5000) < 1e-7
        assert abs(reactions['B']['ry'] - 5000) < 1e-7
        assert abs(reactions['A']['rx']) < 1e-7
        assert result['maxDisplacement'] > 0
        assert page.locator('#member-results tr').count() == 3
        assert page.locator('#joint-results tr').count() == 3
        assert page.locator('#plot line').count() >= 6
        # Import a model produced by the old SI-only JSON editor: retain N, Pa, m² semantics.
        prior = page.evaluate('TrussStudio.example')
        page.locator('#import-model').set_input_files({'name':'legacy.json','mimeType':'application/json',
                                                      'buffer':json.dumps(prior).encode('utf-8')})
        assert 'Analysis complete' in page.locator('#status').inner_text()
        # Normalized user controls now show kN/GPa/mm² rather than SI base units.
        assert page.locator('#nodes tr').nth(2).locator('input[data-field="fy"]').input_value() == '-10'
        assert page.locator('#members tr').nth(0).locator('input[data-field="E"]').input_value() == '200'
        assert page.locator('#members tr').nth(0).locator('input[data-field="area"]').input_value() == '1000.0000000000001' or abs(float(page.locator('#members tr').nth(0).locator('input[data-field="area"]').input_value())-1000)<1e-9
        # Export CSV content in the restricted sandbox without a download navigation.
        page.evaluate('''() => { window.__exports=[]; const orig=URL.createObjectURL.bind(URL);
            URL.createObjectURL = blob => {window.__exports.push({blob});return orig(blob);};
            HTMLAnchorElement.prototype.click = function(){window.__exports.at(-1).name=this.download;}; }''')
        page.locator('#export-csv').click()
        exported = page.evaluate('''async () => ({name:window.__exports[0].name,body:await window.__exports[0].blob.text()})''')
        assert exported['name'].endswith('.csv') and 'Axial force (kN)' in exported['body']
        page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]').uncheck()
        page.locator('#solve').click()
        assert page.locator('#status.error').count() == 1
        page.locator('#export-csv').click()
        assert len(page.evaluate('window.__exports')) == 1, 'Failed analysis must not export stale results'
        page.locator('#reset').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
        assert not errors, errors
        browser.close()
    print('Truss Studio: old SI references, model migration, export, singularity, recovery and mobile PASS')


if __name__ == '__main__':
    main()
