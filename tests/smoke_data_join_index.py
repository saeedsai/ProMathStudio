"""Data Tables indexed joins: duplicates, ordering, outer rows, bounds and rollback."""
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

        def load(left, right):
            page.evaluate("""(data) => MathStudio.dataTables.restoreState({
                version: 1, selected: 'sheet-1', tables: [
                    {id: 'sheet-1', name: 'Left', columns: ['key','label'], rows: data[0]},
                    {id: 'sheet-2', name: 'Right', columns: ['key','label'], rows: data[1]}
                ]
            })""", [left, right])
            # Combine controls live inside a collapsed native disclosure.
            page.locator('#data-menu-navigation > details').nth(2).evaluate('(e) => e.open = true')
            page.locator('#dt-left').select_option(label='Left')
            page.locator('#dt-right').select_option(label='Right')
            page.locator('#dt-left-key').select_option('0')
            page.locator('#dt-right-key').select_option('0')

        def run(mode):
            page.locator('#dt-op').select_option(mode)
            page.locator('#dt-run').click()
            return page.evaluate('MathStudio.dataTables.active.rows')

        load([['1','L1'],['1','L2'],['2','L3'],['','L4']],
             [['1','R1'],['1','R2'],['3','R3'],['','R4']])
        assert run('inner') == [
            ['1','L1','1','R1'], ['1','L1','1','R2'],
            ['1','L2','1','R1'], ['1','L2','1','R2'], ['','L4','','R4']]
        load([['1','L1'],['1','L2'],['2','L3'],['','L4']],
             [['1','R1'],['1','R2'],['3','R3'],['','R4']])
        assert run('left') == [
            ['1','L1','1','R1'], ['1','L1','1','R2'],
            ['1','L2','1','R1'], ['1','L2','1','R2'],
            ['2','L3','',''], ['','L4','','R4']]
        load([['1','L1'],['1','L2'],['2','L3'],['','L4']],
             [['1','R1'],['1','R2'],['3','R3'],['','R4']])
        assert run('right') == [
            ['1','L1','1','R1'], ['1','L1','1','R2'],
            ['1','L2','1','R1'], ['1','L2','1','R2'],
            ['','L4','','R4'], ['','','3','R3']]
        load([['1','L1'],['1','L2'],['2','L3'],['','L4']],
             [['1','R1'],['1','R2'],['3','R3'],['','R4']])
        assert run('full') == [
            ['1','L1','1','R1'], ['1','L1','1','R2'],
            ['1','L2','1','R1'], ['1','L2','1','R2'],
            ['2','L3','',''], ['','L4','','R4'], ['','','3','R3']]

        # Over-limit duplicate joins must fail without adding a sheet.
        load([['x',str(i)] for i in range(100)],
             [['x',str(i)] for i in range(100)])
        before = page.evaluate('MathStudio.dataTables.exportState()')
        page.locator('#dt-op').select_option('inner')
        page.locator('#dt-run').click()
        assert '6,000 rows' in page.locator('#dt-status').inner_text()
        assert page.evaluate('MathStudio.dataTables.exportState()') == before
        # A select cannot retain an unlisted value; insert a malformed option
        # to exercise the application's invalid-key guard explicitly.
        page.evaluate("""() => {
            const key = document.getElementById('dt-left-key');
            key.add(new Option('Invalid', '-1'));
            key.value = '-1';
        }""")
        page.locator('#dt-run').click()
        assert 'Invalid join key' in page.locator('#dt-status').inner_text()
        assert page.evaluate('MathStudio.dataTables.exportState()') == before

        # A larger unique-key join remains bounded and ordered.
        load([[str(i), 'L'+str(i)] for i in range(2500)],
             [[str(i), 'R'+str(i)] for i in range(2500)])
        rows = run('inner')
        assert len(rows) == 2500
        assert rows[0] == ['0','L0','0','R0']
        assert rows[-1] == ['2499','L2499','2499','R2499']
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#dt-sheet').count() == 1
        assert not errors, errors
        browser.close()
    print('PASS indexed joins, duplicates, outer ordering, limits, rollback and mobile')


if __name__ == '__main__':
    main()
