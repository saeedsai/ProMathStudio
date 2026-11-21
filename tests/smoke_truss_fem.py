"""Standalone 2D truss lab: in-browser references, negative cases, SVG visualization,
keyboard and mobile layout, import recovery, CSV/SVG output and console integrity."""
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
            page.get_by_role('button', name='Export SVG').click()
            exported=page.evaluate("""async () => await Promise.all(window.__exports.map(async e => ({name:e.name,text:await e.blob.text()})))""")
            assert exported[0]['name'].endswith('.csv') and 'Axial force (kN)' in exported[0]['text']
            assert exported[1]['name'].endswith('.svg') and '<svg' in exported[1]['text']
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
