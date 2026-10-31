"""Graph dataset export->import identity (mixed cells, column mapping, overlay) and 390px layout."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def upload(page, data):
    page.locator('#hub-project-file').set_input_files({
        'name': 'backup.json', 'mimeType': 'application/json',
        'buffer': json.dumps(data).encode('utf-8')})


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.evaluate("""() => {
          const g = MathStudio.graphData;
          g.loadTable({headers: ['t', 'v', 'label'],
                       rows: [['0', '1.5', 'a'], ['1', '', 'b'], ['2', '3e2', 'c']]}, 'MIX', {x: 0, y: 1, z: 2});
          g.addTable({headers: ['t', 'w'], rows: [['0', '2'], ['1', '4']]}, 'OVERLAY',
                     {x: 0, y: 1, z: 1, mode: '2d', style: 'line'});
        }""")
        first = page.evaluate('window.MathStudio.bridge.export()')
        dataset = first['graph']['dataset']
        assert dataset['headers'] == ['t', 'v', 'label'] and len(dataset['extra']) == 1

        # Re-import our own export: dataset (cells as stored, column order, mapping, overlay) must be identical.
        upload(page, dict(first, working='RT1'))
        page.wait_for_function("window.MathStudio.bridge.export().working === 'RT1'")
        second = page.evaluate('window.MathStudio.bridge.export()')
        assert second['graph']['dataset'] == dataset, (second['graph']['dataset'], dataset)

        # A project with mixed primitive JSON cells restores without losing rows or column order.
        mixed = json.loads(json.dumps(first))
        mixed['graph']['dataset'].update({
            'headers': ['t', 'v', 'flag'], 'x': '0', 'y': '1', 'z': '2', 'extra': [],
            'rows': [[0, 1.5, True], [1, None, False], [2, '3e2', None]]})
        mixed['working'] = 'RT2'
        upload(page, mixed)
        page.wait_for_function("window.MathStudio.bridge.export().working === 'RT2'")
        restored = page.evaluate('window.MathStudio.bridge.export().graph.dataset')
        assert restored['headers'] == ['t', 'v', 'flag'] and len(restored['rows']) == 3, restored

        # Malformed (duplicate header) is refused atomically: the prior dataset and marker stay.
        bad = json.loads(json.dumps(first))
        bad['graph']['dataset']['headers'] = ['t', 'T', 'label']
        bad['working'] = 'SHOULD_NOT_APPLY'
        upload(page, bad)
        page.wait_for_function(
            "document.querySelector('#hub-status').textContent.includes('duplicate column names')")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'RT2'
        assert page.evaluate('window.MathStudio.bridge.export().graph.dataset.headers') == ['t', 'v', 'flag']

        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors, errors
        browser.close()
    print('PASS graph dataset round-trip identity, mixed cells, atomic rejection, mobile')


if __name__ == '__main__':
    main()
