"""Browser regression: structural row/column edits preserve ranges and failed row inserts are atomic."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="data"]').click()
        state = {"version":1,"selected":"sheet-1","tables":[
            {"id":"sheet-1","name":"My Data","columns":["A","B"],"rows":[
                ["2","3"],["4","5"],["6","7"],["8","9"]]},
            {"id":"sheet-2","name":"Other","columns":["A","B","C","D"],"rows":[
                ["=SUM('My Data'!$A$1:$A$4)", "=SUM('My Data'!B1:B4)",
                 "='My Data'!A4", "=SUM('My Data'!A2:A2)"]]}]}
        page.evaluate("(s) => MathStudio.dataTables.restoreState(s)", state)
        other = "MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0]"
        assert page.evaluate(other) == [20,24,8,4]
        page.evaluate("MathStudio.dataTables.deleteRow(1)")
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0]") == [
            "=SUM('My Data'!$A$1:$A$3)", "=SUM('My Data'!B1:B3)",
            "='My Data'!A3", "=SUM(#REF!)"]
        assert page.evaluate(other) == [16,19,8,"#REF!"]
        saved = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(s) => MathStudio.dataTables.restoreState(s)", saved)
        assert page.evaluate(other) == [16,19,8,"#REF!"]
        page.evaluate("MathStudio.dataTables.insertRow(1)")
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0][0]") == "=SUM('My Data'!$A$1:$A$4)"
        assert page.evaluate(other) == [16,19,8,"#REF!"]
        page.evaluate("MathStudio.dataTables.deleteColumn(0)")
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0]") == [
            "=SUM(#REF!)", "=SUM('My Data'!A1:A4)", "=#REF!", "=SUM(#REF!)"]
        assert page.evaluate(other) == ["#REF!",19,"#REF!","#REF!"]
        page.evaluate("""() => MathStudio.dataTables.restoreState({version:1,selected:'sheet-1',
            tables:[{id:'sheet-1',name:'Data1',columns:['A','B'],rows:[
              ['2','=SUM(A1:A4)'],['4','=SUM(A2:A3)'],
              ['6','=SUM(A1:A1)'],['8','=SUM(A3:A4)']]}]})""")
        page.evaluate("MathStudio.dataTables.deleteRow(0)")
        assert page.evaluate("MathStudio.dataTables.active.rows.map(r => r[1])") == [
            "=SUM(A1:A2)","=SUM(#REF!)","=SUM(A2:A3)"]
        assert page.evaluate("MathStudio.dataTables.calculate().map(r => r[1])") == [10,"#REF!",14]

        # Structural edits must not turn an already out-of-grid reference into a valid cell.
        page.evaluate("""() => MathStudio.dataTables.restoreState({version:1,selected:'sheet-1',tables:[
            {id:'sheet-1',name:'Data',columns:['A'],rows:[['10'],['30']]},
            {id:'sheet-2',name:'Refs',columns:['A','B','C'],rows:[[
                '=Data!A2','=Data!A6001','=SUM(Data!A6001:A6001)'
            ]]}
        ]})""")
        row_refs = "MathStudio.dataTables.tables[1].rows[0]"
        row_values = "MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0]"
        assert page.evaluate(row_values) == [30, "#REF!", "#REF!"]
        page.evaluate("MathStudio.dataTables.deleteRow(0)")
        assert page.evaluate(row_refs) == ["=Data!A1", "=Data!A6001", "=SUM(Data!A6001:A6001)"]
        assert page.evaluate(row_values) == [30, "#REF!", "#REF!"]

        page.evaluate("""() => MathStudio.dataTables.restoreState({version:1,selected:'sheet-1',tables:[
            {id:'sheet-1',name:'Data',columns:['A','B'],rows:[['10','20']]},
            {id:'sheet-2',name:'Refs',columns:['A','B','C'],rows:[[
                '=Data!B1','=Data!AG1','=SUM(Data!AG1:AG1)'
            ]]}
        ]})""")
        column_refs = "MathStudio.dataTables.tables[1].rows[0]"
        column_values = "MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0]"
        assert page.evaluate(column_values) == [20, "#REF!", "#REF!"]
        page.evaluate("MathStudio.dataTables.deleteColumn(0)")
        assert page.evaluate(column_refs) == ["=Data!A1", "=Data!AG1", "=SUM(Data!AG1:AG1)"]
        assert page.evaluate(column_values) == [20, "#REF!", "#REF!"]

        # A failed cell-value conversion must not leave cross-sheet references shifted.
        page.evaluate("""() => MathStudio.dataTables.restoreState({version:1,selected:'sheet-1',tables:[
            {id:'sheet-1',name:'Data',columns:['A'],rows:[['10'],['20']]},
            {id:'sheet-2',name:'Refs',columns:['A'],rows:[['=Data!A2']]}
        ]})""")
        rollback = page.evaluate("""() => {
            const before = JSON.stringify(MathStudio.dataTables.exportState());
            let message = '';
            try {
                MathStudio.dataTables.insertRow(0, [{toString(){throw Error('conversion failed')}}]);
            } catch (error) { message = error.message; }
            return {message,before,after:JSON.stringify(MathStudio.dataTables.exportState()),
                reference:MathStudio.dataTables.tables[1].rows[0][0],
                rowCount:MathStudio.dataTables.tables[0].rows.length};
        }""")
        assert rollback["message"] == "conversion failed"
        assert rollback["before"] == rollback["after"]
        assert rollback["reference"] == "=Data!A2"
        assert rollback["rowCount"] == 2

        # A later formula-cell conversion error must not partially commit earlier rewrites.
        staged = page.evaluate("""() => {
            MathStudio.dataTables.restoreState({version:1,selected:'sheet-1',tables:[
                {id:'sheet-1',name:'Data',columns:['A'],rows:[['=A2'],['10']]},
                {id:'sheet-2',name:'Refs',columns:['A','B'],rows:[['=Data!A2','safe']]}
            ]});
            const tables = MathStudio.dataTables.tables;
            tables[1].rows[0][1] = {toString(){throw Error('formula conversion failed');}};
            const before = JSON.stringify(MathStudio.dataTables.exportState());
            let message = '';
            try { MathStudio.dataTables.insertRow(0); }
            catch (error) { message = error.message; }
            const afterFailure = JSON.stringify(MathStudio.dataTables.exportState());
            const failed = {
                message, before, afterFailure,
                localFormula: tables[0].rows[0][0],
                crossSheetFormula: tables[1].rows[0][0],
                rowCount: tables[0].rows.length
            };
            tables[1].rows[0][1] = 'safe';
            MathStudio.dataTables.insertRow(0);
            return {...failed, recoveredLocal: tables[0].rows[1][0],
                recoveredCrossSheet: tables[1].rows[0][0],
                recoveredRowCount: tables[0].rows.length};
        }""")
        assert staged["message"] == "formula conversion failed"
        assert staged["before"] == staged["afterFailure"]
        assert staged["localFormula"] == "=A2"
        assert staged["crossSheetFormula"] == "=Data!A2"
        assert staged["rowCount"] == 2
        assert staged["recoveredLocal"] == "=A3"
        assert staged["recoveredCrossSheet"] == "=Data!A3"
        assert staged["recoveredRowCount"] == 3

        # Sheet rename must stage every formula rewrite before mutating any sheet.
        page.evaluate("""() => MathStudio.dataTables.restoreState({version:1,selected:'sheet-1',tables:[
            {id:'sheet-1',name:'Data',columns:['A'],rows:[['10']]},
            {id:'sheet-2',name:'Refs',columns:['A','B'],rows:[
                ['=Data!A1','="Data!A1"'],
                ['=Data!A1','safe']
            ]}
        ]})""")
        page.evaluate("""() => {
            MathStudio.dataTables.tables[1].rows[1][1] = {
                toString(){throw Error('formula conversion failed');}
            };
        }""")
        page.once("dialog", lambda dialog: dialog.accept("Renamed Sheet"))
        page.locator("#dt-rename").click()
        failed_rename = page.evaluate("""() => ({
            name: MathStudio.dataTables.tables[0].name,
            first: MathStudio.dataTables.tables[1].rows[0][0],
            later: MathStudio.dataTables.tables[1].rows[1][0],
            literal: MathStudio.dataTables.tables[1].rows[0][1]
        })""")
        assert failed_rename == {
            "name": "Data",
            "first": "=Data!A1",
            "later": "=Data!A1",
            "literal": '="Data!A1"'
        }
        page.evaluate("MathStudio.dataTables.tables[1].rows[1][1] = 'safe'")
        page.once("dialog", lambda dialog: dialog.accept("Renamed Sheet"))
        page.locator("#dt-rename").click()
        renamed = page.evaluate("""() => ({
            name: MathStudio.dataTables.tables[0].name,
            first: MathStudio.dataTables.tables[1].rows[0][0],
            later: MathStudio.dataTables.tables[1].rows[1][0],
            literal: MathStudio.dataTables.tables[1].rows[0][1]
        })""")
        assert renamed == {
            "name": "Renamed Sheet",
            "first": "='Renamed Sheet'!A1",
            "later": "='Renamed Sheet'!A1",
            "literal": '="Data!A1"'
        }

        assert not errors, errors
        browser.close()
    print("PASS row/column range edits, invalid-reference preservation, cross-sheet anchors, conversion-failure atomicity, persistence and browser")

if __name__ == "__main__":
    main()
