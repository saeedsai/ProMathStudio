"""Graph Symbols palette distinguishes numeric plot templates from Equation notation."""
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
                executable_path=os.getenv('CHROMIUM_PATH') or None,
                args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1280, 'height': 850})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto('http://127.0.0.1:%s/index.html' % server.server_port, wait_until='load')
            symbols = page.locator('#quick-symbols')
            search = page.locator('#palette-search')
            graph = page.locator('#graph-input')
            equation = page.locator('#equation-input')
            equation.fill('x + ')
            page.locator('[data-workspace="graph"]').click()
            for mode, prefix in [('2d', 'y = '), ('3d', 'z = ')]:
                page.locator('[data-graph-mode="%s"]' % mode).click()
                for width in (390, 768, 1280):
                    page.set_viewport_size({'width': width, 'height': 850})
                    graph.fill(prefix)
                    symbols.click()
                    assert page.locator('#palette-graph-hint').is_visible()
                    search.fill('For all')
                    notation = page.locator('#palette-nav button').filter(has_text='For all').first
                    assert notation.count() == 1 and notation.is_disabled()
                    assert graph.input_value() == prefix
                    search.fill('Sine')
                    numeric = page.locator('#palette-nav button[title="Insert Sine: sin(x)"]')
                    assert numeric.count() == 1 and numeric.is_enabled()
                    numeric.click()
                    assert graph.input_value() == prefix + 'sin(x)'
                    assert graph.evaluate('(el) => document.activeElement === el')
                    assert equation.input_value() == 'x + '
            page.locator('[data-workspace="editor"]').click()
            symbols.click()
            assert page.locator('#palette-graph-hint').is_hidden()
            search.fill('For all')
            notation = page.locator('#palette-nav button[title="Insert For all: forall"]')
            assert notation.count() == 1 and notation.is_enabled()
            notation.click()
            assert equation.input_value() == 'x + forall'
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print('PASS graph numeric palette gating, Equation notation, focus, 2D/3D and responsive')


if __name__ == '__main__':
    main()
