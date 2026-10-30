"""Saved Matrix project imports reject overflowing scientific notation and values above solver bounds."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class MatrixProjectFiniteDraftTests(unittest.TestCase):
    def test_source_matches_offline_bundle(self):
        source = (ROOT / "src/project-schema.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-project-schema">\n'
        self.assertEqual(source.rstrip("\n"), html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n"))
        self.assertIn("Number.isFinite(Number(value))", source)
        self.assertIn("Math.abs(Number(value)) <= 1e12", source)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_v1_v2_boundary_and_rejected_drafts(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const context={window:{MathStudio:{}}};
vm.runInNewContext(fs.readFileSync('src/project-schema.js','utf8'),context);
const migrate=context.window.MathStudio.projectSchema.migrate;
const original=()=>({format:'mathstudio-project',version:2,notebook:[],
 matrix:{rows:2,cols:2,bRows:2,bCols:2,
 a:['1e12','-1e12','1e-8',''],b:['0','1','2','3'],
 rhs:['.5','-2.5E+3'],weights:['1','2']}});
for(const version of [1,2]){
 const data=original();data.version=version;
 const before=JSON.stringify(data);
 const migrated=migrate(data);
 assert.equal(migrated.version,2);
 assert.equal(migrated.matrix.a[0],'1e12');
 assert.equal(migrated.matrix.a[3],'');
 assert.equal(JSON.stringify(data),before,'migration must not mutate source');
}
for(const key of ['a','b','rhs','weights']){
 for(const bad of ['1e999','-1e999','1e13','-1e13','0x10','Infinity','NaN']){
  const data=original();data.matrix[key][0]=bad;
  assert.throws(()=>migrate(data),/saved Matrix .* entries are invalid/,key+': '+bad);
 }
}
const legacy=original();legacy.version=1;delete legacy.matrix;
assert.equal(migrate(legacy).version,2);
console.log('PASS Matrix project finite draft boundary, v1/v2 migration, rejection');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS Matrix project finite draft", result.stdout)

if __name__ == "__main__":
    unittest.main()
