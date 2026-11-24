"""Structural spreadsheet reference regression: row/column edits and cross-sheet links."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1300, "height": 900})
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="data"]').click()
        page.evaluate("""() => MathStudio.dataTables.restoreState({
          version:1, selected:'sheet-1', tables:[
            {id:'sheet-1',name:'Data1',columns:['A','B','C'],rows:[
              ['2','3','=A1+B1'],['4','5','=SUM($A$1:A2)'],['6','7','=A3']
            ]},
            {id:'sheet-2',name:'Other',columns:['D','E'],rows:[
              ['=Data1!$A$2', "=Data1!B2+1"]
            ]}
          ]})""")
        assert page.evaluate("MathStudio.dataTables.calculate()[0][2]") == 5
        assert page.evaluate("MathStudio.dataTables.calculate()[1][2]") == 6
        page.evaluate("MathStudio.dataTables.insertRow(1)")
        assert page.evaluate("MathStudio.dataTables.tables[0].rows[2][2]") == "=SUM($A$1:A3)"
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0][0]") == "=Data1!$A$3"
        assert page.evaluate("MathStudio.dataTables.calculate()[2][2]") == 6
        page.evaluate("MathStudio.dataTables.insertColumn(1)")
        assert page.evaluate("MathStudio.dataTables.tables[0].rows[0][3]") == "=A1+C1"
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0][1]") == "=Data1!C3+1"
        assert page.evaluate("MathStudio.dataTables.calculate()[0][3]") == 5
        assert page.evaluate("MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0][0]") == 4
        page.evaluate("MathStudio.dataTables.deleteRow(0)")
        assert page.evaluate("MathStudio.dataTables.tables[0].rows[1][3]") == "=SUM($A$1:A2)"
        assert page.evaluate("MathStudio.dataTables.calculate()[1][3]") == 4
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0][0]") == "=Data1!$A$2"
        page.evaluate("MathStudio.dataTables.deleteColumn(0)")
        assert page.evaluate("MathStudio.dataTables.tables[0].rows[1][2]") == "=SUM(#REF!)"
        assert page.evaluate("MathStudio.dataTables.calculate()[1][2]") == "#REF!"
        assert page.evaluate("MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0][0]") == "#REF!"
        saved = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", saved)
        assert page.evaluate("MathStudio.dataTables.calculate()[1][2]") == "#REF!"
        # The context-menu row-number mapping must target the visible first data row.
        page.locator("#dt-sheet tbody th.dt-rownum").first.click(button="right")
        assert page.locator("#workspace-context-menu").is_visible()
        page.locator("#workspace-context-menu").get_by_text("Insert row above").click()
        assert page.evaluate("MathStudio.dataTables.active.rows[0].every(v => v==='')") is True
        page.evaluate("MathStudio.dataTables.active.rows[0][0]='=A1'")
        assert page.evaluate("MathStudio.dataTables.calculate()[0][0]") == "#CYCLE"

        # Escaped apostrophes in sheet names are doubled inside single-quoted qualifiers.
        quoted_state = {"version": 1, "selected": "sheet-1", "tables": [
            {"id": "sheet-1", "name": "Obrien", "columns": ["A"],
             "rows": [["20"], ["5"], ["10"]]},
            {"id": "sheet-2", "name": "Summary", "columns": ["A", "B", "C", "D", "E"],
             "rows": [[
                 "='O''Brien'!$A$1+'O''Brien'!A2",
                 "=SUM('O''Brien'!$A$1:A3)",
                 "=SUM('O''Brien'!A3:$A$1)",
                 "='O''Brien'!A3",
                 '="O\'\'Brien!A1"'
             ]]}
        ]}
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", quoted_state)
        page.evaluate("""() => {
            window.prompt = () => "O'Brien";
            document.getElementById('dt-rename').click();
        }""")
        assert page.evaluate("MathStudio.dataTables.tables[0].name") == "O'Brien"
        summary = "MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0]"
        assert page.evaluate(summary)[:4] == [25, 35, 35, 10]
        page.evaluate("MathStudio.dataTables.sortRows(0, 'asc')")
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0]") == [
            "='O''Brien'!$A$3+'O''Brien'!A1",
            "=SUM('O''Brien'!$A$1:A3)",
            "=SUM('O''Brien'!A3:$A$1)",
            "='O''Brien'!A2",
            '="O\'\'Brien!A1"'
        ]
        assert page.evaluate(summary)[:4] == [25, 35, 35, 10]
        page.evaluate("MathStudio.dataTables.insertRow(0)")
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0][:4]") == [
            "='O''Brien'!$A$4+'O''Brien'!A2",
            "=SUM('O''Brien'!$A$2:A4)",
            "=SUM('O''Brien'!A4:$A$2)",
            "='O''Brien'!A3"
        ]
        page.evaluate("MathStudio.dataTables.insertColumn(0)")
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0]") == [
            "='O''Brien'!$B$4+'O''Brien'!B2",
            "=SUM('O''Brien'!$B$2:B4)",
            "=SUM('O''Brien'!B4:$B$2)",
            "='O''Brien'!B3",
            '="O\'\'Brien!A1"'
        ]
        assert page.evaluate(summary)[:4] == [25, 35, 35, 10]
        saved = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", saved)
        assert page.evaluate(summary)[:4] == [25, 35, 35, 10]

        assert not errors, errors
        browser.close()
    print("PASS structural references, cross-sheet, absolute anchors, #REF!, project round-trip and context row index")


if __name__ == "__main__":
    main()
