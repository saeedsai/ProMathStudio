"""Versioned project import, validation and atomic rollback browser regression."""
import json
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def start_server():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def upload(page, data, filename='backup.json'):
    raw = data if isinstance(data, bytes) else json.dumps(data).encode('utf-8')
    page.locator('#hub-project-file').set_input_files({
        'name': filename, 'mimeType': 'application/json', 'buffer': raw})


def main():
    server, server_thread = start_server()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True,
                                         executable_path=os.getenv('CHROMIUM_PATH') or None,
                                         args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            dialogs = []

            def accept_dialog(dialog):
                dialogs.append(dialog.message)
                dialog.accept()

            page.on('dialog', accept_dialog)
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='load')
            original = page.evaluate('window.MathStudio.bridge.export()')
            assert original['version'] == 2
            legacy = dict(original, version=1, working='x+1', origin='editor',
                          notebook=[{'raw': 'x+1'}])
            upload(page, legacy)
            page.wait_for_function("window.MathStudio.bridge.export().working === 'x+1'")
            migrated = page.evaluate('window.MathStudio.bridge.export()')
            assert migrated['version'] == 2
            assert [item['raw'] for item in migrated['notebook']] == ['x+1']
            assert migrated['tables'] == original['tables'], 'legacy table data changed'
            valid_fit = dict(legacy, fit={'model': 'poly', 'degree': '4', 'lastEquation': 'y = 1 + 2*x'})
            upload(page, valid_fit)
            page.wait_for_function("""() => {
              const fit = window.MathStudio.bridge.export().fit;
              return fit?.model === 'poly' && fit.degree === '4' && fit.lastEquation === 'y = 1 + 2*x';
            }""")
            migrated = page.evaluate('window.MathStudio.bridge.export()')
            assert migrated['fit'] == valid_fit['fit']

            valid_solver = dict(legacy.get('solver') or {})
            valid_solver.update({
                'expression': 'θ_1^2', 'variable': 'θ_1', 'operation': 'limit',
                'engine': 'sympy', 'limitPoint': '0', 'limitDirection': '-',
                'odeInitialCondition': 'y(0)=1'
            })
            upload(page, dict(legacy, working='x+1', solver=valid_solver))
            page.wait_for_function("""() => {
              const solver = window.MathStudio.bridge.export().solver;
              return solver.operation === 'limit' && solver.engine === 'sympy' &&
                solver.limitDirection === '-' && solver.variable === 'θ_1' && solver.limitPoint === '0';
            }""")
            migrated = page.evaluate('window.MathStudio.bridge.export()')
            assert migrated['solver']['operation'] == 'limit'
            assert migrated['solver']['engine'] == 'sympy'
            assert migrated['solver']['limitDirection'] == '-'
            assert migrated['solver']['variable'] == 'θ_1'
            assert migrated['solver']['limitPoint'] == '0'
            assert migrated['solver']['odeInitialCondition'] == 'y(0)=1'

            valid_python_function = [{
                'name': 'g_2', 'params': ['t'], 'expression': '',
                'source': 'def g_2(t):\n  return t', 'type': 'python'
            }]
            upload(page, dict(legacy, working='x+1', customFunctions=valid_python_function))
            page.wait_for_function("window.MathStudio.bridge.export().customFunctions[0]?.name === 'g_2'")
            migrated = page.evaluate('window.MathStudio.bridge.export()')
            assert migrated['customFunctions'] == valid_python_function

            # Open the native disclosure before interacting with its hidden editor controls.
            page.locator('#custom-function-panel > summary').click()
            assert page.locator('#cf-name').is_visible(), 'custom-function editor did not open'
            # The editor rejects a Python def whose ordered arguments differ from saved params.
            page.locator('#cf-name').fill('bad_signature')
            page.locator('#cf-params').fill('x')
            page.locator('#cf-type').select_option('python')
            page.locator('#cf-body').fill('def bad_signature(y):\n  return y')
            page.locator('#cf-save').click()
            assert 'matching parameters' in page.locator('#cf-message').inner_text().lower()
            assert not any(item['name'] == 'bad_signature' for item in page.evaluate('window.MathStudio.customFunctions.list()'))
    
            # Matching multi-argument definitions remain supported.
            page.locator('#cf-name').fill('pair_sum')
            page.locator('#cf-params').fill('x,y')
            page.locator('#cf-type').select_option('python')
            page.locator('#cf-body').fill('def pair_sum(x, y):\n  return x + y')
            page.locator('#cf-save').click()
            assert 'Saved pair_sum.' in page.locator('#cf-message').inner_text()
            pair_sum = page.evaluate("window.MathStudio.customFunctions.list().find(item => item.name === 'pair_sum')")
            assert pair_sum['params'] == ['x', 'y']
    
            # The public restore API is also a state boundary: reject an entire invalid list
            # before mutating the active functions or their localStorage copy.
            invalid_restore_cases = [
                [{'name': 'sin', 'params': ['x'], 'expression': 'x', 'type': 'formula'}],
                [{'name': 'SUM', 'params': ['x'], 'expression': 'x', 'type': 'formula'}],
                [{'name': 'f', 'params': ['x', 'x'], 'expression': 'x'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'formula'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python',
                  'source': 'def other(x):\\n  return x'}],
            [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python',
              'source': 'def f(y):\\n  return y'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python',
                  'source': 'def f(x):\n  return x\ndef f(y):\n  return y'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python',
                  'source': 'async def f(x):\n  return x'}],
                [{'name': 'same', 'params': ['x'], 'expression': 'x'},
                 {'name': 'SAME', 'params': ['x'], 'expression': 'x'}],
                [{'name': 'f', 'params': ['x'], 'expression': 'x'}] * 61,
                None,
            ]
            for functions in invalid_restore_cases:
                result = page.evaluate("""items => {
                  const before = window.MathStudio.customFunctions.list();
                  const stored = localStorage.getItem('promath-custom-functions-v1');
                  let error = '';
                  try { window.MathStudio.customFunctions.restore(items); }
                  catch (e) { error = e.message; }
                  return {before, after: window.MathStudio.customFunctions.list(), stored,
                    storedAfter: localStorage.getItem('promath-custom-functions-v1'), error};
                }""", functions)
                assert result['error'], f'invalid direct restore was accepted: {functions!r}'
                assert result['after'] == result['before'], 'invalid direct restore mutated custom functions'
                assert result['storedAfter'] == result['stored'], 'invalid direct restore changed localStorage'

            def rejected(candidate):
                dialog_count = len(dialogs)
                # Valid imports later in this test intentionally replace workspace state.
                # Compare each refusal with the state immediately before that attempted import.
                before = page.evaluate('window.MathStudio.bridge.export()')
                page.locator('#hub-status').evaluate("el => el.textContent = ''")
                upload(page, candidate)
                page.wait_for_function("document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
                current = page.evaluate('window.MathStudio.bridge.export()')
                for key in ('working', 'origin', 'recent', 'notebook', 'calculator', 'matrix',
                            'engineering', 'solver', 'graph', 'customFunctions', 'tables', 'fit'):
                    assert current[key] == before[key], f'invalid import mutated {key}'
                assert len(dialogs) == dialog_count, 'invalid project must be rejected before confirmation'

            rejected(dict(legacy, version=99, working='WRONG'))
            rejected(dict(legacy, working='WRONG', notebook=[{'raw': 42}]))
            for invalid_fit in (
                    {'model': 'unknown', 'degree': '2', 'lastEquation': ''},
                    {'model': 'poly', 'degree': '7', 'lastEquation': ''},
                    {'model': 'poly', 'degree': '4', 'lastEquation': 'x' * 2001},
                    {'model': 3, 'degree': '2', 'lastEquation': ''},
                    {'model': 'poly', 'degree': 4, 'lastEquation': ''},
                    {'model': 'poly', 'degree': '4', 'lastEquation': []},
                    []):
                rejected(dict(legacy, working='WRONG', fit=invalid_fit))
            for invalid_solver in (
                    dict(valid_solver, operation='future-operation'),
                    dict(valid_solver, engine='remote'),
                    dict(valid_solver, limitDirection='left'),
                    dict(valid_solver, variable='x' * 25),
                    dict(valid_solver, variable='1x'),
                    dict(valid_solver, variable='x+y'),
                    dict(valid_solver, limitPoint='0' * 81)):
                rejected(dict(legacy, working='WRONG', solver=invalid_solver))
            invalid_custom_functions = [
                [{'name': 'sin', 'params': ['x'], 'expression': 'x', 'type': 'formula'}],
                [{'name': 'SUM', 'params': ['x'], 'expression': 'x', 'type': 'formula'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'formula'}],
                [{'name': 'f', 'params': ['x'], 'expression': '   ', 'type': 'formula'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python', 'source': ''}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python', 'source': 'def other(x):\n  return x'}],
            [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python', 'source': 'def f(y):\n  return y'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python',
                  'source': 'def f(x):\n  return x\ndef f(y):\n  return y'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python',
                  'source': 'async def f(x):\n  return x'}],
                [{'name': 'f', 'params': ['x'], 'expression': '', 'type': 'python',
                  'source': 'def f(x):\n  return x\nasync def f(y):\n  return y'}],
            ]
            for functions in invalid_custom_functions:
                rejected(dict(legacy, working='WRONG', customFunctions=functions))

            bad_tables = {'version': 1, 'selected': 'sheet-1', 'tables': [
                {'id': 'sheet-1', 'name': 'Data1', 'columns': ['A', 'B'], 'rows': [['1']]}]}
            rejected(dict(legacy, working='WRONG', tables=bad_tables))
            # Tables whose identifiers differ only by surrounding spaces cannot
            # be safely restored as distinct named tables.
            def named_table(table_id, name):
                return {'id': table_id, 'name': name, 'columns': ['A'], 'rows': [[1]]}
            rejected(dict(legacy, working='WRONG', tables={
                'version': 1, 'selected': 'sheet-1', 'tables': [
                    named_table('sheet-1', 'Data1'),
                    named_table('sheet-2', ' data1 ')]}))
            rejected(dict(legacy, working='WRONG', tables={
                'version': 1, 'selected': 'sheet-1', 'tables': [
                    named_table('sheet-1', '   ')]}))

            bad_graph = dict(legacy, working='WRONG', graph={
                'dataset': {'headers': ['time', 'value'], 'rows': [[0, {'unexpected': 1}]]}})
            rejected(bad_graph)
            bad_graph['graph']['dataset']['rows'][0][1] = [1, 2]
            rejected(bad_graph)
            # Duplicate graph headers are ambiguous for column selection.
            for names in (['time', 'time'], ['value', 'value'],
                          [' Time ', 'time'], ['value', ' VALUE '],
                          ['time', ' '], ['', 'value']):
                rejected(dict(legacy, working='WRONG', graph={
                    'dataset': {'headers': names, 'rows': [[0, 2], [1, 3]]}}))
            # Primary Graph selectors are persisted too. Invalid explicit selectors or
            # plot styles must be rejected before any other workspace is changed.
            def mapped_graph(mode='3d'):
                return {'mode': mode, 'dataset': {
                    'name': 'mapped.csv', 'headers': ['time', 'value', 'height'],
                    'rows': [[0, 1, 2], [1, 2, 3]],
                    'x': '0', 'y': '1', 'z': '2', 'style': 'line'}}
            invalid_primary = []
            bad = mapped_graph(); bad['mode'] = '4d'; invalid_primary.append(bad)
            bad = mapped_graph(); bad['dataset']['x'] = '3'; invalid_primary.append(bad)
            bad = mapped_graph(); bad['dataset']['y'] = 'time'; invalid_primary.append(bad)
            bad = mapped_graph(); bad['dataset']['z'] = -1; invalid_primary.append(bad)
            bad = mapped_graph(); bad['dataset']['x'] = '1'; invalid_primary.append(bad)
            bad = mapped_graph(); bad['dataset']['z'] = '1'; invalid_primary.append(bad)
            bad = mapped_graph(); bad['dataset']['style'] = 'dots'; invalid_primary.append(bad)
            bad = {'mode': '3d', 'dataset': {
                'headers': ['time', 'value'], 'rows': [[0, 1], [1, 2]]}}
            invalid_primary.append(bad)
            for graph_state in invalid_primary:
                rejected(dict(legacy, working='WRONG', graph=graph_state))

            good_graph = dict(legacy, working='x+1', graph={
                'dataset': {'headers': ['time', 'value'], 'rows': [[0, 2], [1, None]]}})
            upload(page, good_graph)
            # The bridge can temporarily expose graph.dataset=null while import applies.
            # Poll through that valid transient state, then assert the complete dataset.
            page.wait_for_function("() => window.MathStudio.bridge.export().graph.dataset?.rows?.length === 2")
            assert page.evaluate("window.MathStudio.bridge.export().graph.dataset.rows[1][1]") is None
            assert page.evaluate("window.MathStudio.bridge.export().graph.dataset.headers") == ['time', 'value']
            mapped = dict(legacy, working='x+1', graph=mapped_graph())
            upload(page, mapped)
            page.wait_for_function("() => { const g=window.MathStudio.bridge.export().graph; return g.mode === '3d' && g.dataset?.rows?.length === 2; }")
            restored_graph = page.evaluate("window.MathStudio.bridge.export().graph")
            assert restored_graph['dataset']['x'] == '0'
            assert restored_graph['dataset']['y'] == '1'
            assert restored_graph['dataset']['z'] == '2'
            assert restored_graph['dataset']['style'] == 'line'

            # Nonfinite table numeric values are rejected during schema validation.
            # JSON itself cannot encode Infinity, but JSON.parse may receive 1e999,
            # which becomes Infinity before the project schema sees it.
            nonfinite = dict(legacy, working='WRONG')
            nonfinite['tables'] = {'version': 1, 'selected': 'sheet-1', 'tables': [
                {'id': 'sheet-1', 'name': 'Data1', 'columns': ['A'], 'rows': [[float('inf')]]}]}
            raw_nonfinite = json.dumps(nonfinite).replace('Infinity', '1e999').encode('utf-8')
            rejected(raw_nonfinite)

            upload(page, b' ' * 2_000_001)
            page.wait_for_function("document.querySelector('#hub-status').textContent.includes('exceeds 2 MB')")
            assert page.evaluate('window.MathStudio.bridge.export().working') == 'x+1'

            # Simulate a restore-stage failure after notebook mutation. The previous
            # project must be reapplied rather than left half imported.
            # Capture the state that is actually active after the later valid Graph imports.
            # The earlier migrated snapshot belongs to the SymPy solver import and is stale here.
            solver_before_rollback = page.evaluate('window.MathStudio.bridge.export().solver')
            page.evaluate("""() => {
              const fit=window.MathStudio.curveFit;
              window.__originalFitRestore=fit.restoreState;
              let once=true;
              fit.restoreState=(value)=>{
                if(once){once=false;throw Error('injected restore failure');}
                return window.__originalFitRestore(value);
              };
            }""")
            upload(page, dict(legacy, working='SHOULD_ROLL_BACK', notebook=[{'raw': 'y^2'}]))
            page.wait_for_function("document.querySelector('#hub-status').textContent.includes('injected restore failure')")
            page.evaluate("window.MathStudio.curveFit.restoreState=window.__originalFitRestore")
            assert page.evaluate('window.MathStudio.bridge.export().working') == 'x+1'
            assert [i['raw'] for i in page.evaluate('window.MathStudio.bridge.export().notebook')] == ['x+1']
            assert page.evaluate('window.MathStudio.bridge.export().solver') == solver_before_rollback, 'restore failure rollback changed solver controls'
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)
    print('PASS: v1→v2 migration, workbook retention, invalid/future/oversize refusal and transactional rollback')


if __name__ == '__main__':
    main()
