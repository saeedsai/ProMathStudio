"""CSV/TSV explicit empty records survive import/export without dropping data."""
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

        # A delimiter or quoted empty field is an intentional record; an empty
        # physical line is not. Both graph and sheet import use this parser.
        csv_text = 'id,note\n1,"hello\nworld"\n,\n"",""\n\n2,"x,y"\n'
        parsed = page.evaluate('(s) => MathStudio.graphData.parseCSV(s)', csv_text)
        expected = [['1', 'hello\nworld'], ['', ''], ['', ''], ['2', 'x,y']]
        assert parsed == {'headers': ['id', 'note'], 'rows': expected}, parsed
        assert page.evaluate('(s) => MathStudio.graphData.parseCSV(s).rows', 'x,y\n,\n') == [['', '']]
        assert page.evaluate('(s) => MathStudio.graphData.parseCSV(s).rows', 'x\ty\n\t\n') == [['', '']]
        assert page.evaluate('(s) => MathStudio.graphData.parseCSV(s).rows', 'x,y\n"",""') == [['', '']]
        assert page.evaluate('''() => {
            try { MathStudio.graphData.parseCSV('x,y\\n'+'1,2\\n'.repeat(6001)); return false; }
            catch (error) { return error.message.includes('6,000'); }
        }''')

        page.locator('#dt-import').set_input_files({
            'name': 'blanks.csv', 'mimeType': 'text/csv', 'buffer': csv_text.encode()})
        page.wait_for_function("() => !document.querySelector('#dt-import-preview').hidden")
        page.locator('#dt-import-confirm').evaluate('(e) => e.click()')
        page.wait_for_function('() => MathStudio.dataTables.tables.some(t => t.name === "blanks")')
        assert page.evaluate('MathStudio.dataTables.active.rows') == expected
        assert page.evaluate('MathStudio.dataTables.active.columns') == ['id', 'note']
        page.locator('#data-menu-navigation > details').nth(3).evaluate('(e) => e.open = true')
        with page.expect_download() as result:
            page.locator('#dt-export-csv').click()
        exported = Path(result.value.path()).read_bytes()
        assert list(csv.reader(io.StringIO(exported.decode('utf-8')))) == [
            ['id', 'note'], *expected]

        page.locator('#dt-import').set_input_files({
            'name': 'replay.csv', 'mimeType': 'text/csv', 'buffer': exported})
        page.wait_for_function("() => !document.querySelector('#dt-import-preview').hidden")
        page.locator('#dt-import-confirm').evaluate('(e) => e.click()')
        page.wait_for_function('() => MathStudio.dataTables.tables.some(t => t.name === "replay")')
        assert page.evaluate('MathStudio.dataTables.active.rows') == expected

        tsv = 'x\ty\n\t\n""\t""\n3\t4\n'
        page.locator('#dt-import').set_input_files({
            'name': 'tabbed.tsv', 'mimeType': 'text/tab-separated-values',
            'buffer': tsv.encode()})
        page.wait_for_function("() => !document.querySelector('#dt-import-preview').hidden")
        page.locator('#dt-import-confirm').evaluate('(e) => e.click()')
        page.wait_for_function('() => MathStudio.dataTables.tables.some(t => t.name === "tabbed")')
        assert page.evaluate('MathStudio.dataTables.active.rows') == [
            ['', ''], ['', ''], ['3', '4']]

        before = page.evaluate('MathStudio.dataTables.exportState()')
        page.locator('#dt-import').set_input_files({
            'name': 'broken.csv', 'mimeType': 'text/csv',
            'buffer': b'x,y\n1,"unclosed\n'})
        page.wait_for_function('() => document.querySelector("#dt-status").textContent.includes("Import failed")')
        assert page.evaluate('MathStudio.dataTables.exportState()') == before
        assert 'unclosed quote' in page.locator('#dt-status').inner_text()

        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#dt-import').count() == 1
        assert not errors, errors
        browser.close()
    print('PASS CSV/TSV explicit empty records, multiline quoting, export/reimport, malformed rollback and limits')


if __name__ == '__main__':
    main()
