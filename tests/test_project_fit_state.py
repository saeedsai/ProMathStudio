"""Saved curve-fit preferences are validated before project restore mutates workspaces."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectFitStateTests(unittest.TestCase):
    def test_project_schema_bundle_parity_and_fit_restore_guard(self):
        source = (ROOT / "src/project-schema.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-project-schema">\n'
        start = html.index(marker) + len(marker)
        end = html.index("</script>", start)
        self.assertEqual(html[start:end].rstrip("\n"), source.rstrip("\n"))
        self.assertIn("saved curve-fit model is invalid.", source)
        self.assertIn("saved curve-fit degree is invalid.", source)
        self.assertIn("saved curve-fit equation", source)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_fit_state_enums_bounds_and_legacy_defaults(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const context={window:{MathStudio:{}}};
vm.runInNewContext(fs.readFileSync('src/project-schema.js','utf8'),context);
const migrate=context.window.MathStudio.projectSchema.migrate;
const base=()=>({format:'mathstudio-project',version:2,notebook:[]});
const models=['none','linear','poly','exp','log','power','gaussian'];
const degrees=['2','3','4','5','6'];
for(const model of models)for(const degree of degrees){
 const data=base();data.fit={model,degree,lastEquation:'y = 1 + 2*x'};
 const before=JSON.stringify(data),result=migrate(data);
 assert.equal(result.fit.model,model);assert.equal(result.fit.degree,degree);
 assert.equal(result.fit.lastEquation,'y = 1 + 2*x');
 assert.equal(JSON.stringify(data),before,'migration must not mutate source');
}
const empty=base();empty.fit={};
assert.deepEqual(JSON.parse(JSON.stringify(migrate(empty).fit)),{});
const legacy=base();legacy.version=1;legacy.fit={model:null,degree:'',lastEquation:null};
assert.equal(migrate(legacy).version,2);
assert.equal(migrate(legacy).fit.lastEquation,null);
const noFit=base();noFit.version=1;assert.equal(migrate(noFit).version,2);
const nullFit=base();nullFit.fit=null;assert.equal(migrate(nullFit).fit,null);
for(const value of ['unknown',3,false,{}]){
 const data=base();data.fit={model:value};
 assert.throws(()=>migrate(data),/saved curve-fit model is invalid/);
}
for(const value of ['7',2,false,[]]){
 const data=base();data.fit={degree:value};
 assert.throws(()=>migrate(data),/saved curve-fit degree is invalid/);
}
for(const value of [3,[],{},'x'.repeat(2001)]){
 const data=base();data.fit={lastEquation:value};
 assert.throws(()=>migrate(data),/saved curve-fit equation/);
}
const overLimit=base();overLimit.fit={lastEquation:'x'.repeat(2000)};
assert.equal(migrate(overLimit).fit.lastEquation.length,2000);
const badObject=base();badObject.fit=[];
assert.throws(()=>migrate(badObject),/fit must be an object/);
console.log('PASS saved curve-fit state enum, type, length, v1/v2 and immutability');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS saved curve-fit state", result.stdout)


if __name__ == "__main__":
    unittest.main()
