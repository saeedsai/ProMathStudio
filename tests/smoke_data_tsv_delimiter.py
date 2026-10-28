"""TSV export must quote commas/semicolons to survive delimiter sniffing on reimport."""
import csv
import io
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(accept_downloads=True, viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="data"]').click()

        # More commas than tabs in a valid TSV header used to confuse the
        # shared CSV/TSV delimiter sniffer during reimport.
        headers = ['id', 'Cost, SEK, tax', 'Region, EU; west']
        rows = [['1', 'a\tb', 'Hej, "värld"'],
                ['2', 'two\nlines', 'Semi;colon'],
                ['3', '', '']]
        original = io.StringIO(newline='')
        writer = csv.writer(original, lineterminator='\r\n')
        writer.writerow(headers)
        writer.writerows(rows)
        page.locator('#dt-import').set_input_files({
            'name': 'ambiguous.csv', 'mimeType': 'text/csv',
            'buffer': original.getvalue().encode('utf-8')})
        page.wait_for_function(
            '() => MathStudio.dataTables.tables.some(t => t.name === "ambiguous")')
        assert page.evaluate('MathStudio.dataTables.active.columns') == headers
        assert page.evaluate('MathStudio.dataTables.active.rows') == rows

        page.locator('#data-menu-navigation > details').nth(3).evaluate('(e) => e.open = true')
        with page.expect_download() as download:
            page.locator('#dt-export-tsv').click()
        result = download.value
        assert result.suggested_filename.endswith('.tsv')
        raw = Path(result.path()).read_bytes()
        decoded = raw.decode('utf-8')
        assert '"Cost, SEK, tax"' in decoded.splitlines()[0]
        assert '"Region, EU; west"' in decoded.splitlines()[0]
        assert list(csv.reader(io.StringIO(decoded, newline=''), delimiter='\t')) == [
            headers, *rows]

        page.locator('#dt-import').set_input_files({
            'name': 'reimport.tsv', 'mimeType': 'text/tab-separated-values',
            'buffer': raw})
        page.wait_for_function(
            '() => MathStudio.dataTables.tables.some(t => t.name === "reimport")')
        assert page.evaluate('MathStudio.dataTables.active.columns') == headers
        assert page.evaluate('MathStudio.dataTables.active.rows') == rows

        before = page.evaluate('MathStudio.dataTables.exportState()')
        page.locator('#dt-import').set_input_files({
            'name': 'broken.tsv', 'mimeType': 'text/tab-separated-values',
            'buffer': b'x\ty\n1\t"unterminated\n'})
        page.wait_for_function(
            '() => document.querySelector("#dt-status").textContent.includes("Import failed")')
        assert page.evaluate('MathStudio.dataTables.exportState()') == before
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#dt-export-tsv').count() == 1
        assert not errors, errors
        browser.close()
    print('PASS TSV delimiter ambiguity, Unicode, quotes, tabs, multiline, rollback and mobile')


if __name__ == '__main__':
    main()
