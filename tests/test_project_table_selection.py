"""Saved Data Tables selection must reference an existing table; cell types and column order survive migration."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class TableSelectionProjectValidation(unittest.TestCase):
    def test_selection_order_cells_and_standalone_parity(self):
        script = r"""
const fs=require('fs'),assert=require('assert'),vm=require('vm');
const source=fs.readFileSync('src/project-schema.js','utf8');
const html=fs.readFileSync('index.html','utf8');
const marker='<script id="promath-project-schema">\n';
const start=html.indexOf(marker),end=html.indexOf('</script>',start+marker.length);
assert(start>=0);
assert.strictEqual(html.slice(start+marker.length,end).trimEnd(),source.trimEnd());
const context={window:{MathStudio:{}}};vm.runInNewContext(source,context);
const migrate=context.window.MathStudio.projectSchema.migrate;
const project=(selected,version=2)=>({format:'mathstudio-project',version,notebook:[],
 tables:{version:1,selected,tables:[
  {id:'sheet-1',name:'Alpha',columns:['z','a','m'],rows:[['1',2,true],[null,'x',0]]},
  {id:'sheet-2',name:'Beta',columns:['B'],rows:[['=Alpha!A1']]}]}});
// Reference: valid selection, original column order and mixed primitives are preserved exactly.
const ok=migrate(project('sheet-2'));
assert.strictEqual(ok.tables.selected,'sheet-2');
assert.deepStrictEqual(ok.tables.tables[0].columns,['z','a','m']);
assert.deepStrictEqual(ok.tables.tables[0].rows,[['1',2,true],[null,'x',0]]);
// Legacy v1 with a valid selection migrates; absent selection stays allowed.
assert.strictEqual(migrate(project('sheet-1',1)).version,2);
const absent=project('sheet-1');delete absent.tables.selected;
assert.strictEqual(migrate(absent).tables.tables.length,2);
// Negative: unknown id, wrong types.
for(const bad of ['sheet-9','',null,7,{id:'sheet-1'},['sheet-1']])
 assert.throws(()=>migrate(project(bad)),/selected table does not exist/);
// Boundary: empty table list has nothing to select and remains accepted.
const empty=project('sheet-1');empty.tables.tables=[];
assert.strictEqual(migrate(empty).tables.tables.length,0);
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
