"""Browser regression: MEDIAN, existing formulas, invalid ranges and library insertion."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="data"]').click()
        page.evaluate("""() => MathStudio.dataTables.restoreState({
          version:1, selected:'sheet-1', tables:[
            {id:'sheet-1',name:'Data1',columns:['A','B','C','D','E','F','G','H','I','J'],rows:[
              ['1','text','=MEDIAN(A1:A3)','=SUM(A1:A5)','=IF(A1>0,MEDIAN(A1:A3),99)','=MEDIAN(A0:A2)','=MEDIAN(A1:A3)','','=MIN(A1:A3)','=MEDIAN(B1:B3)'],
              ['4','','=MEDIAN(A1:A2)','=AVERAGE(A1:A3)',"=MEDIAN('Other Data'!A1:A3)",'=MEDIAN(A1:AG1)','=MEDIAN(G2:G2)','','=MAX(A1:A3)',''],
              ['8','2','=MEDIAN(A1:A3,B3)','=COUNT(A1:A3,B1:B3)','=MEDIAN(B1:B2)',"=MEDIAN('Missing'!A1:A2)",'=MEDIAN(A1:A3)','','=SUM(A1:A3)','']
            ]},
            {id:'sheet-2',name:'Other Data',columns:['A'],rows:[['9'],['7'],['5']]}
          ]
        })""")
        values = page.evaluate("MathStudio.dataTables.calculate()")
        assert [values[i][2] for i in range(3)] == [4, 2.5, 3], values
        assert values[0][3] == 13 and abs(values[1][3] - 13/3) < 1e-10 and values[2][3] == 4
        assert [values[i][4] for i in range(3)] == [4, 7, '#NUM!']
        assert [values[i][5] for i in range(3)] == ['#REF!', '#REF!', '#SHEET']
        assert values[1][6] == '#CYCLE'
        assert [values[i][8] for i in range(3)] == [1, 8, 13]
        assert values[0][9] == 2
        assert page.evaluate("MathStudio.dataTables.formula('MEDIAN(1,2,3,4)','Data1')") == 2.5
        assert page.evaluate("MathStudio.dataTables.formula('MEDIAN(1,2,3)','Data1')") == 2
        # In-grid but unpopulated rows are blank, not zero-valued observations.
        assert page.evaluate("MathStudio.dataTables.formula('MEDIAN(A1:A5)','Data1')") == 4
        assert page.evaluate("MathStudio.dataTables.formula('COUNT(A1:A5)','Data1')") == 3
        assert abs(page.evaluate("MathStudio.dataTables.formula('AVERAGE(A1:A5)','Data1')") - 13/3) < 1e-10
        page.locator('#dt-code-library summary').click()
        page.locator('#dt-sheet td input[data-row="0"][data-col="7"]').click()
        page.locator('#dt-library-search').fill('median')
        page.get_by_role('button', name='Insert MEDIAN').click()
        assert page.evaluate("MathStudio.dataTables.active.rows[0][7]") == '=MEDIAN(A1:A5)'
        assert page.evaluate("MathStudio.dataTables.calculate()[0][7]") == 4
        state = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", state)
        assert page.evaluate("MathStudio.dataTables.calculate()[0][7]") == 4
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 850})
            assert page.locator('#dt-library-search').count() == 1
        assert not errors, errors
        browser.close()
    print("PASS MEDIAN odd/even, ranges, cross-sheet, errors, insertion, persistence")

if __name__ == "__main__":
    main()
