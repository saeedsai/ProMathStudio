"""Custom spreadsheet functions composed with nested aggregates, IF and references."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="data"]').click()
        page.evaluate("""() => {
          MathStudio.customFunctions.restore([
            {name:'TWICE',params:['x'],expression:'2*x',type:'formula'},
            {name:'SHIFT',params:['x'],expression:'x+3',type:'formula'}
          ]);
          MathStudio.dataTables.restoreState({
            version:1,selected:'sheet-1',tables:[{
              id:'sheet-1',name:'Data1',columns:['A','B','C'],
              rows:[
                ['1','=TWICE(SUM(A1:A3))','=SUM(TWICE(A1),TWICE(SUM(A1:A3)),SHIFT(TWICE(2)))'],
                ['2','=IF(0,TWICE(1/0),SHIFT(2))','=SUM(TWICE(2),MEDIAN(A1:A3))'],
                ['4','=TWICE(TWICE(3))','=TWICE(2)+TWICE(3)']
              ]
            }]
          });
        }""")
        rows = page.evaluate("MathStudio.dataTables.calculate()")
        assert [row[1:] for row in rows] == [[14, 23], [5, 6], [12, 10]], rows
        assert page.evaluate(
            "MathStudio.dataTables.formula('TWICE(SUM(A1:A3))','Data1')"
        ) == 14
        assert page.evaluate(
            "MathStudio.dataTables.formula('SUM(TWICE(2),SHIFT(TWICE(1)))','Data1')"
        ) == 9
        assert page.evaluate(
            "MathStudio.dataTables.formula('IF(0,UNKNOWN(2),TWICE(3))','Data1')"
        ) == 6
        assert page.evaluate(
            "MathStudio.dataTables.formula('SUM(1,2)','Data1')"
        ) == 3

        def failure(expression):
            return page.evaluate("""(expr) => {
              try { MathStudio.dataTables.formula(expr,'Data1'); }
              catch (error) { return error.message; }
              return 'NO_ERROR';
            }""", expression)

        assert failure('TWICE(1,2)') == '#ARGS'
        assert failure('TWICE()') == '#ARGS'
        assert failure('UNKNOWN(2)') == '#FORMULA'
        assert failure('TWICE(' * 41 + '1' + ')' * 41) == '#LIMIT'
        assert failure('TWICE(1/0)') == '#VALUE'

        # Workbook round-trip preserves editable formulas, not only results.
        state = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(s) => MathStudio.dataTables.restoreState(s)", state)
        assert page.evaluate("MathStudio.dataTables.calculate()") == rows
        assert page.locator('#dt-sheet input[aria-label="B1"]').input_value() == '14'
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 850})
            assert page.locator('#dt-sheet').count() == 1
        assert not errors, errors
        browser.close()
    print("PASS nested custom/aggregate/IF spreadsheet formulas, bounds, errors, persistence and mobile")


if __name__ == "__main__":
    main()
