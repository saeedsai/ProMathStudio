"""Saved custom-function schema validation (v1/v2), offline parity and CI registration."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = r"""
const fs=require('fs');global.window={MathStudio:{}};
new Function(fs.readFileSync('src/project-schema.js','utf8'))();
const out=[];for(const c of JSON.parse(process.argv[1])){try{const r=window.MathStudio.projectSchema.migrate(c);out.push({ok:true,version:r.version,fns:r.customFunctions});}catch(e){out.push({ok:false,error:e.message});}}
process.stdout.write(JSON.stringify(out));
"""


def project(version, functions="omit"):
    data = {"format": "mathstudio-project", "version": version, "notebook": []}
    if functions != "omit":
        data["customFunctions"] = functions
    return data


@unittest.skipUnless(shutil.which("node"), "Node required")
class CustomFunctionSchemaTests(unittest.TestCase):
    def run_cases(self, cases):
        done = subprocess.run(["node", "-e", SCRIPT, json.dumps(cases)], cwd=ROOT, capture_output=True,
                              text=True, check=True, timeout=60)
        return json.loads(done.stdout)

    def test_valid_and_legacy(self):
        valid = [{"name": "f", "params": ["x", "y"], "expression": "x*y", "source": "x*y", "type": "formula"},
                 {"name": "g_2", "params": ["t"], "expression": "", "source": "def g_2(t):\n  return t", "type": "python"},
                 {"name": "h", "params": ["a"], "expression": "a+1"}]
        sixty = [{"name": "f%d" % i, "params": ["x"], "expression": "x"} for i in range(60)]
        cases = [project(v, fn) for v in (1, 2) for fn in ("omit", [], valid, sixty)]
        for result in self.run_cases(cases):
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["version"], 2)

    def test_malformed_rejected(self):
        bad = [
            {"name": "f"},
            [{"name": "1f", "params": ["x"], "expression": "x"}],
            [{"name": "f-g", "params": ["x"], "expression": "x"}],
            [{"name": "f" * 65, "params": ["x"], "expression": "x"}],
            [{"name": "f", "params": [], "expression": "x"}],
            [{"name": "f", "params": ["x"] * 2, "expression": "x"}],
            [{"name": "f", "params": list("abcdefg"), "expression": "x"}],
            [{"name": "f", "params": ["2x"], "expression": "x"}],
            [{"name": "f", "params": "x", "expression": "x"}],
            [{"name": "f", "params": ["x"]}],
            [{"name": "f", "params": ["x"], "expression": "x" * 12001}],
            [{"name": "f", "params": ["x"], "expression": "x", "source": 5}],
            [{"name": "f", "params": ["x"], "expression": "x", "type": "js"}],
            [{"name": "f", "params": ["x"], "expression": "x"}, {"name": "F", "params": ["x"], "expression": "x"}],
            [{"name": "f%d" % i, "params": ["x"], "expression": "x"} for i in range(61)],
            ["f"],
            None,
        ]
        cases = [project(v, fn) for v in (1, 2) for fn in bad]
        for case, result in zip(cases, self.run_cases(cases)):
            self.assertFalse(result["ok"], case)
            self.assertRegex(result["error"], r"^Invalid project: (duplicate )?custom function", result)

    def test_parity_and_registration(self):
        source = (ROOT / "src/project-schema.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-project-schema">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_project_atomic_import.py", workflow)


if __name__ == "__main__":
    unittest.main()
