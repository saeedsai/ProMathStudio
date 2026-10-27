"""Browser regression for lazy nested spreadsheet IF and project persistence."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 860})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="data"]').click()
        page.evaluate("""() => MathStudio.dataTables.restoreState({
            version:1, selected:'sheet-1', tables:[
              {id:'sheet-1',name:'Data1',columns:['A','B','C'],rows:[
                ['2','7','=IF(A1>0,IF(B1>3,B1+1,0),99)'],
                ['1','0','=2+IF(A2>0,IF(B1>2,5,0),0)'],
                ['1','0','=IF(IF(A1>0,1,0)=1,12,0)'],
                ['1','0','=IF(1,IF(0,#REF!,4),0)'],
                ['1','0','=IF(1,5,C5)'],
                ['1','0','=IF(1,C6,0)'],
                ['1','0','=IF(1,2)'],
                ['1','0','=IF(1,2,3'],
                ['1','0','=SUM(IF(A1>0,2,0),IF(A1<0,9,3))'],
                ['1','0','=IF(0,1/0,6)']
              ]},
              {id:'sheet-2',name:'Other Data',columns:['A','B'],rows:[
                ['3',"=IF('Other Data'!A1>0,Data1!B1,0)"],
                ['0','=IF(1,7,Data1!C6)']
              ]}
            ]
          })""")
        expected = [8, 7, 12, 4, 5, "#CYCLE", "#IF", "#IF", 5, 6]
        assert [row[2] for row in page.evaluate("MathStudio.dataTables.calculate()")] == expected
        assert page.locator('#dt-sheet input[aria-label="C1"]').input_value() == "8"
        assert page.evaluate(
            "MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])"
        ) == [[3, 7], [0, 7]]
        assert page.evaluate(
            "MathStudio.dataTables.formula('IF(1,IF(0,100,11),12)','Data1')"
        ) == 11
        saved = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(s) => MathStudio.dataTables.restoreState(s)", saved)
        assert [row[2] for row in page.evaluate("MathStudio.dataTables.calculate()")] == expected
        assert page.evaluate(
            "MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])"
        ) == [[3, 7], [0, 7]]
        assert not errors, errors
        browser.close()
    print("PASS nested/lazy IF, arithmetic, cross-sheet, #REF! skip, cycle, malformed IF, UI and round-trip")


if __name__ == "__main__":
    main()
