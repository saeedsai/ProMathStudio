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
        assert page.evaluate("MathStudio.dataTables.tables[0].rows[1][3]") == "=SUM(#REF!:A2)"
        assert page.evaluate("MathStudio.dataTables.calculate()[1][3]") == "#REF!"
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0][0]") == "=Data1!$A$2"
        page.evaluate("MathStudio.dataTables.deleteColumn(0)")
        assert page.evaluate("MathStudio.dataTables.tables[0].rows[0][2]") == "=#REF!+B1" or page.evaluate("MathStudio.dataTables.tables[0].rows[0][2]") == "=#REF!+B1"
        assert page.evaluate("MathStudio.dataTables.calculate()[0][2]") == "#REF!"
        saved = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", saved)
        assert page.evaluate("MathStudio.dataTables.calculate()[0][2]") == "#REF!"
        # The context-menu row-number mapping must target the visible first data row.
        page.locator("#dt-sheet tbody th.dt-rownum").first.click(button="right")
        assert page.locator("#workspace-context-menu").is_visible()
        page.locator("#workspace-context-menu").get_by_text("Insert row above").click()
        assert page.evaluate("MathStudio.dataTables.active.rows[0].every(v => v==='')") is True
        assert not errors, errors
        browser.close()
    print("PASS structural references, cross-sheet, absolute anchors, #REF!, project round-trip and context row index")


if __name__ == "__main__":
    main()
