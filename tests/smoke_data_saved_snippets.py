"""Browser regression: saved Data Tables snippets persist, rename and delete safely."""
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1280, 'height': 850})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            url = 'http://127.0.0.1:%s/index.html' % server.server_port
            page.goto(url, wait_until='load')
            page.evaluate('localStorage.clear()')
            page.reload(wait_until='load')
            page.locator('[data-workspace="data"]').click()
            lib = page.locator('#dt-code-library')
            lib.locator('summary').click()
            name = page.locator('#dt-snippet-name')
            kind = page.locator('#dt-snippet-kind')
            code = page.locator('#dt-snippet-code')
            search = page.locator('#dt-library-search')
            status = page.locator('#dt-library-message')
            name.fill('My total')
            kind.select_option('Formula')
            code.fill('=SUM(A1:A5)')
            page.get_by_role('button', name='Save snippet').click()
            assert page.get_by_role('button', name='Edit snippet My total').count() == 1
            assert 'Saved My total' in status.inner_text()
            # Editing an existing snippet can rename it, but must not duplicate it.
            search.fill('My total')
            page.get_by_role('button', name='Edit snippet My total').click()
            assert name.input_value() == 'My total'
            name.fill('Monthly total')
            code.fill('=SUM(B1:B5)')
            page.get_by_role('button', name='Update snippet').click()
            search.fill('')
            assert page.get_by_role('button', name='Edit snippet My total').count() == 0
            assert page.get_by_role('button', name='Edit snippet Monthly total').count() == 1
            assert page.evaluate("JSON.parse(localStorage.getItem('promathstudio-data-snippets-v1')).length") == 1
            # Duplicate names require an explicit Edit action.
            name.fill('Monthly total')
            code.fill('=SUM(C1:C5)')
            page.get_by_role('button', name='Save snippet').click()
            assert 'Select Edit' in status.inner_text()
            assert page.evaluate("JSON.parse(localStorage.getItem('promathstudio-data-snippets-v1'))[0].sample") == '=SUM(B1:B5)'
            # Python snippets are catalog entries, never automatically executed.
            name.fill('Filter positives')
            kind.select_option('Python')
            code.fill("result = next(iter(tables.values())).dropna()")
            page.get_by_role('button', name='Save snippet').click()
            search.fill('Filter positives')
            output_before = page.locator('#python-output-result').text_content()
            page.get_by_role('button', name='Insert Filter positives').click()
            assert 'dropna()' in page.locator('#dt-python-code').input_value()
            assert page.locator('#python-output-result').text_content() == output_before
            page.keyboard.press('Escape')
            # Cancelled deletion must preserve the catalog and storage.
            page.once('dialog', lambda dialog: dialog.dismiss())
            page.get_by_role('button', name='Delete snippet Filter positives').click()
            assert page.get_by_role('button', name='Delete snippet Filter positives').count() == 1
            page.once('dialog', lambda dialog: dialog.accept())
            page.get_by_role('button', name='Delete snippet Filter positives').click()
            assert page.get_by_role('button', name='Delete snippet Filter positives').count() == 0
            assert 'Deleted Filter positives' in status.inner_text()
            # Storage write failure must roll back in-memory edits.
            search.fill('')
            name.fill('Do not persist')
            kind.select_option('Formula')
            code.fill('=MAX(A1:A5)')
            page.evaluate("() => { window.__setItem = Storage.prototype.setItem; Storage.prototype.setItem = function(){throw Error('quota');}; }")
            page.get_by_role('button', name='Save snippet').click()
            assert 'Storage unavailable' in status.inner_text()
            assert page.get_by_role('button', name='Edit snippet Do not persist').count() == 0
            page.evaluate('() => { Storage.prototype.setItem = window.__setItem; }')
            # Browser reload retains the renamed snippet and not deleted/failed entries.
            page.reload(wait_until='load')
            page.locator('[data-workspace="data"]').click()
            page.locator('#dt-code-library summary').click()
            assert page.get_by_role('button', name='Edit snippet Monthly total').count() == 1
            assert page.get_by_role('button', name='Edit snippet Filter positives').count() == 0
            assert page.get_by_role('button', name='Edit snippet Do not persist').count() == 0
            for width in (390, 768, 1280):
                page.set_viewport_size({'width': width, 'height': 850})
                assert page.locator('#dt-snippet-save').count() == 1
                assert page.get_by_role('button', name='Delete snippet Monthly total').count() == 1
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print('PASS saved snippets create/edit/rename/delete, rollback, reload, no auto-run, responsive')


if __name__ == '__main__':
    main()
