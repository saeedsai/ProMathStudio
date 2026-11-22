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
                        prefix:Array.from(bytes.slice(0,3)),tail:Array.from(bytes.slice(-2)),
                        emptyBytes:Array.from(new Uint8Array(await window.__exports[1].blob.arrayBuffer())),bomCount};
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
                        prefix:Array.from(bytes.slice(0,3)),bomCount};
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
            # Layout is contained even on 390px viewport; inner tables scroll independently.
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'), page.evaluate('''() => ({width: innerWidth, scroll:document.documentElement.scrollWidth, wide:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+2).slice(0,12).map(e=>[e.tagName,e.id,e.className?.baseVal||e.className,Math.round(e.getBoundingClientRect().right)])})''')
            assert not errors, errors
            page.close()
        browser.close()
    print('Truss FEM reference, validation, graphics, export, keyboard and mobile checks passed')


if __name__ == '__main__':
    main()
