"""Project imports normalize table identities without modifying display names."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TableNameIdentityTests(unittest.TestCase):
    def test_offline_bundle_parity(self):
        source = (ROOT / 'src/project-schema.js').read_text(encoding='utf-8')
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        marker = '<script id="promath-project-schema">\n'
        bundled = html.split(marker, 1)[1].split('</script>', 1)[0].rstrip('\n')
        self.assertEqual(source.rstrip('\n'), bundled)
        self.assertIn("table.name.trim().toLowerCase()", source)
        self.assertIn("if (!name) fail('table name must not be blank.')", source)

    @unittest.skipUnless(shutil.which('node'), 'Node.js required')
    def test_v1_v2_names_and_atomic_validation(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const context={window:{MathStudio:{}}};
vm.runInNewContext(fs.readFileSync('src/project-schema.js','utf8'),context);
const migrate=context.window.MathStudio.projectSchema.migrate;
const base=(names,version=2)=>({format:'mathstudio-project',version,notebook:[],
 tables:{tables:names.map(name=>({name,columns:['t','value'],rows:[[0,1],[1,2]]}))}});
for(const version of [1,2]){
 const data=base([' Experiment ','Analysis'],version);
 const snapshot=JSON.stringify(data),result=migrate(data);
 assert.equal(result.version,2);
 assert.equal(result.tables.tables[0].name,' Experiment ');
 assert.equal(JSON.stringify(data),snapshot,'validation must not mutate original project');
 assert.throws(()=>migrate(base([' Experiment ','experiment'],version)),/duplicate table names/);
 assert.throws(()=>migrate(base(['Foo','  fOo  '],version)),/duplicate table names/);
 for(const invalid of ['', ' ', '\t\n']){
  assert.throws(()=>migrate(base([invalid],version)),/table name must not be blank/);
 }
 assert.equal(migrate(base(['Experiment A','Experiment B'],version)).tables.tables.length,2);
}
console.log('PASS saved Data Tables name identity and migration');
"""
        result=subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PASS saved Data Tables',result.stdout)

if __name__=='__main__':
    unittest.main()
