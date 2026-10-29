"""Data Tables import must preview validated CSV/TSV/JSON without mutation."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="data"]').click()
        page.locator('#data-menu-navigation > details').nth(3).evaluate('(e) => e.open = true')
        preview = page.locator('#dt-import-preview')
        summary = page.locator('#dt-import-preview-summary')
        schema = page.locator('#dt-import-preview-schema')
        before = page.evaluate('MathStudio.dataTables.exportState()')

        def upload(name, data):
            page.locator('#dt-import').set_input_files({
                'name': name, 'mimeType': 'application/json' if name.endswith('.json') else 'text/plain',
                'buffer': data.encode('utf-8') if isinstance(data, str) else data,
            })
            page.wait_for_function("() => document.querySelector('#dt-import').value === ''")

        upload('cancel.csv', 'Name,Value\nÅngström,1\n日本語,2\n')
        assert preview.is_visible()
        assert '2 rows, 2 columns' in summary.inner_text(), summary.inner_text()
        assert 'Name' in schema.inner_text()
        assert page.locator('#dt-import-preview-sample tbody tr').count() == 2
        assert page.evaluate('MathStudio.dataTables.exportState()') == before
        assert preview.evaluate('(e) => document.activeElement === e')
        page.keyboard.press('Escape')
        assert preview.is_hidden()
        assert page.evaluate('MathStudio.dataTables.exportState()') == before
        assert page.locator('#dt-import').evaluate('(e) => document.activeElement === e')

        # Preview strings are text, not executable markup; confirm is explicit.
        upload('unicode.json', '[{"label":"<img src=x onerror=alert(1)>","note":"日本語"},'
                               '{"label":"Ångström","note":"two\\nlines"}]')
        assert preview.is_visible()
        assert page.locator('#dt-import-preview-sample img').count() == 0
        assert '<img src=x onerror=alert(1)>' in preview.inner_text()
        assert page.evaluate('MathStudio.dataTables.exportState()') == before
        page.locator('#dt-import-confirm').click()
        page.wait_for_function("() => MathStudio.dataTables.tables.some(t => t.name === 'unicode')")
        assert preview.is_hidden()
        assert page.evaluate('MathStudio.dataTables.active.rows[0][0]') == '<img src=x onerror=alert(1)>'
        after = page.evaluate('MathStudio.dataTables.exportState()')

        upload('duplicate.csv', 'x,x\n1,2\n')
        assert preview.is_visible()
        assert 'duplicate' in schema.inner_text().lower()
        page.locator('#dt-import-cancel').click()
        assert page.evaluate('MathStudio.dataTables.exportState()') == after

        upload('broken.tsv', 'x\ty\n1\t"unclosed\n')
        page.wait_for_function('() => document.querySelector("#dt-status").textContent.includes("Import failed")')
        assert preview.is_hidden()
        assert page.evaluate('MathStudio.dataTables.exportState()') == after

        upload('huge.csv', b'x,y\n' + b'1,2\n' * 250001)
        page.wait_for_function('() => document.querySelector("#dt-status").textContent.includes("1 MB")')
        assert preview.is_hidden()
        assert page.evaluate('MathStudio.dataTables.exportState()') == after

        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            upload('responsive.csv', 'a,b\n1,2\n')
            assert preview.is_visible()
            assert page.locator('#dt-import-confirm').is_visible()
            assert page.locator('#dt-import-cancel').is_visible()
            page.locator('#dt-import-cancel').click()
            assert page.evaluate('MathStudio.dataTables.exportState()') == after
        assert not errors, errors
        browser.close()
    print('PASS Data Tables import preview, cancel, confirmation, safe text, schema, rollback and mobile')


if __name__ == '__main__':
    main()
