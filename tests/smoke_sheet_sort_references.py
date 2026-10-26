"""Browser regression: stable row sort preserves formula identities across sheets."""
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
            {"id":"sheet-1","name":"Data1","columns":["A","B","C"],"rows":[
                ["20","=A1+1","=SUM(A1:A3)"],["5","=A2+1",""],["10","=A3+1",""]]},
            {"id":"sheet-2","name":"Other","columns":["A","B"],"rows":[
                ["=Data1!$A$1+Data1!A2","='Data1'!B3"]]}]}
        page.evaluate("(s) => MathStudio.dataTables.restoreState(s)", state)
        assert page.evaluate("MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0]") == [25,11]
        page.locator("#dt-sortcol").select_option("0")
        page.locator("#dt-sort").click()
        assert page.evaluate("MathStudio.dataTables.active.rows.map(r => r[0])") == ["5","10","20"]
        assert page.evaluate("MathStudio.dataTables.active.rows.map(r => r[1])") == ["=A1+1","=A2+1","=A3+1"]
        assert page.evaluate("MathStudio.dataTables.active.rows[2][2]") == "=SUM(A1:A3)"
        assert page.evaluate("MathStudio.dataTables.calculate()[2][2]") == 35
        assert page.evaluate("MathStudio.dataTables.tables[1].rows[0]") == ["=Data1!$A$3+Data1!A1","='Data1'!B2"]
        assert page.evaluate("MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0]") == [25,11]
        saved = page.evaluate("MathStudio.dataTables.exportState()")
        page.evaluate("(s) => MathStudio.dataTables.restoreState(s)", saved)
        assert page.evaluate("MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0]") == [25,11]
        page.evaluate("MathStudio.dataTables.sortRows(0,'desc')")
        assert page.evaluate("MathStudio.dataTables.active.rows.map(r => r[0])") == ["20","10","5"]
        assert page.evaluate("MathStudio.dataTables.calculate(MathStudio.dataTables.tables[1])[0]") == [25,11]
        page.evaluate("(s) => MathStudio.dataTables.restoreState(s)", state)
        page.evaluate("MathStudio.dataTables.active.rows[0][2]='=SUM(A1:A2)'")
        before = page.evaluate("MathStudio.dataTables.exportState()")
        page.locator("#dt-sort").click()
        assert "noncontiguous" in page.locator("#dt-status").inner_text()
        assert page.evaluate("MathStudio.dataTables.exportState()") == before
        assert page.evaluate("""() => {try {MathStudio.dataTables.sortRows(99);return false;}
            catch(e){return /Invalid sort column/.test(e.message);}}""")
        assert page.evaluate("MathStudio.dataTables.exportState()") == before
        page.evaluate("""() => MathStudio.dataTables.restoreState({version:1,selected:'sheet-1',
            tables:[{id:'sheet-1',name:'Data1',columns:['A','B'],
            rows:[['2','first'],['1','low'],['2','second']]}]})""")
        page.evaluate("MathStudio.dataTables.sortRows(0,'asc')")
        assert page.evaluate("MathStudio.dataTables.active.rows.map(r => r[1])") == ["low","first","second"]
        assert not errors,errors
        browser.close()
    print("PASS stable sort, cross-sheet references, ranges, rollback and persistence")

if __name__ == "__main__":
    main()
