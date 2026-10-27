"""Browser regression: XLSX formula translation must not corrupt function names or exponent literals."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    for name in ('xlsx-tools.js', 'xlsx-import.js'):
        assert (ROOT / 'src' / name).read_text(encoding='utf-8').rstrip('\n') in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium',
            args=['--no-sandbox'])
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(html, wait_until='load')
        original = 'IF(A1>0,LOG10(B1)+ATAN2(C1,D1)+1E3+totalA2,"A1")+\'Sales 2026\'!$C$2'
        excel = 'IF(A2>0,LOG10(B2)+ATAN2(C2,D2)+1E3+totalA2,"A1")+\'Sales 2026\'!$C$3'
        assert page.evaluate('formula => MathStudio.xlsxTools.formulaToExcel(formula)', original) == excel
        assert page.evaluate('formula => MathStudio.xlsxImport.fromExcel(formula)', excel) == original
        references = {
            'LOG10(A2)': 'LOG10(A1)',
            'ATAN2(A2,B2)': 'ATAN2(A1,B1)',
            '1E3+A2': '1E3+A1',
            'totalA2+A2': 'totalA2+A1',
        }
        for name, expected in references.items():
            converted = page.evaluate('formula => MathStudio.xlsxImport.fromExcel(formula)', name)
            assert converted == expected, (name, converted)
        assert page.evaluate("""() => {
            try { MathStudio.xlsxImport.fromExcel('SUM(A1:A2)'); return false; }
            catch(e) { return e.message.includes('header'); }
        }""")
        assert not errors, errors
        browser.close()
    print('PASS: XLSX formula references preserve LOG10, ATAN2, scientific notation, names and quoted text')

if __name__ == '__main__':
    main()
