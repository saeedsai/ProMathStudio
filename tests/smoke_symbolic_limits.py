"""Symbolic limits: exact SymPy reference, nonexistence/domain errors, and UI integration."""
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = (ROOT / 'index.html').read_text(encoding='utf-8')
    match = re.search(r'<script id="mathstudio-sympy-python" type="text/plain">(.*?)</script>', source, re.S)
    assert match, 'Safe embedded SymPy worker code missing'
    scope = {}
    exec(compile(match.group(1), '<embedded-sympy>', 'exec'), scope)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(source, wait_until='load')
        def ast(expr):
            return page.evaluate('(text) => MathStudio.parse(text).ast', expr)
        def run(expr, point, direction='+-'):
            return json.loads(scope['_ms_process'](json.dumps({
                'ast': ast(expr), 'operation': 'limit', 'variable': 'x',
                'pointAst': ast(point), 'direction': direction
            })))
        def invalid(expr, point, direction='+-', variable='x'):
            try:
                scope['_ms_process'](json.dumps({
                    'ast': ast(expr), 'operation': 'limit', 'variable': variable,
                    'pointAst': ast(point), 'direction': direction
                }))
                assert False, (expr, point, direction, 'unexpectedly accepted')
            except scope['MathStudioSympyError'] as exc:
                return str(exc)
        assert run('sin(x)/x', '0')['items'][0]['plain'] == '1'
        assert run('1/x', '0', '+')['items'][0]['plain'] == 'oo'
        assert run('1/x', '0', '-')['items'][0]['plain'] == '-oo'
        assert run('1/x^2', '0')['items'][0]['plain'] == 'oo'
        assert run('1/x', 'oo')['items'][0]['plain'] == '0'
        assert run('x', '-oo')['items'][0]['plain'] == '-oo'
        assert run('sin(x)', 'pi/2')['items'][0]['plain'] == '1'
        assert 'does not exist' in invalid('1/x', '0').lower()
        assert 'does not exist' in invalid('sin(1/x)', '0').lower()
        assert 'real constant' in invalid('x', 'sqrt(-1)').lower()
        assert 'real constant' in invalid('x', 'y').lower()
        assert 'free parameters' in invalid('x+y', '0').lower()
        assert 'scalar expression' in invalid('x=1', '0').lower()
        assert 'direction' in invalid('x', '0', 'sideways').lower()
        assert 'valid symbolic variable' in invalid('x', '0', variable='pi').lower()
        page.locator('[data-workspace="solver"]').click()
        page.locator('#cas-operation').select_option('limit')
        assert page.locator('#cas-limit-point').is_visible()
        assert page.locator('#cas-limit-direction').is_visible()
        page.locator('#cas-limit-point').fill('0')
        page.locator('#cas-limit-direction').select_option('+-')
        page.locator('#equation-input').fill('sin(x)/x')
        page.evaluate("""() => {
          window.Worker = class {
            postMessage(message) {
              window.__limitPayload = message.payload;
              queueMicrotask(() => this.onmessage({data:{
                id: message.id, type:'result',
                data:{operation:'limit', version:'1.14.0', note:'Two-sided limit',
                  items:[{plain:'1',latex:'1',mathml:'<math><mn>1</mn></math>',approx:''}]}
              }}));
            }
            terminate() {}
          };
        }""")
        page.locator('#cas-run').click()
        page.wait_for_function('() => !!window.__limitPayload')
        payload = page.evaluate('window.__limitPayload')
        assert payload['operation'] == 'limit', payload
        assert payload['direction'] == '+-', payload
        assert payload['pointAst']['kind'] == 'number', payload
        page.wait_for_function("() => document.getElementById('cas-python').textContent.includes('sp.limit(')")
        exported = page.locator('#cas-python').inner_text()
        assert 'sp.limit(expr, x, 0, dir="+-")' in exported, exported
        assert 'Two-sided limit' in page.locator('#cas-status').inner_text()
        page.locator('#cas-engine').select_option('offline')
        page.locator('#cas-run').click()
        assert 'requires SymPy' in page.locator('#cas-status').inner_text()
        page.locator('#cas-limit-point').fill('')
        page.locator('#cas-engine').select_option('auto')
        page.locator('#cas-run').click()
        assert 'approach point' in page.locator('#cas-status').inner_text()
        assert not errors, errors
        browser.close()
    print('PASS: exact symbolic limits, domain errors, UI worker payload and offline rejection')


if __name__ == '__main__':
    main()
