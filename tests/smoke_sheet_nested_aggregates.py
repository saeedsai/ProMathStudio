"""Nested spreadsheet aggregates: numeric oracle, references, errors and library UI."""
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
        page.evaluate("""() => MathStudio.dataTables.restoreState({
          version:1,selected:'sheet-1',tables:[
            {id:'sheet-1',name:'Data1',
             columns:['A','B','C','D','E','F','G','H','I','J','K','L','M'],
             rows:[
               ['1','text',
                '=SUM(MEDIAN(A1:A5),COUNT(A1:A5))',
                '=SUM(AVERAGE(A1:A5),MAX(A1:A5))',
                '=SUM(MIN(A1:A5),SUM(MAX(A1:A5),MEDIAN(A1:A5)))',
                '=SUM(MEDIAN(A1:A5),IF(A1>0,COUNT(A1:A5),0))',
                "=SUM(MEDIAN('Other Data'!A1:A3),COUNT(A1:A5))",
                '=SUM(MEDIAN(A1:A5),COUNT(A1:A5),2^3)',
                '=SUM(MEDIAN(A1:A5),MEDIAN(B1:B3))',
                '=SUM(MEDIAN(A1:A5),MEDIAN(B1:B2))',
                '=SUM(MEDIAN(A1:ZZ1),1)',
                '=SUM(MEDIAN(L1:L1),1)',
                '=SUM(MEDIAN(A1:A5),1)'],
               ['4','','','','','','','','','','','',''],
               ['8','2','','','','','','','','','','','']
             ]},
            {id:'sheet-2',name:'Other Data',columns:['A'],
             rows:[['9'],['7'],['5']]}
          ]
        })""")
        values = page.evaluate("MathStudio.dataTables.calculate()")
        row = values[0]
        assert row[2] == 7, values
        assert abs(row[3] - (13 / 3 + 8)) < 1e-10, values
        assert row[4:9] == [13, 7, 10, 15, 6], values
        assert row[9:12] == ['#NUM!', '#REF!', '#CYCLE'], values
        assert row[12] == 5, values
        assert page.evaluate(
            "MathStudio.dataTables.formula('COUNT(MEDIAN(A1:A5),MAX(A1:A5))','Data1')"
        ) == 2
        assert page.evaluate(
            "MathStudio.dataTables.formula('SUM(IF(A1>0,MEDIAN(A1:A5),0),COUNT(A1:A5))','Data1')"
        ) == 7
        assert page.evaluate(
            "MathStudio.dataTables.formula('SUM(1,2)','Data1')"
        ) == 3
        # A negative aggregate is still a scalar in multiplication and powers.
        assert page.evaluate(
            "MathStudio.dataTables.formula('SUM(2*SUM(-3))','Data1')"
        ) == -6
        assert page.evaluate(
            "MathStudio.dataTables.formula('SUM(-2)^2','Data1')"
        ) == 4
        deep_error = page.evaluate("""() => {
          try { MathStudio.dataTables.formula('SUM('.repeat(41)+'1'+')'.repeat(41),'Data1'); }
          catch(e) { return e.message; }
          return 'NO_ERROR';
        }""")
        assert deep_error == '#LIMIT', deep_error

        # The new library example is discoverable and inserts an editable formula.
        page.locator('#dt-code-library summary').click()
        page.locator('#dt-sheet td input[data-row="1"][data-col="12"]').click()
        page.locator('#dt-library-search').fill('Nested aggregates')
        page.get_by_role('button', name='Insert Nested aggregates').click()
        assert page.evaluate('MathStudio.dataTables.active.rows[1][12]') == (
            '=SUM(MEDIAN(A1:A5),COUNT(A1:A5))')
        assert page.evaluate('MathStudio.dataTables.calculate()[1][12]') == 7
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 850})
            assert page.locator('#dt-library-search').count() == 1
        assert not errors, errors
        browser.close()
    print("PASS nested aggregates, IF, cross-table, blanks, cycle, bounds and library UI")


if __name__ == "__main__":
    main()
