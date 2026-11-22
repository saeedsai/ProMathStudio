"""Standalone 2D truss lab: in-browser references, negative cases, SVG visualization,
keyboard and mobile layout, import recovery, CSV/SVG output and console integrity."""
import csv
import io
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'tools' / 'truss-studio.html').read_text(encoding='utf-8')
# Test the unchanged standalone JS with inline injection to avoid file://, which is
# disallowed in some restricted CI/container browsers. Deployment keeps relative files.
HTML = HTML.replace('<script defer src="truss-fem.js"></script>', '')
HTML = HTML.replace('<script defer src="truss-fem-ui.js"></script>', '')
HTML = HTML.replace('</body>', '<script>' + (ROOT / 'tools' / 'truss-fem.js').read_text(encoding='utf-8') + '</script>'
                    + '<script>' + (ROOT / 'tools' / 'truss-fem-ui.js').read_text(encoding='utf-8') + '</script></body>')


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
            page.locator('#scale').fill('500')
            page.locator('#scale').press('Tab')
            assert '500' in page.locator('#plot').text_content()
            # About:blank contexts cannot trigger downloads in sandboxed browsers;
            # verify generated Blob bytes + filenames via the same click handlers.
            page.evaluate("""() => { window.__exports=[];
                const create=URL.createObjectURL.bind(URL);
                URL.createObjectURL = blob => {window.__exports.push({blob});return create(blob);};
                HTMLAnchorElement.prototype.click = function() { window.__exports.at(-1).name=this.download; };
            }""")
            page.get_by_role('button', name='Export results CSV').click()
            page.get_by_role('button', name='Export material schedule CSV').click()
            page.get_by_role('button', name='Export SVG').click()
            exported=page.evaluate("""async () => await Promise.all(window.__exports.map(async e => ({name:e.name,type:e.blob.type,text:await e.blob.text(),prefix:Array.from(new Uint8Array(await e.blob.slice(0,3).arrayBuffer()))})))""")
            assert exported[0]['name'] == 'promath-truss-results.csv'
            assert exported[1]['name'] == 'promath-truss-material-schedule.csv'
            assert exported[2]['name'] == 'promath-truss-deformation.svg'
            for item in exported[:2]:
                assert item['prefix'] == [239, 187, 191], item['prefix']
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
            assert sum(1 for row in result_rows if row and len(row) == 7) == 4
            material_csv = exported[1]['text'].lstrip('\ufeff')
            material_rows = list(csv.reader(io.StringIO(material_csv, newline='')))
            assert material_rows[0] == [
                'Member ID', 'Start joint ID', 'End joint ID', 'Centreline length (m)',
                'Cross-sectional area (m²)', 'Axial material volume (m³)', 'Elastic modulus (GPa)',
                'Axial stiffness EA/L (kN/mm)', 'Density (kg/m³)', 'Member mass (kg)',
                'Second moment of area I (mm⁴)', 'Effective length factor K (-)', 'Euler critical load Pcr (kN)'
            ]
            assert len(material_rows) == 4
            assert all(len(row) == 13 for row in material_rows)
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
                    solvedLines: root.querySelectorAll('line').length
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
            assert svg_metadata['solvedLines'] >= 6
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
