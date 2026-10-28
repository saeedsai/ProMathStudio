"""Chromium: saved snippets can be inspected fully without execution or mutation."""
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
            browser = pw.chromium.launch(headless=True,
                executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':1280,'height':850})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto('http://127.0.0.1:%s/index.html' % server.server_port, wait_until='load')
            page.evaluate('localStorage.clear()')
            page.reload(wait_until='load')
            page.locator('[data-workspace="data"]').click()
            page.locator('#dt-code-library summary').click()
            name = 'Long <unsafe>'
            injection = '</textarea><img src=x onerror="window.__snippetXss=true">'
            sample = "print('not executed')\\n" + injection
            sample += 'x' * (8000 - len(sample))
            assert len(sample) == 8000
            page.locator('#dt-snippet-name').fill(name)
            page.locator('#dt-snippet-kind').select_option('Python')
            page.locator('#dt-snippet-code').fill(sample)
            page.locator('#dt-snippet-save').click()
            page.locator('#dt-library-search').fill(name)
            view = page.get_by_role('button', name='View full snippet '+name)
            assert view.count() == 1
            before = page.evaluate("localStorage.getItem('promathstudio-data-snippets-v1')")
            python_before = page.locator('#python-output-result').text_content()
            for width in (1280, 768, 390):
                page.set_viewport_size({'width':width,'height':850})
                view.click()
                pane = page.locator('#dt-snippet-inspect')
                source = page.locator('#dt-snippet-inspect-code')
                assert pane.is_visible()
                assert source.input_value() == sample
                assert source.get_attribute('readonly') is not None
                assert source.evaluate('(e) => document.activeElement===e')
                assert source.bounding_box()['width'] <= width
                assert page.evaluate("localStorage.getItem('promathstudio-data-snippets-v1')") == before
                assert page.locator('#python-output-result').text_content() == python_before
                assert page.evaluate('window.__snippetXss === undefined')
                page.keyboard.press('Escape')
                assert pane.is_hidden()
                assert source.input_value() == ''
                assert view.evaluate('(e) => document.activeElement===e')
            view.click()
            page.get_by_role('button', name='Close snippet preview').click()
            assert page.locator('#dt-snippet-inspect').is_hidden()
            assert view.evaluate('(e) => document.activeElement===e')
            assert page.evaluate("localStorage.getItem('promathstudio-data-snippets-v1')") == before
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__ == '__main__':
    main()
