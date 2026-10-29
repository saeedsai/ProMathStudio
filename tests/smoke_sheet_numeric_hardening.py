"""Browser regression: reserved aggregate names, finite means and nonfinite errors."""
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
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"),
                         wait_until="load")
        page.locator('[data-workspace="data"]').click()
        page.evaluate("""() => {
          MathStudio.customFunctions.restore([
            {name:'SUM',params:['x','y'],expression:'99',type:'formula'},
            {name:'COUNT',params:['x','y'],expression:'99',type:'formula'},
            {name:'MEDIAN',params:['x','y'],expression:'99',type:'formula'},
            {name:'IF',params:['a','b','c'],expression:'99',type:'formula'},
            {name:'TWICE',params:['x'],expression:'2*x',type:'formula'},
            {name:'BROKEN',params:['x'],expression:'x/0',type:'formula'}
          ]);
          MathStudio.dataTables.restoreState({
            version:1,selected:'sheet-1',tables:[{
              id:'sheet-1',name:'Data1',
              columns:['A','B','C','D','E','F'],
              rows:[['1','=SUM(1e308,1e308)',
                     '=AVERAGE(1e308,1e308)',
                     '=IF(0,SUM(1e308,1e308),TWICE(4))',
                     '=BROKEN(2)',
                     '=SUM(TWICE(2),3)']]
            }]
          });
        }""")
        values = page.evaluate("MathStudio.dataTables.calculate()")
        assert values == [[1, '#NUM!', 1e308, 8, '#VALUE', 7]], values

        def formula(expression):
            return page.evaluate(
                "(expr) => MathStudio.dataTables.formula(expr,'Data1')",
                expression)

        def failure(expression):
            return page.evaluate("""(expr) => {
              try { MathStudio.dataTables.formula(expr,'Data1'); }
              catch(error) { return error.message; }
              return 'NO_ERROR';
            }""", expression)

        # Imported/saved names must not override spreadsheet built-ins.
        assert formula('SUM(2,3)') == 5
        assert formula('COUNT(2,3)') == 2
        assert formula('MEDIAN(1,3)') == 2
        assert formula('IF(1,COUNT(2,3),BROKEN(1))') == 2
        assert formula('SUM(TWICE(2),SUM(1,2))') == 7

        # Finite averages stay finite even if an intermediate sum would overflow.
        assert formula('AVERAGE(1e308,1e308)') == 1e308
        assert formula('AVG(1e308,1e308)') == 1e308
        assert formula('AVERAGE(1e308,-1e308)') == 0
        assert formula('MEDIAN(1e308,1e308)') == 1e308
        assert formula('SUM(1e308,-1e308)') == 0
        assert failure('SUM(1e308,1e308)') == '#NUM!'
        assert failure('SUM(TWICE(1e308),2)') == '#VALUE'
        assert failure('BROKEN(2)') == '#VALUE'
        assert failure('COUNT(BROKEN(1))') == '#VALUE'
        assert formula('IF(0,BROKEN(1),SUM(1,2))') == 3

        state = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", state)
        assert page.evaluate("MathStudio.dataTables.calculate()") == values
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 850})
            assert page.locator('#dt-sheet').count() == 1
        assert not errors, errors
        browser.close()
    print("PASS spreadsheet built-in priority, finite averages, overflow and custom errors")


if __name__ == "__main__":
    main()
