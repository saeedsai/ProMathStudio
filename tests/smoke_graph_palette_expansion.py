"""Graph palette numeric templates: reference oracles, plot integration and mobile."""
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
    server = ThreadingHTTPServer(
        ('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
                args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1280, 'height': 850})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto('http://127.0.0.1:%s/index.html' % server.server_port,
                      wait_until='load')
            # Numeric reference values use the same safe AST evaluator as plotting.
            result = page.evaluate("""() => {
                const calc = text => window.MathStudio.advanced.numeric(text);
                let zeroDivision = false;
                try { calc('frac(1,0)'); } catch (_) { zeroDivision = true; }
                return {
                    cube: calc('root(3,8)'), fraction: calc('frac(7,2)'),
                    factorial: calc('5!'), zeroDivision
                };
            }""")
            for name, expected in [('cube', 2), ('fraction', 3.5), ('factorial', 120)]:
                assert abs(result[name]['re'] - expected) < 1e-9, (name, result)
                assert abs(result[name]['im']) < 1e-9, (name, result)
            assert result['zeroDivision'], result

            page.locator('[data-workspace="graph"]').click()
            symbols = page.locator('#quick-symbols')
            search = page.locator('#palette-search')
            graph = page.locator('#graph-input')
            for mode, prefix in [('2d', 'y = '), ('3d', 'z = ')]:
                page.locator('[data-graph-mode="%s"]' % mode).click()
                for width in (390, 768, 1280):
                    page.set_viewport_size({'width': width, 'height': 850})
                    for term, label, code in [
                        ('Nth root', 'Nth root', 'root(3,x)'),
                        ('Fraction', 'Fraction', 'frac(a,b)'),
                        ('Factorial', 'Factorial', '5!'),
                    ]:
                        graph.fill(prefix)
                        symbols.click()
                        search.fill(term)
                        button = page.locator('#palette-nav button[title="Insert %s: %s"]' %
                                              (label, code)).first
                        assert button.count() == 1 and button.is_enabled(), (mode, width, code)
                        button.click()
                        assert graph.input_value() == prefix + code, (mode, width, code)
                        assert graph.evaluate('(el) => document.activeElement === el')
                        if code != '5!':
                            # Placeholder fraction arguments must be filled before plotting.
                            if code == 'frac(a,b)':
                                graph.fill(prefix + 'frac(x,2)')
                            page.locator('#graph-plot').click()
                            assert not page.locator('#graph-status').evaluate(
                                '(el) => el.classList.contains("error")'), (
                                    mode, width, code, page.locator('#graph-status').inner_text())
                    graph.fill(prefix)
                    symbols.click()
                    search.fill('For all')
                    notation = page.locator('#palette-nav button').filter(has_text='For all').first
                    assert notation.count() == 1 and notation.is_disabled()
                    assert graph.input_value() == prefix
            page.locator('[data-workspace="editor"]').click()
            symbols.click()
            search.fill('For all')
            notation = page.locator('#palette-nav button[title="Insert For all: forall"]')
            assert notation.count() == 1 and notation.is_enabled()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print('PASS graph numeric palette root/fraction/factorial, oracles, 2D/3D, mobile')


if __name__ == '__main__':
    main()
