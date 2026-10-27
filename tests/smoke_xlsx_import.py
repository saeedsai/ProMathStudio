"""Offline XLSX import round-trip, DEFLATE, malicious ZIP rejection and transactional browser regression."""
from pathlib import Path
import io
import os
import zipfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def repack(data, compression=zipfile.ZIP_STORED, transform=None, extra=None):
    with zipfile.ZipFile(io.BytesIO(data)) as original:
        entries = [(n, original.read(n)) for n in original.namelist()]
    if transform:
        entries = [(n, transform(n, content)) for n, content in entries]
    if extra:
        entries.extend(extra)
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=compression) as target:
        for name, content in entries:
            target.writestr(name, content)
    return output.getvalue()

def main():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    source = (ROOT / 'src/xlsx-import.js').read_text(encoding='utf-8')
    assert source.rstrip('\n') in html
    assert 'python tests/smoke_xlsx_import.py' in (ROOT / '.github/workflows/quality.yml').read_text()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium',
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('dialog', lambda dialog: dialog.accept())
        page.set_content(html, wait_until='load')
        data = bytes(page.evaluate("""() => {
            const M = MathStudio;
            const a = M.dataTables.create('Sales 2026', ['qty', 'price', 'total'],
                [['2', '3', '=A1*B1'], ['4', '5', '=SUM(A1:A2)']]);
            const b = M.dataTables.create('Budget', ['total', 'note'],
                [["='Sales 2026'!C1", 'north & <south>'], ['001', '']]);
            return Array.from(M.xlsxTools.build({tables: [a, b]}));
        }"""))
        # Assert individual values without relying on object-key ordering.
        parsed = page.evaluate("""async bytes =>
            await MathStudio.xlsxImport.parse(new Uint8Array(bytes))""", list(data))
        assert [t['name'] for t in parsed] == ['Sales 2026', 'Budget']
        assert parsed[0]['rows'][0] == ['2', '3', '=A1*B1']
        assert parsed[0]['rows'][1][2] == '=SUM(A1:A2)'
        assert parsed[1]['rows'][0] == ["='Sales 2026'!C1", 'north & <south>']
        assert parsed[1]['rows'][1][0] == '001'
        assert page.evaluate("""() => MathStudio.xlsxImport.fromExcel(
            'IF(A2>0,"A2",SUM($B$3:B4))')""") == 'IF(A1>0,"A2",SUM($B$2:B3))'
        compressed = repack(data, zipfile.ZIP_DEFLATED)
        assert page.evaluate("""async bytes => (await MathStudio.xlsxImport.parse(
            new Uint8Array(bytes))).length""", list(compressed)) == 2

        corrupted = data.replace(b'north', b'south', 1)
        assert corrupted != data
        duplicate = repack(data, transform=lambda n, c: (
            c.replace(b'name="Budget"', b'name="Sales 2026"') if n == 'xl/workbook.xml' else c))
        external = repack(data, extra=[('xl/externalLinks/externalLink1.xml', b'<link/>')])
        header_ref = repack(data, transform=lambda n, c: (
            c.replace(b'<f>A2*B2</f>', b'<f>A1*B2</f>')
            if n == 'xl/worksheets/sheet1.xml' else c))
        bomb = bytearray(data)
        central = bomb.find(b'PK\x01\x02')
        assert central > 0
        bomb[central+24:central+28] = (6000000).to_bytes(4, 'little')
        bad = [corrupted, duplicate, external, header_ref, bytes(bomb), b'not a zip']
        original_state = page.evaluate('JSON.stringify(MathStudio.dataTables.exportState())')
        for archive in bad:
            result = page.evaluate("""async bytes => {
                try { await MathStudio.xlsxImport.load(new Uint8Array(bytes)); return 'accepted'; }
                catch(e) { return e.message; }
            }""", list(archive))
            assert result.startswith('XLSX import:'), result
            assert page.evaluate('JSON.stringify(MathStudio.dataTables.exportState())') == original_state

        assert page.evaluate("""async bytes => await MathStudio.xlsxImport.load(
            new Uint8Array(bytes))""", list(data)) == 2
        assert page.evaluate('MathStudio.dataTables.tables.length') == 2
        assert page.evaluate('MathStudio.dataTables.tables[0].rows[0][2]') == '=A1*B1'
        page.locator('[data-workspace="data"]').click()
        page.locator('#xlsx-import-details').evaluate('(el) => el.open = true')
        page.locator('#xlsx-import-file').set_input_files({
            'name': 'roundtrip.xlsx',
            'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'buffer': compressed,
        })
        page.locator('#xlsx-import').click()
        page.wait_for_function("""() => document.querySelector(
            '#xlsx-import-status').textContent.includes('Imported 2 sheet(s)')""")
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.locator('#xlsx-import').is_visible()
        assert not errors, errors
        browser.close()
    print('PASS: XLSX stored/DEFLATE import, two-sheet round-trip, malicious archives, rollback and browser UI')

if __name__ == '__main__':
    main()
