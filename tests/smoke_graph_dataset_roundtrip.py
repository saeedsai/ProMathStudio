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
          const before=JSON.stringify(g.exportState());
          for(const headers of [['t','T'],['t',' ']]){
            let error='';
            try{g.addTable({headers,rows:[['0','2']]},'INVALID',{x:0,y:1,mode:'2d'});}
            catch(e){error=e.message;}
            if(error!=='Invalid column names.')throw Error('ambiguous overlay headers were accepted: '+headers);
            if(JSON.stringify(g.exportState())!==before)throw Error('rejected overlay changed the existing graph dataset');
          }
          g.addTable({headers: ['t', 'w'], rows: [['0', '2'], ['1', '4']]}, 'OVERLAY',
                     {x: 0, y: 1, z: 1, mode: '2d', style: 'line'});
        }""")
        first = page.evaluate('window.MathStudio.bridge.export()')
        dataset = first['graph']['dataset']
        assert dataset['headers'] == ['t', 'v', 'label'] and len(dataset['extra']) == 1

        # Primary Graph projects must satisfy the same dimensions and numeric-point
        # requirements as the live importer, before any workspace is applied.
        prior_working = first['working']
        invalid_primary = [
            (['time', 'value'], [], '2d', '0', '1', '0'),
            (['time'], [[0]], '2d', '0', '0', '0'),
            (['t' * 101, 'value'], [[0, 1]], '2d', '0', '1', '0'),
            (['time', 'value'], [['not-x', 'not-y']], '2d', '0', '1', '0'),
            (['x', 'y', 'z'], [[0, 1, 'not-z']], '3d', '0', '1', '2'),
        ]
        for headers, rows, mode, x, y, z in invalid_primary:
            bad = json.loads(json.dumps(first))
            bad['working'] = 'SHOULD_NOT_APPLY'
            bad['graph']['mode'] = mode
            bad['graph']['dataset'] = {
                'name': 'invalid.csv', 'headers': headers, 'rows': rows,
                'x': x, 'y': y, 'z': z, 'style': 'points', 'extra': []}
            upload(page, bad)
            page.wait_for_function("document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
            current = page.evaluate('window.MathStudio.bridge.export()')
            assert current['working'] == prior_working
            assert current['graph']['dataset'] == dataset

        # Saved non-default selectors must be installed before the first series build.
        mapped = json.loads(json.dumps(first))
        mapped['working'] = 'RT-MAPPED'
        mapped['graph']['mode'] = '2d'
        mapped['graph']['dataset'] = {
            'name': 'mapped.csv', 'headers': ['label', 'first', 'second'],
            'rows': [['A', 0, 1], ['B', 1, 2]],
            'x': '1', 'y': '2', 'z': '0', 'style': 'line', 'extra': []}
        upload(page, mapped)
        page.wait_for_function("window.MathStudio.bridge.export().working === 'RT-MAPPED'")
        mapped_state = page.evaluate('window.MathStudio.graphData.getState()')
        assert mapped_state['x'] == '1' and mapped_state['y'] == '2', mapped_state
        assert len(mapped_state['points']) == 2, mapped_state
        assert mapped_state['points'][0]['x'] == 0 and mapped_state['points'][0]['y'] == 1, mapped_state

        # Re-import our own export: dataset (cells as stored, column order, mapping, overlay) must be identical.
        upload(page, dict(first, working='RT1'))
        page.wait_for_function("window.MathStudio.bridge.export().working === 'RT1'")
        second = page.evaluate('window.MathStudio.bridge.export()')
        assert second['graph']['dataset'] == dataset, (second['graph']['dataset'], dataset)

        # Invalid saved overlays must fail before project application, not be silently dropped.
        bad_overlay = json.loads(json.dumps(first))
        bad_overlay['working'] = 'SHOULD_NOT_APPLY'
        bad_overlay['graph']['dataset']['extra'][0]['mapping']['x'] = 99
        upload(page, bad_overlay)
        page.wait_for_function("document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'RT1'
        assert page.evaluate('window.MathStudio.bridge.export().graph.dataset') == dataset

        # Axis selectors are bounded base-10 integer indices, not Number()-coercible literals.
        bad_primary_index = json.loads(json.dumps(first))
        bad_primary_index['working'] = 'SHOULD_NOT_APPLY'
        bad_primary_index['graph']['dataset']['x'] = '0x0'
        upload(page, bad_primary_index)
        page.wait_for_function("document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'RT1'
        assert page.evaluate('window.MathStudio.bridge.export().graph.dataset') == dataset

        bad_overlay_index = json.loads(json.dumps(first))
        bad_overlay_index['working'] = 'SHOULD_NOT_APPLY'
        bad_overlay_index['graph']['dataset']['extra'][0]['mapping']['x'] = '0x0'
        upload(page, bad_overlay_index)
        page.wait_for_function("document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'RT1'
        assert page.evaluate('window.MathStudio.bridge.export().graph.dataset') == dataset

        # Saved overlays must use the same unambiguous header identity rule as primary datasets.
        for names in (['t', 'T'], ['t', ' ']):
            bad_headers = json.loads(json.dumps(first))
            bad_headers['working'] = 'SHOULD_NOT_APPLY'
            bad_headers['graph']['dataset']['extra'][0]['table']['headers'] = names
            upload(page, bad_headers)
            page.wait_for_function("document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
            assert page.evaluate('window.MathStudio.bridge.export().working') == 'RT1'
            assert page.evaluate('window.MathStudio.bridge.export().graph.dataset') == dataset

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
    print('PASS graph dataset round-trip identity, overlay validation/atomic rejection, mixed cells and mobile')


if __name__ == '__main__':
    main()
