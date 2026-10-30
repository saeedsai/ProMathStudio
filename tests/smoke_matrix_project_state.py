"""Matrix draft project round-trip, focus preservation and mobile import rollback."""
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def upload(page, data):
    page.locator('#hub-project-file').set_input_files({
        'name': 'matrix-project.json', 'mimeType': 'application/json',
        'buffer': json.dumps(data).encode('utf-8'),
    })


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('dialog', lambda dialog: dialog.accept())
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'),
                         wait_until='load')
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#workspace-task-select').select_option('matrix')
        page.locator('#matrix-tools').evaluate('(el) => el.open = true')

        page.locator('#mat-rows').select_option('3')
        page.locator('#mat-cols').select_option('2')
        page.locator('#mat-b-cols').select_option('3')
        page.locator('#mat-grid [data-row="2"][data-col="1"]').fill('2.5')
        page.locator('#mat-grid [data-row="0"][data-col="0"]').fill('')
        page.locator('#mat-b-grid [data-row="1"][data-col="2"]').fill('7')
        page.locator('#mat-rhs-grid [data-row="2"][data-col="0"]').fill('-4')
        page.locator('#mat-weight-grid [data-row="2"][data-col="0"]').fill('0.25')
        saved = page.evaluate('MathStudio.bridge.export()')
        assert saved['matrix']['rows'] == 3
        assert saved['matrix']['cols'] == 2
        assert saved['matrix']['bCols'] == 3
        assert saved['matrix']['a'][0] == ''
        assert saved['matrix']['a'][-1] == '2.5'

        # Restoring while editing the grid keeps the same cell focused.
        cell = page.locator('#mat-grid [data-row="2"][data-col="1"]')
        cell.focus()
        page.evaluate('MathStudio.matrixTools.restoreState(MathStudio.matrixTools.exportState())')
        assert page.locator('#mat-grid [data-row="2"][data-col="1"]').evaluate(
            '(el) => document.activeElement === el')

        # Restoring from elsewhere must never steal keyboard focus.
        page.locator('#workspace-task-select').focus()
        page.evaluate('MathStudio.matrixTools.restoreState(MathStudio.matrixTools.exportState())')
        assert page.evaluate('document.activeElement.id') == 'workspace-task-select'

        page.locator('#mat-rows').select_option('2')
        page.locator('#mat-cols').select_option('3')
        page.locator('#mat-grid [data-row="0"][data-col="0"]').fill('99')
        page.set_viewport_size({'width': 390, 'height': 844})
        upload(page, saved)
        page.wait_for_function(
            "() => MathStudio.matrixTools.exportState().rows === 3 && "
            "MathStudio.matrixTools.exportState().cols === 2")
        restored = page.evaluate('MathStudio.matrixTools.exportState()')
        assert restored == saved['matrix'], (restored, saved['matrix'])
        assert page.locator('#mat-grid [data-row="2"][data-col="1"]').input_value() == '2.5'

        # Recovered drafts compute the expected transpose; a subsequent project
        # restore must invalidate the stale transferable result.
        page.locator('#mat-grid [data-row="0"][data-col="0"]').fill('1')
        assert page.evaluate("MathStudio.matrixTools.calculate('transpose').value") == [
            [1, 0, 0], [0, 1, 2.5]]
        assert not page.locator('#mat-send').is_disabled()
        upload(page, saved)
        page.wait_for_function("() => document.querySelector('#mat-send').disabled")
        assert page.evaluate('MathStudio.matrixTools.exportState()') == restored

        # Invalid schema must be rejected before mutating any Matrix drafts.
        invalid = json.loads(json.dumps(saved))
        invalid['matrix']['rows'] = 4
        upload(page, invalid)
        page.wait_for_function(
            "() => document.querySelector('#hub-status').textContent.startsWith('Import failed:')")
        assert page.evaluate('MathStudio.matrixTools.exportState()') == restored
        assert not errors, errors
        browser.close()
    print('PASS: Matrix project round-trip, invalid drafts, focus and mobile')


if __name__ == '__main__':
    main()
