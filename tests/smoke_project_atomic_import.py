"""Cross-module atomic project import: malformed v1/v2 fixtures and injected apply
failures preserve prior Matrix, Data Tables, notebook and custom-function state."""
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def snapshot(page):
    data = page.evaluate("MathStudio.bridge.export()")
    data.pop("date", None)
    return data


def upload(page, data, expect_failure):
    page.evaluate("document.querySelector('#hub-status').textContent=''")
    page.locator("#hub-project-file").set_input_files({
        "name": "project.json", "mimeType": "application/json",
        "buffer": json.dumps(data).encode("utf-8")})
    prefix = "Import failed:" if expect_failure else "Project imported."
    page.wait_for_function(
        "p => document.querySelector('#hub-status').textContent.startsWith(p)", arg=prefix)
    return page.locator("#hub-status").inner_text()


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        # Prior state: non-default Matrix draft, Data table and custom function.
        page.evaluate("""() => {
          const m = MathStudio.matrixTools.exportState();
          m.a = ['4', '1', '2', '3'];
          MathStudio.matrixTools.restoreState(m);
          const t = MathStudio.dataTables.exportState();
          t.tables[0].rows[0][0] = '42';
          MathStudio.dataTables.restoreState(t);
          MathStudio.customFunctions.restore([{name:'prior', params:['x'], expression:'x+1', source:'x+1', type:'formula'}]);
        }""")
        prior = snapshot(page)
        assert prior["matrix"]["a"] == ["4", "1", "2", "3"], prior["matrix"]
        assert prior["customFunctions"][0]["name"] == "prior"

        good = json.loads(json.dumps(prior))
        good["matrix"]["a"] = ["9", "8", "7", "6"]
        good["tables"]["tables"][0]["rows"][0][0] = "-1"
        good["customFunctions"] = [{"name": "imported", "params": ["x", "y"], "expression": "x*y", "type": "formula"}]
        good["working"] = "x+2"

        malformed = []
        for version in (1, 2):
            base = json.loads(json.dumps(good)); base["version"] = version
            bad = json.loads(json.dumps(base)); bad["tables"]["tables"][0]["columns"] = ["x", "X ", "z"]
            malformed.append(("duplicate columns v%d" % version, bad))
            bad = json.loads(json.dumps(base)); bad["customFunctions"] = [{"name": "1bad", "params": ["x"], "expression": "x"}]
            malformed.append(("bad function name v%d" % version, bad))
            bad = json.loads(json.dumps(base)); bad["customFunctions"] = [{"name": "f", "params": ["x"], "expression": "x"},
                                                                         {"name": "F", "params": ["y"], "expression": "y"}]
            malformed.append(("duplicate function v%d" % version, bad))
            bad = json.loads(json.dumps(base)); bad["customFunctions"] = [{"name": "f", "params": [], "expression": "1"}]
            malformed.append(("no arguments v%d" % version, bad))
            bad = json.loads(json.dumps(base)); bad["customFunctions"] = [{"name": "f%d" % i, "params": ["x"], "expression": "x"} for i in range(61)]
            malformed.append(("61 functions v%d" % version, bad))
            bad = json.loads(json.dumps(base)); bad["customFunctions"] = {"name": "f"}
            malformed.append(("function object v%d" % version, bad))
            bad = json.loads(json.dumps(base)); bad["matrix"]["weights"] = ["1"]
            malformed.append(("short weights v%d" % version, bad))
        for label, fixture in malformed:
            text = upload(page, fixture, True)
            assert "Invalid project" in text, (label, text)
            assert snapshot(page) == prior, label

        # Schema-valid fixture whose later module apply fails must roll back every
        # module already applied (engineering, notebook, calculator, Matrix, functions, graph).
        for target in ("dataTables", "curveFit"):
            page.evaluate("""target => {
              const api = MathStudio[target], original = api.restoreState;
              api.restoreState = function(state) {
                api.restoreState = original;
                throw Error('injected ' + target + ' failure');
              };
            }""", target)
            text = upload(page, good, True)
            assert "injected " + target + " failure" in text, text
            assert snapshot(page) == prior, target

        # v1 legacy project without matrix and customFunctions keys imports cleanly:
        # Matrix drafts are left as-is and functions are cleared, as before.
        legacy = json.loads(json.dumps(good)); legacy["version"] = 1
        legacy.pop("matrix"); legacy.pop("customFunctions"); legacy.pop("engineering")
        upload(page, legacy, False)
        after_legacy = snapshot(page)
        assert after_legacy["matrix"] == prior["matrix"], after_legacy["matrix"]
        assert after_legacy["tables"]["tables"][0]["rows"][0][0] == "-1"
        assert after_legacy["customFunctions"] == []

        # Valid v2 project imports every module and round-trips exactly.
        upload(page, good, False)
        imported = snapshot(page)
        assert imported["matrix"] == good["matrix"], imported["matrix"]
        assert imported["tables"] == good["tables"]
        assert imported["customFunctions"] == good["customFunctions"]
        assert imported["working"] == "x+2"
        upload(page, imported, False)
        assert snapshot(page) == imported
        assert not errors, errors
        browser.close()
    print("PASS atomic v1/v2 project import: malformed fixtures, injected rollback and round trip")


if __name__ == "__main__":
    main()
