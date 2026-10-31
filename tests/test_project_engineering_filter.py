"""Saved Engineering filter: schema validation, restore contract and bundle parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class EngineeringFilterProjectTests(unittest.TestCase):
    def test_schema_and_parity(self):
        script = r"""
const fs=require('fs'),assert=require('assert'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
for(const [tag,file] of [['promath-project-schema','src/project-schema.js'],['promath-engineering-catalog','src/engineering-catalog.js']]){
 const m='<script id="'+tag+'">\n',a=html.indexOf(m)+m.length,b=html.indexOf('</script>',a);
 assert(a>m.length);assert.strictEqual(html.slice(a,b).trimEnd(),fs.readFileSync(file,'utf8').trimEnd(),tag);
}
assert(html.includes('engineering:window.MathStudio.engineeringCatalog?.exportState()||null'));
assert(html.includes('window.MathStudio.engineeringCatalog?.restoreState(data.engineering);'));
const ctx={window:{MathStudio:{}}};vm.runInNewContext(fs.readFileSync('src/project-schema.js','utf8'),ctx);
const migrate=ctx.window.MathStudio.projectSchema.migrate;
const project=eng=>({format:'mathstudio-project',version:2,notebook:[],engineering:eng});
// Reference: valid, empty-discipline and legacy (absent/null) projects are accepted unchanged.
assert.deepStrictEqual(migrate(project({discipline:'control',query:'stability'})).engineering,{discipline:'control',query:'stability'});
assert.strictEqual(migrate(project({discipline:'',query:''})).engineering.discipline,'');
const legacy=project(undefined);delete legacy.engineering;assert.strictEqual(migrate(legacy).engineering,undefined);
assert.strictEqual(migrate(project(null)).engineering,null);
// Boundary: 200-character query accepted, 201 refused.
assert.ok(migrate(project({discipline:'',query:'x'.repeat(200)})));
assert.throws(()=>migrate(project({discipline:'',query:'x'.repeat(201)})),/Engineering filter is invalid/);
// Negative: wrong shapes and types, bad discipline syntax, v1 migration still works.
for(const bad of [[],'control',7,{discipline:'control'},{query:''},{discipline:5,query:''},{discipline:'Control!',query:''},{discipline:'control',query:{}}])
 assert.throws(()=>migrate(project(bad)),/Engineering filter is invalid/);
const v1=project({discipline:'gnss',query:'x'});v1.version=1;assert.strictEqual(migrate(v1).version,2);
console.log('PASS');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
