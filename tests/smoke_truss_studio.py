"""Backwards-compatible truss studio: original SI reference values, CSV export and UI.
The upgraded page uses an editable table UI but retains the prior solver interface."""
from pathlib import Path
import csv
import io
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
        # Preview valid geometry without solving, including a model that is structurally unstable.
        assert page.locator('#preview-summary').get_attribute('aria-live') == 'polite'
        page.locator('#member-material-details > summary').click()
        support_y = page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]')
        support_y.focus()
        page.keyboard.press('Space')
        preview = page.locator('#preview-summary').inner_text()
        for expected in ('3 joints', '3 members', '1 connected component', '0 isolated joints',
                         'total member length 11.21 m', 'axial member volume Σ(L·A) 0.01345 m³',
                         'bounds 4 × 3 m', 'applied load', 'ΣFy -20 kN', 'not a stability check'):
            assert expected in preview, (expected, preview)
        member_rows = page.locator('#member-metrics tr')
        assert member_rows.count() == 3
        assert [member_rows.nth(0).locator('td').nth(i).inner_text() for i in range(6)] == ['AB','A','B','4','1200','0.0048']
        assert [member_rows.nth(1).locator('td').nth(i).inner_text() for i in range(6)] == ['AC','A','C','3.606','1200','0.004327']
        assert [member_rows.nth(2).locator('td').nth(i).inner_text() for i in range(6)] == ['BC','B','C','3.606','1200','0.004327']
        assert page.locator('#plot line[data-member-id]').count() == 3
        assert page.locator('#plot circle[data-node-id]').count() == 3
        assert 'Preview ready' in page.locator('#status').inner_text()
        assert page.locator('#status.error').count() == 0
        # The solver rejects this released support, but the non-solving preview remains visible.
        page.locator('#solve').click()
        assert page.locator('#status.error').count() == 1
        assert 'Unstable or under-constrained truss' in page.locator('#status').inner_text()
        assert page.locator('#plot line[data-member-id]').count() == 3
        # Invalid geometry removes stale preview; correcting the field restores it.
        node_b_x = page.locator('#nodes tr').nth(1).locator('input[data-field="x"]')
        node_b_x.fill('')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        assert page.locator('#plot line[data-member-id]').count() == 0
        assert 'Correct model inputs' in page.locator('#member-metrics').inner_text()
        node_b_x.fill('4')
        assert '3 joints' in page.locator('#preview-summary').inner_text()
        assert page.locator('#member-metrics tr').count() == 3
        page.locator('#reset').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        # Material metrics use the same SI contract for the simple analytical bar and triangle.
        page.locator('#example').select_option('bar')
        page.locator('#load-example').click()
        bar_preview = page.locator('#preview-summary').inner_text()
        assert 'total member length 2 m' in bar_preview, bar_preview
        assert 'axial member volume Σ(L·A) 0.002 m³' in bar_preview, bar_preview
        bar_row = page.locator('#member-metrics tr').first.locator('td')
        assert [bar_row.nth(i).inner_text() for i in range(6)] == ['AB','A','B','2','1000','0.002']
        page.locator('#example').select_option('triangle')
        page.locator('#load-example').click()
        triangle_preview = page.locator('#preview-summary').inner_text()
        assert 'total member length 11.21 m' in triangle_preview, triangle_preview
        assert 'axial member volume Σ(L·A) 0.01345 m³' in triangle_preview, triangle_preview
        assert page.evaluate("() => { const e=document.querySelector('#preview-summary'); return e.scrollWidth <= e.clientWidth + 1; }")
        assert page.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
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
        # Force File.text() to return a UTF-8 BOM, as some external editors include one.
        # The browser UI must use the canonical importer rather than raw JSON.parse.
        page.evaluate("""() => {
            const read = File.prototype.text;
            File.prototype.text = function() {
                return read.call(this).then(value => String.fromCharCode(0xFEFF) + value);
            };
        }""")
        page.locator('#import-model').set_input_files({'name':'legacy.json','mimeType':'application/json',
                                                      'buffer':json.dumps(prior).encode('utf-8')})
        assert 'Analysis complete' in page.locator('#status').inner_text()
        assert page.locator('#status').get_attribute('aria-busy') == 'false'
        # Normalized user controls now show kN/GPa/mm² rather than SI base units.
        assert page.locator('#nodes tr').nth(2).locator('input[data-field="fy"]').input_value() == '-10'
        assert page.locator('#members tr').nth(0).locator('input[data-field="E"]').input_value() == '200'
        assert page.locator('#members tr').nth(0).locator('input[data-field="area"]').input_value() == '1000.0000000000001' or abs(float(page.locator('#members tr').nth(0).locator('input[data-field="area"]').input_value())-1000)<1e-9
        legacy_preview = page.locator('#preview-summary').inner_text()
        assert 'total member length 4.828 m' in legacy_preview, legacy_preview
        assert 'axial member volume Σ(L·A) 0.004828 m³' in legacy_preview, legacy_preview
        assert 'bounds 2 × 1 m' in legacy_preview, legacy_preview
        legacy_rows = page.locator('#member-metrics tr')
        assert legacy_rows.count() == 3
        legacy_first = legacy_rows.first.locator('td')
        assert [legacy_first.nth(i).inner_text() for i in range(6)] == ['AB','A','B','2','1000','0.002']
        # Capture Blob downloads without navigating away from the standalone tool.
        page.evaluate('''() => { window.__exports=[]; const orig=URL.createObjectURL.bind(URL);
            URL.createObjectURL = blob => {window.__exports.push({blob});return orig(blob);};
            HTMLAnchorElement.prototype.click = function(){window.__exports.at(-1).name=this.download;}; }''')
        page.locator('#export-model').click()
        model_export = page.evaluate('''async () => ({name:window.__exports[0].name,body:await window.__exports[0].blob.text()})''')
        assert model_export['name'].endswith('.json')
        exported_model = json.loads(model_export['body'])
        assert abs(float(exported_model['members'][0]['area']) - 1000) < 1e-9
        # Invalid edits must not produce a JSON file that cannot be imported again.
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('')
        page.locator('#export-model').click()
        assert page.locator('#status.error').count() == 1
        assert len(page.evaluate('window.__exports')) == 1, 'Invalid model must not be exported'
        page.locator('#export-material-csv').click()
        assert len(page.evaluate('window.__exports')) == 1, 'Invalid model must not produce a material schedule'
        assert 'Material schedule export failed' in page.locator('#status').inner_text()
        # Restore a valid model but do not solve: material scheduling is a pre-solve workflow.
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('0')
        page.locator('#export-material-csv').focus()
        page.keyboard.press('Enter')
        material_export = page.evaluate('''async () => ({name:window.__exports[1].name,body:await window.__exports[1].blob.text()})''')
        assert material_export['name'] == 'promath-truss-material-schedule.csv'
        material_rows = list(csv.reader(io.StringIO(material_export['body'])))
        assert material_rows[0] == ['Member ID','Start joint ID','End joint ID','Centreline length (m)','Cross-sectional area (m²)','Axial material volume (m³)']
        assert material_rows[1] == ['AB','A','B','2','0.001','0.002']
        assert material_export['body'].endswith('\\r\\n')
        assert 'Validated member material schedule exported.' in page.locator('#status').inner_text()
        page.locator('#solve').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        # A malformed import must preserve the currently edited model.
        # Hold File.text() open to verify the UI announces pending work before validation settles.
        page.evaluate('''() => {
            const read = File.prototype.text;
            let release;
            const gate = new Promise(resolve => { release = resolve; });
            window.__releaseInvalidImport = release;
            File.prototype.text = function() {
                const pending = read.call(this);
                return this.name === 'invalid.json' ? gate.then(() => pending) : pending;
            };
        }''')
        page.locator('#import-model').set_input_files({'name':'invalid.json','mimeType':'application/json',
                                                      'buffer':b'{bad'})
        assert page.locator('#status').inner_text() == 'Importing model…'
        assert page.locator('#status').get_attribute('aria-busy') == 'true'
        page.evaluate('window.__releaseInvalidImport()')
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status.classList.contains('error') && status.getAttribute('aria-busy') === 'false';
        }""")
        assert page.locator('#status.error').count() == 1
        assert page.locator('#nodes tr').count() == 3
        assert page.locator('#nodes tr').nth(2).locator('input[data-field="fy"]').input_value() == '-10'
        page.locator('#solve').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        page.locator('#export-csv').click()
        exported = page.evaluate('''async () => ({name:window.__exports[2].name,body:await window.__exports[2].blob.text()})''')
        assert exported['name'].endswith('.csv') and 'Axial force (kN)' in exported['body']
        page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]').uncheck()
        page.locator('#solve').click()
        assert page.locator('#status.error').count() == 1
        page.locator('#export-csv').click()
        assert len(page.evaluate('window.__exports')) == 3, 'Failed analysis must not export stale results'
        page.locator('#reset').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
        assert not errors, errors
        browser.close()
    print('Truss Studio: pre-solve geometry, validated material schedule CSV, import/export, recovery and mobile PASS')


if __name__ == '__main__':
    main()
