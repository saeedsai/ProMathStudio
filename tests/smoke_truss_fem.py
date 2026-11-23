"""Standalone 2D truss lab: in-browser references, negative cases, SVG visualization,
keyboard and mobile layout, import recovery, CSV/SVG output and console integrity."""
import csv
import io
import json
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'tools' / 'truss-studio.html').read_text(encoding='utf-8')
# Test the unchanged standalone JS with inline injection to avoid file://, which is
# disallowed in some restricted CI/container browsers. Deployment keeps relative files.
HTML = HTML.replace('<script defer src="truss-fem.js"></script>', '')
HTML = HTML.replace('<script defer src="truss-fem-ui.js"></script>', '')
FEM_JS = (ROOT / 'tools' / 'truss-fem.js').read_text(encoding='utf-8')
UI_JS = (ROOT / 'tools' / 'truss-fem-ui.js').read_text(encoding='utf-8')
# Expose the private CSV helper only in this injected test copy; production keeps it scoped.
UI_JS = UI_JS.replace('  updateSectionShape();',
                      '  window.__testDownloadCsv = downloadCsv;\n  updateSectionShape();', 1)
assert 'window.__testDownloadCsv = downloadCsv;' in UI_JS
HTML = HTML.replace('</body>', '<script>' + FEM_JS + '</script>'
                    + '<script>' + UI_JS + '</script></body>')


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        for width in (1280, 390):
            page = browser.new_page(viewport={'width': width, 'height': 900}, accept_downloads=True,
                                    reduced_motion='reduce')
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            page.set_content(HTML, wait_until='load')
            page.locator('#status').wait_for()
            assert 'Analysis complete' in page.locator('#status').inner_text(), page.locator('#status').inner_text()
            assert 'mm' in page.locator('#disp-card').inner_text()
            assert page.locator('#plot line').count() >= 6
            assert page.locator('#member-results tr').count() == 3
            assert page.locator('#joint-results tr').count() == 3
            assert page.locator('#reactions tr').count() == 2
            results = page.evaluate('''() => { const r=ProMathTrussFEM.solve(ProMathTrussFEM.examples.triangle);
              return [r.reactions[0].ry,r.reactions[1].ry,r.maxDisplacement.magnitude,r.residual,r.energyError]; }''')
            assert abs(results[0] - 10000) < 1e-6 and abs(results[1] - 10000) < 1e-6
            assert results[2] > 0 and results[3] < 1e-10 and results[4] < 1e-10
            # Simulate an underconstrained joint, then recover without page reload.
            page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]').uncheck()
            page.get_by_role('button', name='Analyze truss').click()
            assert page.locator('#status.error').count() == 1
            page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]').check()
            page.get_by_role('button', name='Analyze truss').click()
            assert 'Analysis complete' in page.locator('#status').inner_text()
            assert '[object' not in page.locator('#status').inner_text()
            page.locator('#scale').fill('500')
            page.locator('#scale').press('Tab')
            assert '500' in page.locator('#plot').text_content()
            # Capture the actual generated download Blobs for a UI-level JSON round-trip.
            page.evaluate("""() => { window.__exports=[];
                const create=URL.createObjectURL.bind(URL);
                URL.createObjectURL = blob => {window.__exports.push({blob});return create(blob);};
                HTMLAnchorElement.prototype.click = function() { window.__exports.at(-1).name=this.download; };
            }""")
            legacy_model = {
                'nodes': [
                    {'id': 'A', 'x': 0, 'y': 0, 'fixX': True, 'fixY': True, 'fx': 0, 'fy': 0},
                    {'id': 'B', 'x': 2, 'y': 0, 'fixX': False, 'fixY': True, 'fx': 1000, 'fy': 0}
                ],
                'members': [
                    {'id': 'AB', 'a': 'A', 'b': 'B', 'E': 200e9, 'A': 0.001,
                     'density': 7850, 'I': 1e-6, 'K': 1}
                ]
            }
            page.locator('#import-model').set_input_files({
                'name': 'legacy-truss.json', 'mimeType': 'application/json',
                'buffer': json.dumps(legacy_model).encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent.includes(
                'Legacy SI input converted to Studio units.')""")
            assert 'Optional property units in file: density kg/m³, I m⁴, K dimensionless.' in page.locator('#status').inner_text()
            assert page.locator('#nodes tr').count() == 2
            assert page.locator('#members tr').count() == 1
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').input_value() == '1'
            legacy_row = page.locator('#members tr').first
            assert legacy_row.locator('input[data-field="E"]').input_value() == '200'
            assert legacy_row.locator('input[data-field="area"]').input_value() == '1000'
            assert legacy_row.locator('input[data-field="density"]').input_value() == '7850'
            assert legacy_row.locator('input[data-field="I"]').input_value() == '1000000'
            assert legacy_row.locator('input[data-field="K"]').input_value() == '1'
            assert '0.01 mm' in page.locator('#disp-card').inner_text()

            page.get_by_role('button', name='Export JSON').click()
            current_export = page.evaluate("""async () => {
                const item=window.__exports.at(-1);
                return {name:item.name,type:item.blob.type,text:await item.blob.text()};
            }""")
            assert current_export['name'] == 'promath-truss-model.json'
            assert current_export['type'] == 'application/json;charset=utf-8'
            studio_model = json.loads(current_export['text'])
            assert float(studio_model['nodes'][1]['fx']) == 1
            assert float(studio_model['members'][0]['E']) == 200
            assert float(studio_model['members'][0]['area']) == 1000
            assert float(studio_model['members'][0]['density']) == 7850
            assert float(studio_model['members'][0]['I']) == 1000000
            assert float(studio_model['members'][0]['K']) == 1

            page.locator('#import-model').set_input_files({
                'name': 'studio-roundtrip.json', 'mimeType': 'application/json',
                'buffer': current_export['text'].encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent.includes(
                'Studio units retained from file.')""")
            assert 'Optional property units in file: density kg/m³, I mm⁴, K dimensionless.' in page.locator('#status').inner_text()
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').input_value() == '1'
            studio_row = page.locator('#members tr').first
            assert studio_row.locator('input[data-field="E"]').input_value() == '200'
            assert studio_row.locator('input[data-field="area"]').input_value() == '1000'
            assert studio_row.locator('input[data-field="density"]').input_value() == '7850'
            assert studio_row.locator('input[data-field="I"]').input_value() == '1000000'
            assert studio_row.locator('input[data-field="K"]').input_value() == '1'
            displacement_before_rejection = page.locator('#disp-card').inner_text()

            mixed_model = json.loads(json.dumps(legacy_model))
            mixed_model['members'][0]['area'] = 1000
            page.locator('#import-model').set_input_files({
                'name': 'mixed-units.json', 'mimeType': 'application/json',
                'buffer': json.dumps(mixed_model).encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').classList.contains('error')""")
            assert 'Mixed legacy SI and current' in page.locator('#status').inner_text()
            assert page.locator('#nodes tr').count() == 2
            assert page.locator('#members tr').count() == 1
            assert page.locator('#members tr').first.locator('input[data-field="E"]').input_value() == '200'
            assert page.locator('#members tr').first.locator('input[data-field="area"]').input_value() == '1000'
            assert page.locator('#members tr').first.locator('input[data-field="density"]').input_value() == '7850'
            assert page.locator('#members tr').first.locator('input[data-field="I"]').input_value() == '1000000'
            assert page.locator('#members tr').first.locator('input[data-field="K"]').input_value() == '1'
            assert page.locator('#disp-card').inner_text() == displacement_before_rejection
            page.evaluate("window.__exports=[]")
            # Reset captured downloads before the CSV and SVG export assertions.
            page.evaluate('window.__exports=[]')
            page.get_by_role('button', name='Export results CSV').click()
            page.get_by_role('button', name='Export material schedule CSV').click()
            page.get_by_role('button', name='Export SVG').click()
            exported=page.evaluate("""async () => await Promise.all(window.__exports.map(async e => {
                const bytes = new Uint8Array(await e.blob.arrayBuffer());
                let bomCount=0;
                for(let i=0;i<=bytes.length-3;i++) {
                    if(bytes[i]===239&&bytes[i+1]===187&&bytes[i+2]===191) bomCount++;
                }
                return {name:e.name,type:e.blob.type,text:await e.blob.text(),
                        prefix:Array.from(bytes.slice(0,3)),bomCount};
            }))""")
            assert exported[0]['name'] == 'promath-truss-results.csv'
            assert exported[1]['name'] == 'promath-truss-material-schedule.csv'
            assert exported[2]['name'] == 'promath-truss-deformation.svg'
            for item in exported[:2]:
                assert item['prefix'] == [239, 187, 191], item['prefix']
                assert item['bomCount'] == 1, item['bomCount']
                content = item['text'].lstrip('\ufeff')
                assert content.endswith('\r\n')
                without_crlf = content.replace('\r\n', '')
                assert '\r' not in without_crlf and '\n' not in without_crlf
            result_csv = exported[0]['text'].lstrip('\ufeff')
            result_rows = list(csv.reader(io.StringIO(result_csv, newline='')))
            assert result_rows[0] == ['Member', 'Axial force (kN)', 'Stress (MPa)', 'Strain',
                                      'Euler utilization (%)', 'Euler load ratio Pcr/Pcomp (-)', 'Euler assessment']
            assert ['Joint', 'Ux (mm)', 'Uy (mm)'] in result_rows
            assert ['Support', 'Rx (kN)', 'Ry (kN)'] in result_rows
            assert sum(1 for row in result_rows if not row) == 2
            assert all(len(row) in (3, 7) for row in result_rows if row)
            member_rows = [row for row in result_rows if row and len(row) == 7]
            assert len(member_rows) == 2, member_rows  # header plus the imported AB member
            assert member_rows[1][0] == 'AB'
            assert abs(float(member_rows[1][1]) - 1.0) < 1e-12
            assert abs(float(member_rows[1][2]) - 1.0) < 1e-12
            material_csv = exported[1]['text'].lstrip('\ufeff')
            material_rows = list(csv.reader(io.StringIO(material_csv, newline='')))
            assert material_rows[0] == [
                'Member ID', 'Start joint ID', 'End joint ID', 'Centreline length (m)',
                'Cross-sectional area (m²)', 'Axial material volume (m³)', 'Elastic modulus (GPa)',
                'Axial stiffness EA/L (kN/mm)', 'Density (kg/m³)', 'Member mass (kg)',
                'Second moment of area I (mm⁴)', 'Effective length factor K (-)', 'Euler critical load Pcr (kN)'
            ]
            assert len(material_rows) == 2  # header plus the imported AB member
            assert all(len(row) == 13 for row in material_rows)
            assert material_rows[1][:3] == ['AB', 'A', 'B']
            assert float(material_rows[1][3]) == 2.0
            assert abs(float(material_rows[1][4]) - 0.001) < 1e-15  # schedule is SI m², not editor mm²
            assert abs(float(material_rows[1][5]) - 0.002) < 1e-15  # 2 m × 0.001 m²
            assert abs(float(material_rows[1][7]) - 100.0) < 1e-12  # EA/L in kN/mm
            assert abs(float(material_rows[1][9]) - 15.7) < 1e-12  # SI density × volume
            assert float(material_rows[1][6]) == 200.0
            assert float(material_rows[1][8]) == 7850.0
            assert float(material_rows[1][10]) == 1000000.0
            assert float(material_rows[1][11]) == 1.0
            svg_metadata = page.evaluate("""text => {
                const document = new DOMParser().parseFromString(text, 'image/svg+xml');
                const root = document.documentElement;
                const title = root.querySelector(':scope > title');
                const description = root.querySelector(':scope > desc');
                const labels = (root.getAttribute('aria-labelledby') || '').split(/\\s+/).filter(Boolean);
                const ids = new Set([...root.querySelectorAll('[id]')].map(node => node.id));
                return {
                    parseError: Boolean(document.querySelector('parsererror')),
                    namespace: root.namespaceURI,
                    width: root.getAttribute('width'),
                    height: root.getAttribute('height'),
                    viewBox: root.getAttribute('viewBox'),
                    preserveAspectRatio: root.getAttribute('preserveAspectRatio'),
                    role: root.getAttribute('role'),
                    labels,
                    labelsResolve: labels.length === 2 && labels.every(id => ids.has(id)),
                    titleId: title?.id || '',
                    title: title?.textContent || '',
                    descriptionId: description?.id || '',
                    description: description?.textContent || '',
                    firstChildren: [...root.children].slice(0, 3).map(node => node.localName),
                    background: root.querySelector(':scope > rect')?.getAttribute('fill') || '',
                    solvedLines: root.querySelectorAll('line').length,
                    geometry: [...root.querySelectorAll('line[data-geometry-role]')].map(line => ({
                        role: line.getAttribute('data-geometry-role'),
                        memberId: line.getAttribute('data-member-id'),
                        nodeId: line.getAttribute('data-node-id'),
                        forceState: line.getAttribute('data-force-state'),
                        loadFxKn: line.getAttribute('data-force-x-kN'),
                        loadFyKn: line.getAttribute('data-force-y-kN'),
                        arrowheadIndex: line.getAttribute('data-arrowhead-index')
                    })),
                    unclassifiedLines: root.querySelectorAll('line:not([data-geometry-role])').length
                };
            }""", exported[2]['text'])
            assert not svg_metadata['parseError'], svg_metadata
            assert svg_metadata['namespace'] == 'http://www.w3.org/2000/svg'
            assert (svg_metadata['width'], svg_metadata['height']) == ('1240', '760')
            assert svg_metadata['viewBox'] == '0 0 620 380'
            assert svg_metadata['preserveAspectRatio'] == 'xMidYMid meet'
            assert exported[2]['type'] == 'image/svg+xml;charset=utf-8'
            assert svg_metadata['role'] == 'img'
            assert svg_metadata['labels'] == ['truss-export-title', 'truss-export-description']
            assert svg_metadata['labelsResolve']
            assert svg_metadata['titleId'] == 'truss-export-title'
            assert svg_metadata['title'] == 'ProMathStudio truss deformation analysis'
            assert svg_metadata['descriptionId'] == 'truss-export-description'
            assert 'original truss members' in svg_metadata['description']
            assert 'tension or compression' in svg_metadata['description']
            assert svg_metadata['firstChildren'] == ['title', 'desc', 'rect']
            assert svg_metadata['background'] == '#09152a'
            assert svg_metadata['solvedLines'] == 5, svg_metadata
            assert svg_metadata['unclassifiedLines'] == 0, svg_metadata
            assert svg_metadata['geometry'] == [
                {'role':'original-member','memberId':'AB','nodeId':None,'forceState':None,
                 'loadFxKn':None,'loadFyKn':None,'arrowheadIndex':None},
                {'role':'deformed-member','memberId':'AB','nodeId':None,'forceState':'tension',
                 'loadFxKn':None,'loadFyKn':None,'arrowheadIndex':None},
                {'role':'applied-load','memberId':None,'nodeId':'B','forceState':None,
                 'loadFxKn':'1','loadFyKn':'0','arrowheadIndex':None},
                {'role':'load-arrowhead','memberId':None,'nodeId':'B','forceState':None,
                 'loadFxKn':None,'loadFyKn':None,'arrowheadIndex':'1'},
                {'role':'load-arrowhead','memberId':None,'nodeId':'B','forceState':None,
                 'loadFxKn':None,'loadFyKn':None,'arrowheadIndex':'2'}
            ], svg_metadata
            # Exercise the actual private CSV helper with an existing BOM and mixed newline styles.
            page.evaluate("""() => {
                window.__exports=[];
                window.__testDownloadCsv('serializer-normalization.csv',
                    '\\uFEFFh1,h2\\n1,2\\r3,4','text/csv;charset=utf-8');
                window.__testDownloadCsv('empty.csv','','text/csv;charset=utf-8');
            }""")
            normalized_csv = page.evaluate("""async () => {
                const item=window.__exports[0];
                const bytes=new Uint8Array(await item.blob.arrayBuffer());
                let bomCount=0;
                for(let i=0;i<=bytes.length-3;i++) {
                    if(bytes[i]===239&&bytes[i+1]===187&&bytes[i+2]===191) bomCount++;
                }
                return {name:item.name,type:item.blob.type,text:await item.blob.text(),
                        prefix:Array.from(bytes.slice(0,3)),tail:Array.from(bytes.slice(-2)),
                        emptyBytes:Array.from(new Uint8Array(await window.__exports[1].blob.arrayBuffer())),bomCount};
            }""")
            assert normalized_csv['name'] == 'serializer-normalization.csv'
            assert normalized_csv['type'] == 'text/csv;charset=utf-8'
            assert normalized_csv['prefix'] == [239, 187, 191]
            assert normalized_csv['bomCount'] == 1
            assert normalized_csv['tail'] == [13, 10], normalized_csv['tail']
            assert normalized_csv['emptyBytes'] == [239, 187, 191], normalized_csv['emptyBytes']
            assert normalized_csv['text'] == 'h1,h2\r\n1,2\r\n3,4\r\n'
            page.locator('#example').select_option('bar')
            page.get_by_role('button', name='Load example').click()
            assert page.locator('#member-results tr').count() == 1
            assert abs(page.evaluate('ProMathTrussFEM.solve(ProMathTrussFEM.examples.bar).displacements[1].x') - 1e-5) < 1e-12

            # Section properties apply atomically to one selected member only.
            page.locator('#example').select_option('triangle')
            page.get_by_role('button', name='Load example').click()
            assert page.locator('#members tr').count() == 3
            # The helper is intentionally inside the collapsed material-breakdown details.
            page.locator('#member-material-details > summary').click()
            assert page.locator('#section-helper').is_visible()

            def section_member_snapshot():
                return page.evaluate("""() => [...document.querySelectorAll('#members tr')].map(tr =>
                    Object.fromEntries([...tr.querySelectorAll('input[data-field]')].map(input =>
                        [input.dataset.field, input.type === 'checkbox' ? input.checked : input.value])))""")

            distinct_member_values = [
                {'E': '190', 'area': '1100', 'density': '7800', 'I': '111000', 'K': '0.9'},
                {'E': '200', 'area': '1200', 'density': '7850', 'I': '222000', 'K': '1.1'},
                {'E': '210', 'area': '1300', 'density': '7900', 'I': '333000', 'K': '1.2'}
            ]
            for index, values in enumerate(distinct_member_values):
                row = page.locator('#members tr').nth(index)
                for field, value in values.items():
                    row.locator(f'input[data-field="{field}"]').fill(value)

            section_target = page.locator('#members tr').nth(1).locator('input[data-field="id"]').input_value()
            other_member_id = page.locator('#members tr').nth(2).locator('input[data-field="id"]').input_value()

            # Duplicate IDs make a target ambiguous; applying properties must not pick
            # the first matching row or modify any member until the ID is unique again.
            page.locator('#members tr').nth(2).locator('input[data-field="id"]').fill(section_target)
            page.locator('#section-member').select_option(section_target)
            section_before_ambiguous = section_member_snapshot()
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text() == (
                'Not applied: Selected member ID is ambiguous.')
            assert section_member_snapshot() == section_before_ambiguous
            page.locator('#members tr').nth(2).locator('input[data-field="id"]').fill(other_member_id)
            page.locator('#section-member').select_option(section_target)
            page.locator('#section-shape').select_option('rectangle')
            page.locator('#section-axis').select_option('width')
            page.locator('#section-width').fill('40')
            page.locator('#section-height').fill('60')
            section_before_invalid_axis = section_member_snapshot()
            invalid_axis_value = page.locator('#section-axis').evaluate(
                "(select) => { select.value = 'unsupported-axis'; return select.value; }")
            assert invalid_axis_value == ''
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text() == (
                'Not applied: Choose a valid section axis.')
            assert section_member_snapshot() == section_before_invalid_axis
            page.locator('#section-axis').select_option('width')
            section_before = section_member_snapshot()
            page.locator('#section-properties-apply').click()
            section_after = section_member_snapshot()
            assert section_after[1]['area'] == '2400', section_after
            assert section_after[1]['I'] == '720000', section_after
            for field, value in section_before[1].items():
                if field not in ('area', 'I'):
                    assert section_after[1][field] == value, (field, section_before, section_after)
            assert section_after[0] == section_before[0]
            assert section_after[2] == section_before[2]
            assert f'applied to member {section_target}.' in page.locator('#section-result').inner_text()

            # Invalid and overflowing geometry must leave every member unchanged.
            section_before_invalid = section_member_snapshot()
            page.locator('#section-width').fill('0')
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith(
                'Not applied: Rectangle width and depth must be positive.')
            assert section_member_snapshot() == section_before_invalid
            page.locator('#section-width').fill('1e308')
            page.locator('#section-height').fill('1e308')
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith('Not applied:')
            assert section_member_snapshot() == section_before_invalid

            # If either destination field is absent, preflight prevents a partial write.
            page.locator('#section-width').fill('40')
            page.locator('#section-height').fill('60')
            section_before_missing_field = section_member_snapshot()
            page.evaluate("""memberId => {
                const row = [...document.querySelectorAll('#members tr')].find(tr =>
                    tr.querySelector('input[data-field="id"]')?.value.trim() === memberId);
                row.querySelector('input[data-field="I"]').remove();
            }""", section_target)
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text() == (
                'Not applied: Selected member row is missing area and I fields.')
            section_after_missing_field = section_member_snapshot()
            assert 'I' not in section_after_missing_field[1]
            assert section_after_missing_field[1]['area'] == section_before_missing_field[1]['area']
            for field in ('id', 'a', 'b', 'E', 'density', 'K'):
                assert section_after_missing_field[1][field] == section_before_missing_field[1][field]
            assert section_after_missing_field[0] == section_before_missing_field[0]
            assert section_after_missing_field[2] == section_before_missing_field[2]

            # Restore a clean one-member model for the subsequent asynchronous import tests.
            page.locator('#example').select_option('bar')
            page.get_by_role('button', name='Load example').click()
            # A pending file import must not overwrite edits made to the active model.
            slow_model = {
                'nodes': [
                    {'id': 'S', 'x': 0, 'y': 0, 'fixX': True, 'fixY': True, 'fx': 0, 'fy': 0},
                    {'id': 'T', 'x': 4, 'y': 0, 'fixX': False, 'fixY': True, 'fx': 1, 'fy': 0}
                ],
                'members': [{'id': 'ST', 'a': 'S', 'b': 'T', 'E': 200, 'area': 1000}]
            }
            page.evaluate("""() => {
                const original = File.prototype.arrayBuffer;
                window.__slowImportSettled = false;
                window.__releaseSlowImport = null;
                File.prototype.arrayBuffer = function() {
                    if (this.name !== 'delayed-import.json') return original.call(this);
                    const file = this;
                    return new Promise((resolve, reject) => {
                        window.__releaseSlowImport = () => {
                            File.prototype.arrayBuffer = original;
                            return original.call(file).then(bytes => {
                                window.__slowImportSettled = true;
                                resolve(bytes);
                            }, reject);
                        };
                    });
                };
            }""")
            page.locator('#import-model').set_input_files({
                'name': 'delayed-import.json', 'mimeType': 'application/json',
                'buffer': json.dumps(slow_model).encode('utf-8')
            })
            page.wait_for_function("window.__releaseSlowImport !== null")
            edited_length = page.locator('#nodes tr').nth(1).locator('input[data-field="x"]')
            edited_length.fill('3')
            # Repeated input/change invalidations must not erase the cancellation notice.
            edited_length.dispatch_event('change')
            assert 'Pending import cancelled because the model was edited.' in page.locator('#status').inner_text()
            assert page.locator('#status').get_attribute('aria-busy') == 'false'
            page.evaluate('window.__releaseSlowImport()')
            page.wait_for_function('window.__slowImportSettled === true')
            page.wait_for_timeout(20)
            assert [page.locator('#nodes tr').nth(i).locator('input[data-field="id"]').input_value()
                    for i in range(2)] == ['A', 'B']
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="x"]').input_value() == '3'
            assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'AB'
            assert 'Pending import cancelled because the model was edited.' in page.locator('#status').inner_text()
            page.get_by_role('button', name='Analyze truss').click()
            assert 'Analysis complete' in page.locator('#status').inner_text()
            assert '0.015 mm' in page.locator('#disp-card').inner_text()

            # File metadata and the actual bytes returned by the browser must agree.
            # The truncated payload is still valid JSON (only trailing whitespace is omitted),
            # so a parser-only check would silently accept it and replace the active model.
            mismatched_payload = (json.dumps(slow_model) + '          ').encode('utf-8')
            # Use a real File with immutable, correct size metadata. Override only this
            # instance's read method so the test deterministically simulates a short read
            # without changing File.prototype state left by earlier import-race coverage.
            page.evaluate("""payload => {
                const input = document.querySelector('#import-model');
                const file = new File([payload], 'mismatched-size.json', {type:'application/json'});
                const nativeRead = Blob.prototype.arrayBuffer;
                window.__mismatchRead = null;
                Object.defineProperty(file, 'arrayBuffer', {
                    configurable: true,
                    value: function() {
                        return nativeRead.call(this).then(bytes => {
                            window.__mismatchRead = {
                                name: this.name,
                                declared: this.size,
                                returned: bytes.byteLength - 10
                            };
                            return bytes.slice(0, bytes.byteLength - 10);
                        });
                    }
                });
                const transfer = new DataTransfer();
                transfer.items.add(file);
                input.files = transfer.files;
                input.dispatchEvent(new Event('change', {bubbles:true}));
            }""", mismatched_payload.decode('utf-8'))
            page.wait_for_function("""() => {
                const status = document.querySelector('#status');
                return window.__mismatchRead !== null &&
                       status?.textContent.includes('Model JSON file size does not match the bytes read.');
            }""")
            mismatch_read = page.evaluate('window.__mismatchRead')
            assert mismatch_read == {
                'name': 'mismatched-size.json',
                'declared': len(mismatched_payload),
                'returned': len(mismatched_payload) - 10
            }, mismatch_read
            mismatch_status = page.locator('#status').inner_text()
            assert mismatch_status.startswith(
                'Import failed: Model JSON file size does not match the bytes read. ('
            ), mismatch_status
            assert mismatch_status.endswith(
                f'(expected {len(mismatched_payload)} bytes, received '
                f'{len(mismatched_payload) - 10} bytes).'
            ), mismatch_status
            assert [page.locator('#nodes tr').nth(i).locator('input[data-field="id"]').input_value()
                    for i in range(2)] == ['A', 'B']
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="x"]').input_value() == '3'
            assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'AB'
            assert '0.015 mm' in page.locator('#disp-card').inner_text()

            # A newer file selection must win even when an older read resolves or rejects later.
            def race_model(prefix, length=2.0, load=1.0):
                return {
                    'nodes': [
                        {'id': prefix + '-A', 'x': 0, 'y': 0, 'fixX': True, 'fixY': True, 'fx': 0, 'fy': 0},
                        {'id': prefix + '-B', 'x': length, 'y': 0, 'fixX': False, 'fixY': True, 'fx': load, 'fy': 0}
                    ],
                    'members': [{'id': prefix + '-AB', 'a': prefix + '-A', 'b': prefix + '-B', 'E': 200, 'area': 1000}]
                }

            def start_delayed_import(name, model, key):
                page.evaluate("""({name, payload, key}) => {
                    const file = new File([payload], name, {type:'application/json'});
                    const nativeRead = Blob.prototype.arrayBuffer;
                    const pending = window[key] = {settled:false, release:null, reject:null};
                    Object.defineProperty(file, 'arrayBuffer', {
                        configurable:true,
                        value:function() {
                            const target = this;
                            return new Promise((resolve, reject) => {
                                pending.release = () => nativeRead.call(target).then(bytes => {
                                    pending.settled = true;
                                    resolve(bytes);
                                }, error => {
                                    pending.settled = true;
                                    reject(error);
                                });
                                pending.reject = error => {
                                    pending.settled = true;
                                    reject(error);
                                };
                            });
                        }
                    });
                    const transfer = new DataTransfer();
                    transfer.items.add(file);
                    const input = document.querySelector('#import-model');
                    input.files = transfer.files;
                    input.dispatchEvent(new Event('change', {bubbles:true}));
                }""", {'name': name, 'payload': json.dumps(model), 'key': key})
                page.wait_for_function(f"window.{key}.release !== null && window.{key}.reject !== null")

            def assert_race_model(prefix):
                assert page.locator('#nodes tr').nth(0).locator('input[data-field="id"]').input_value() == prefix + '-A'
                assert page.locator('#nodes tr').nth(1).locator('input[data-field="id"]').input_value() == prefix + '-B'
                assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == prefix + '-AB'
                assert 'Analysis complete' in page.locator('#status').inner_text()
                assert page.locator('#status').get_attribute('aria-busy') == 'false'
                assert page.locator('#disp-card').inner_text().strip()

            # Older successful read after a newer successful import is ignored.
            start_delayed_import('older-success.json', race_model('OLD-SUCCESS', length=5), '__staleSuccess')
            page.locator('#import-model').set_input_files({
                'name': 'latest-success.json', 'mimeType': 'application/json',
                'buffer': json.dumps(race_model('LATEST-SUCCESS')).encode('utf-8')
            })
            page.wait_for_function("document.querySelector('#status')?.textContent.includes('Analysis complete')")
            assert_race_model('LATEST-SUCCESS')
            latest_success_status = page.locator('#status').inner_text()
            latest_success_result = page.locator('#disp-card').inner_text()
            page.evaluate('window.__staleSuccess.release()')
            page.wait_for_function('window.__staleSuccess.settled === true')
            page.wait_for_timeout(20)
            assert_race_model('LATEST-SUCCESS')
            assert page.locator('#status').inner_text() == latest_success_status
            assert page.locator('#disp-card').inner_text() == latest_success_result

            # An older rejected read after a newer successful import cannot replace its status.
            start_delayed_import('older-failure.json', race_model('OLD-FAILURE', length=6), '__staleFailure')
            page.locator('#import-model').set_input_files({
                'name': 'latest-after-failure.json', 'mimeType': 'application/json',
                'buffer': json.dumps(race_model('LATEST-AFTER-FAILURE', length=3)).encode('utf-8')
            })
            page.wait_for_function("document.querySelector('#status')?.textContent.includes('Analysis complete')")
            assert_race_model('LATEST-AFTER-FAILURE')
            latest_failure_status = page.locator('#status').inner_text()
            latest_failure_result = page.locator('#disp-card').inner_text()
            page.evaluate("window.__staleFailure.reject(new Error('deliberately stale read failure'))")
            page.wait_for_function('window.__staleFailure.settled === true')
            page.wait_for_timeout(20)
            assert_race_model('LATEST-AFTER-FAILURE')
            assert page.locator('#status').inner_text() == latest_failure_status
            assert page.locator('#disp-card').inner_text() == latest_failure_result

            # Layout is contained even on 390px viewport; inner tables scroll independently.
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'), page.evaluate('''() => ({width: innerWidth, scroll:document.documentElement.scrollWidth, wide:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+2).slice(0,12).map(e=>[e.tagName,e.id,e.className?.baseVal||e.className,Math.round(e.getBoundingClientRect().right)])})''')
            assert not errors, errors
            page.close()
        browser.close()
    print('Truss FEM reference, validation, graphics, export, keyboard and mobile checks passed')


if __name__ == '__main__':
    main()
