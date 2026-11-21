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
        # Two overlapping imports must be ordered by selection, not by File.text() completion.
        triangle_json = page.evaluate("() => ProMathTrussFEM.exportJSON(ProMathTrussFEM.examples.triangle)")
        page.evaluate("""() => {
            const read = File.prototype.text;
            window.__importReads = [];
            File.prototype.text = function() {
                const name = this.name;
                const delay = name === 'slow-invalid.json' ? 120 : 0;
                return new Promise(resolve => setTimeout(resolve, delay))
                    .then(() => read.call(this))
                    .then(value => { window.__importReads.push(name); return value; });
            };
        }""")
        page.locator('#import-model').set_input_files({'name':'slow-invalid.json','mimeType':'application/json',
                                                       'buffer':b'{bad'})
        page.locator('#import-model').set_input_files({'name':'fast-valid.json','mimeType':'application/json',
                                                       'buffer':triangle_json.encode('utf-8')})
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return window.__importReads?.length === 2 &&
                   status?.textContent.startsWith('Analysis complete') &&
                   status.getAttribute('aria-busy') === 'false';
        }""")
        assert page.evaluate('window.__importReads') == ['fast-valid.json','slow-invalid.json']
        assert 'total member length 11.21 m' in page.locator('#preview-summary').inner_text()
        assert page.locator('#member-metrics tr').count() == 3
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
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status?.textContent.includes('Analysis complete') &&
                   status.getAttribute('aria-busy') === 'false';
        }""")
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
        assert [legacy_first.nth(i).inner_text() for i in range(8)] == ['AB','A','B','2','1000','0.002','200','100']
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
        assert material_rows[0] == ['Member ID','Start joint ID','End joint ID','Centreline length (m)','Cross-sectional area (m²)','Axial material volume (m³)','Elastic modulus (GPa)','Axial stiffness EA/L (kN/mm)','Density (kg/m³)','Member mass (kg)','Second moment of area I (mm⁴)','Effective length factor K (-)','Euler critical load Pcr (kN)']
        assert material_rows[1] == ['AB','A','B','2','0.001','0.002','200','100','','','','','']
        assert material_export['body'].endswith(chr(13) + chr(10))
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
        # Optional density stays unknown until supplied; mass is volume × density in SI.
        page.locator('#example').select_option('bar')
        page.locator('#load-example').click()
        density_input = page.locator('#members tr').first.locator('input[data-field="density"]')
        assert density_input.input_value() == ''
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.count() == 13
        assert metric_cells.nth(8).inner_text() == '—' and metric_cells.nth(9).inner_text() == '—'
        assert [metric_cells.nth(i).inner_text() for i in (10,11,12)] == ['—','—','—']
        density_input.fill('7850')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(8).inner_text() == '7850'
        assert metric_cells.nth(9).inner_text() == '15.7'
        export_index = page.evaluate('window.__exports.length')
        page.locator('#export-material-csv').click()
        density_export = page.evaluate('''async index => ({name:window.__exports[index].name,body:await window.__exports[index].blob.text()})''', export_index)
        density_rows = list(csv.reader(io.StringIO(density_export['body'])))
        assert density_rows[0][8:10] == ['Density (kg/m³)','Member mass (kg)']
        assert density_rows[1][8:10] == ['7850','15.7']
        density_input.fill('')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(8).inner_text() == '—' and metric_cells.nth(9).inner_text() == '—'
        # Euler Pcr is available only when both optional I and K are supplied.
        i_input = page.locator('#members tr').first.locator('input[data-field="I"]')
        k_input = page.locator('#members tr').first.locator('input[data-field="K"]')
        i_input.fill('1000000')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        assert 'provide both I' in page.locator('#status').inner_text()
        k_input.fill('1')
        assert 'Preview ready' in page.locator('#status').inner_text()
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.count() == 13
        assert metric_cells.nth(10).inner_text() == '1000000'
        assert metric_cells.nth(11).inner_text() == '1'
        assert metric_cells.nth(12).inner_text() == '493.48'
        export_index = page.evaluate('window.__exports.length')
        page.locator('#export-material-csv').click()
        euler_export = page.evaluate('''async index => ({name:window.__exports[index].name,body:await window.__exports[index].blob.text()})''', export_index)
        euler_rows = list(csv.reader(io.StringIO(euler_export['body'])))
        assert euler_rows[0][-3:] == ['Second moment of area I (mm⁴)','Effective length factor K (-)','Euler critical load Pcr (kN)']
        assert euler_rows[1][-3:] == ['1000000','1','493.4802200544678']
        # Post-solve Euler screening is compression-only: tension and zero demand never divide.
        page.locator('#solve').click()
        result_cells = page.locator('#member-results tr').first.locator('td')
        assert result_cells.count() == 7
        assert result_cells.nth(4).inner_text() == '—' and result_cells.nth(5).inner_text() == '—'
        assert result_cells.nth(6).inner_text() == 'Tension — not applicable'
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('0')
        page.locator('#solve').click()
        result_cells = page.locator('#member-results tr').first.locator('td')
        assert result_cells.nth(4).inner_text() == '—' and result_cells.nth(5).inner_text() == '—'
        assert result_cells.nth(6).inner_text() == 'No compression demand'
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('-1')
        page.locator('#solve').click()
        result_cells = page.locator('#member-results tr').first.locator('td')
        assert 0 < float(result_cells.nth(4).inner_text().rstrip('%')) < 1
        assert abs(float(result_cells.nth(5).inner_text()) - 493.4802200544678) < 0.1
        assert result_cells.nth(6).inner_text() == 'Below ideal Euler load'
        export_index = page.evaluate('window.__exports.length')
        page.locator('#export-csv').click()
        result_export = page.evaluate('''async index => ({name:window.__exports[index].name,body:await window.__exports[index].blob.text()})''', export_index)
        result_rows = list(csv.reader(io.StringIO(result_export['body'])))
        assert result_rows[0][:7] == ['Member','Axial force (kN)','Stress (MPa)','Strain','Euler utilization (%)','Euler load ratio Pcr/Pcomp (-)','Euler assessment']
        assert result_rows[1][4] and result_rows[1][5] and result_rows[1][6] == 'Below ideal Euler load'
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('-600')
        page.locator('#solve').click()
        result_cells = page.locator('#member-results tr').first.locator('td')
        assert float(result_cells.nth(4).inner_text().rstrip('%')) > 100
        assert result_cells.nth(6).inner_text() == 'At/above ideal Euler load'
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('1')
        page.locator('#solve').click()
        k_input.fill('2')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(12).inner_text() == '123.37'
        k_input.fill('0')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        assert 'K must be positive' in page.locator('#status').inner_text()
        k_input.fill('1')
        i_input.fill('-1')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        assert 'I must be positive' in page.locator('#status').inner_text()
        i_input.fill('')
        k_input.fill('')
        assert 'Preview ready' in page.locator('#status').inner_text()
        # Negative density is rejected and cannot be exported; clearing it restores the preview.
        density_input.fill('-1')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        downloads_before_invalid = page.evaluate('window.__exports.length')
        page.locator('#export-material-csv').click()
        assert page.evaluate('window.__exports.length') == downloads_before_invalid
        assert 'density must be non-negative' in page.locator('#status').inner_text()
        density_input.fill('')
        assert 'Preview ready' in page.locator('#status').inner_text()
        # Legacy SI import keeps density and the Euler estimate physically equivalent.
        legacy_model = page.evaluate('TrussStudio.example')
        for member in legacy_model['members']:
            member['density'] = 7850
            member['I'] = 1e-6
            member['K'] = 1
        page.locator('#import-model').set_input_files({'name':'legacy-density-buckling.json','mimeType':'application/json',
                                                       'buffer':json.dumps(legacy_model).encode('utf-8')})
        page.wait_for_function("""() => document.querySelector('#status').textContent.startsWith('Analysis complete')""")
        legacy_cells = page.locator('#member-metrics tr').first.locator('td')
        assert legacy_cells.nth(8).inner_text() == '7850'
        assert legacy_cells.nth(9).inner_text() == '15.7'
        assert legacy_cells.nth(10).inner_text() == '1000000'
        assert legacy_cells.nth(11).inner_text() == '1'
        assert legacy_cells.nth(12).inner_text() == '493.48'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
        assert not errors, errors
        browser.close()
    print('Truss Studio: pre-solve geometry, validated material schedule CSV, import/export, recovery and mobile PASS')


if __name__ == '__main__':
    main()
