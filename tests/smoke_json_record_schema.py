"""JSON record imports must not silently discard columns introduced by later rows."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="data"]').click()

        # Key ordering may vary, but each record must contain the same keys.
        valid = [{'x': 1, 'label': 'Ångström'}, {'label': '日本語', 'x': 2}]
        assert page.evaluate('(s) => MathStudio.graphData.parseJSON(s)',
                             json.dumps(valid, ensure_ascii=False)) == {
            'headers': ['x', 'label'], 'rows': [[1, 'Ångström'], [2, '日本語']]}
        page.locator('#dt-import').set_input_files({
            'name': 'valid.json', 'mimeType': 'application/json',
            'buffer': json.dumps(valid, ensure_ascii=False).encode('utf-8')})
        page.wait_for_function('() => MathStudio.dataTables.tables.some(t => t.name === "valid")')
        assert page.evaluate('MathStudio.dataTables.active.rows') == [
            ['1', 'Ångström'], ['2', '日本語']]
        before = page.evaluate('MathStudio.dataTables.exportState()')

        invalid = [
            [{'x': 1, 'y': 2}, {'x': 3, 'y': 4, 'z': 5}],
            [{'x': 1, 'y': 2}, {'x': 3}],
            [{'x': 1, 'y': 2}, {'x': 3, 'z': 5}],
        ]
        for i, records in enumerate(invalid):
            payload = json.dumps(records)
            message = page.evaluate("""(s) => {
                try { MathStudio.graphData.parseJSON(s); return 'accepted'; }
                catch (error) { return error.message; }
            }""", payload)
            assert 'JSON record 2 has missing or unexpected columns' in message, message
            page.locator('#dt-import').set_input_files({
                'name': f'bad-{i}.json', 'mimeType': 'application/json',
                'buffer': payload.encode('utf-8')})
            page.wait_for_function('() => document.querySelector("#dt-status").textContent.includes("Import failed")')
            assert 'missing or unexpected columns' in page.locator('#dt-status').inner_text()
            assert page.evaluate('MathStudio.dataTables.exportState()') == before

        # The shared parser is used for graph import too; a rejected file must
        # not replace the previously selected graph dataset.
        page.locator('[data-workspace="graph"]').click()
        page.locator('#graph-data-file').set_input_files({
            'name': 'points.json', 'mimeType': 'application/json',
            'buffer': b'[{"x":1,"y":2},{"y":4,"x":3}]'})
        page.wait_for_function('() => MathStudio.graphData.hasData()')
        graph_before = page.evaluate('MathStudio.graphData.exportState()')
        page.locator('#graph-data-file').set_input_files({
            'name': 'bad-graph.json', 'mimeType': 'application/json',
            'buffer': json.dumps(invalid[0]).encode('utf-8')})
        page.wait_for_function('() => document.querySelector("#graph-data-status").textContent.includes("Import failed")')
        assert page.evaluate('MathStudio.graphData.exportState()') == graph_before
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#graph-data-file').count() == 1
        assert not errors, errors
        browser.close()
    print('PASS: strict JSON record schemas, reordered keys, Unicode, transactional table and graph imports')


if __name__ == '__main__':
    main()
