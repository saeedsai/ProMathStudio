"""Single-column CSV/TSV/JSON are valid Data Tables, never graph coordinate data."""
import csv
import io
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def upload(page, filename, payload):
    page.locator('#dt-import').set_input_files({
        'name': filename,
        'mimeType': 'application/json' if filename.endswith('.json') else 'text/plain',
        'buffer': payload.encode('utf-8') if isinstance(payload, str) else payload,
    })
    stem = filename.rsplit('.', 1)[0]
    page.wait_for_function(
        '(name) => MathStudio.dataTables.tables.some(t => t.name === name)', arg=stem)
    return page.evaluate('MathStudio.dataTables.active')


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(accept_downloads=True,
                                viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'),
                         wait_until='load')
        page.locator('[data-workspace="data"]').click()

        original_rows = [['Ångström, "café"'], ['two\nlines'],
                         ['=SUM(1,2)'], ['']]
        out = io.StringIO(newline='')
        csv.writer(out, lineterminator='\r\n').writerows([['Value'], *original_rows])
        first = upload(page, 'one_column.csv', out.getvalue())
        assert first['columns'] == ['Value'], first
        assert first['rows'] == original_rows, first

        # Source CSV must preserve formulas, Unicode, multiline text and blanks.
        page.locator('#data-menu-navigation > details').nth(3).evaluate(
            '(e) => e.open = true')
        with page.expect_download() as download:
            page.locator('#dt-export-source-csv').click()
        raw = Path(download.value.path()).read_bytes()
        assert list(csv.reader(io.StringIO(raw.decode('utf-8')))) == [
            ['Value'], *original_rows]
        second = upload(page, 'one_column_again.csv', raw)
        assert second['columns'] == ['Value']
        assert second['rows'] == original_rows

        # Single-column TSV has no delimiter in its header. Commas inside
        # unquoted formulas are valid TSV content, not CSV separators.
        tsv = 'Metric\r\n"Å, B; C\tD"\r\n"two\nlines"\r\n=SUM(1,2)\r\n""\r\n'
        third = upload(page, 'one_column_tsv.tsv', tsv)
        assert third['columns'] == ['Metric'], third
        assert third['rows'] == [['Å, B; C\tD'], ['two\nlines'],
                                 ['=SUM(1,2)'], ['']], third
        page.locator('#data-menu-navigation > details').nth(3).evaluate(
            '(e) => e.open = true')
        with page.expect_download() as download:
            page.locator('#dt-export-tsv').click()
        tsv_raw = Path(download.value.path()).read_bytes()
        # The regular TSV export intentionally exports calculated values,
        # unlike the separate formula-source CSV export.
        evaluated_tsv_rows = [['Å, B; C\tD'], ['two\nlines'], ['3'], ['']]
        assert list(csv.reader(io.StringIO(tsv_raw.decode('utf-8')),
                               delimiter='\t')) == [['Metric'], *evaluated_tsv_rows]
        assert upload(page, 'one_column_tsv_again.tsv', tsv_raw)['rows'] == evaluated_tsv_rows
        # A TSV file with a comma in its unquoted *single* header is still
        # one column: extension-specific tab delimiter wins over sniffing.
        comma_header = upload(page, 'comma_header.tsv',
                              'Metric, USD\r\n=SUM(1,2)\r\n')
        assert comma_header['columns'] == ['Metric, USD'], comma_header
        assert comma_header['rows'] == [['=SUM(1,2)']], comma_header

        records = [{'Reading': '日本語'}, {'Reading': 'Ångström'}]
        fourth = upload(page, 'one_column_json.json',
                        json.dumps(records, ensure_ascii=False))
        assert fourth['columns'] == ['Reading'], fourth
        assert fourth['rows'] == [['日本語'], ['Ångström']], fourth
        page.locator('#data-menu-navigation > details').nth(3).evaluate(
            '(e) => e.open = true')
        with page.expect_download() as download:
            page.locator('#dt-export-json').click()
        exported = Path(download.value.path()).read_bytes()
        assert json.loads(exported) == records
        assert upload(page, 'one_column_json_again.json', exported)['rows'] == fourth['rows']

        # Also accept single-column JSON coordinate and column-array formats.
        for variant_index, (payload, expected) in enumerate([
            ('[[1],[2]]', [['1'], ['2']]),
            ('{"score":[3,4]}', [['3'], ['4']]),
            ('{"columns":["score"],"rows":[[5],[6]]}', [['5'], ['6']]),
        ]):
            result = page.evaluate(
                '(s) => MathStudio.graphData.parseJSON(s,{allowSingleColumn:true})',
                payload)
            assert len(result['headers']) == 1 and len(result['rows']) == 2
            assert upload(page, f'one_column_variant_{variant_index}.json', payload)['rows'] == expected

        before = page.evaluate('MathStudio.dataTables.exportState()')
        for name, payload in [
            ('invalid.csv', 'Value\r\n1,2\r\n'),
            ('invalid.tsv', 'Value\r\n"unclosed\r\n'),
            ('invalid.json', '[{"a":1},{"b":2}]'),
        ]:
            page.locator('#dt-import').set_input_files({
                'name': name, 'mimeType': 'text/plain',
                'buffer': payload.encode('utf-8')})
            expected_error = {'invalid.csv': 'Inconsistent CSV column count',
                              'invalid.tsv': 'unclosed quote',
                              'invalid.json': 'missing or unexpected columns'}[name]
            page.wait_for_function(
                '(message) => document.querySelector("#dt-status").textContent.includes(message)',
                arg=expected_error)
            assert page.evaluate('MathStudio.dataTables.exportState()') == before

        # Graphs must still reject a one-coordinate dataset.
        for fn, value in [('parseCSV', 'Value\n1\n'),
                          ('parseJSON', '[{"Value":1}]')]:
            result = page.evaluate(
                '([fn, value]) => { try { MathStudio.graphData[fn](value); '
                'return "accepted"; } catch (e) { return e.message; } }',
                [fn, value])
            assert result != 'accepted', (fn, result)
        page.locator('[data-workspace="graph"]').click()
        page.locator('#graph-data-file').set_input_files({
            'name': 'one.csv', 'mimeType': 'text/csv',
            'buffer': b'Value\n1\n'})
        page.wait_for_function(
            '() => document.querySelector("#graph-data-status").textContent.includes("Import failed")')
        assert not page.evaluate('MathStudio.graphData.hasData()')

        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#dt-import').count() == 1
        assert not errors, errors
        browser.close()
    print('PASS single-column CSV/TSV/JSON, formula round-trip, rollback and strict graph XY')


if __name__ == '__main__':
    main()
