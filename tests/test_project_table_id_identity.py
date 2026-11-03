"""Project table IDs must remain unique so selection and formulas resolve deterministically."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which("node"), "Node.js required")
class TableIdIdentityTests(unittest.TestCase):
    def test_unique_ids_legacy_compatibility_and_bundle(self):
        script = r"""
const fs=require('fs'),assert=require('assert'),vm=require('vm');
const source=fs.readFileSync('src/project-schema.js','utf8');
const html=fs.readFileSync('index.html','utf8');
const marker='<script id="promath-project-schema">\n';
const start=html.indexOf(marker);assert(start>=0);
assert.strictEqual(html.slice(start+marker.length,html.indexOf('</script>',start)).trimEnd(),source.trimEnd());
const window={MathStudio:{}};vm.runInNewContext(source,{window});
const migrate=window.MathStudio.projectSchema.migrate;
const make=(ids,version=2)=>({format:'mathstudio-project',version,notebook:[],tables:{
 selected:ids[0],tables:ids.map((id,i)=>({id,name:'Sheet'+i,columns:['A'],rows:[[i]]}))}});
for(const version of [1,2]){
 const valid=make(['sheet-1','sheet-2'],version),snapshot=JSON.stringify(valid);
 assert.strictEqual(migrate(valid).tables.selected,'sheet-1');
 assert.strictEqual(JSON.stringify(valid),snapshot,'migration must not mutate input');
 assert.throws(()=>migrate(make(['sheet-1','sheet-1'],version)),/duplicate table ids/);
 for(const bad of ['', '  ',null,42,{},'x'.repeat(121)])
  assert.throws(()=>migrate(make(['sheet-1',bad],version)),/table id is invalid/);
 const legacy=make(['sheet-1','sheet-2'],version);delete legacy.tables.tables[1].id;
 assert.strictEqual(migrate(legacy).tables.tables.length,2,'missing legacy id stays supported');
}
// Explicit selection of a nonexistent sheet must fail even in an empty workbook.
for (const version of [1,2]) {
 const empty={format:'mathstudio-project',version,notebook:[],tables:{tables:[],selected:'ghost'}};
 assert.throws(()=>migrate(empty),/selected table does not exist/);
 const nullSelection={...empty,tables:{tables:[],selected:null}};
 assert.throws(()=>migrate(nullSelection),/selected table does not exist/);
 const noSelection={...empty,tables:{tables:[]}};
 assert.strictEqual(migrate(noSelection).tables.tables.length,0);
}
// Column selectors must be unambiguous across case and whitespace variants.
for (const version of [1,2]) {
 const makeColumns = columns => ({format:'mathstudio-project',version,notebook:[],tables:{tables:[{id:'t',name:'Sheet',columns,rows:[columns.map(()=>1)]}],selected:'t'}});
 const valid=makeColumns(['A','B']); const before=JSON.stringify(valid);
 assert.strictEqual(migrate(valid).tables.tables[0].columns[1],'B');
 assert.strictEqual(JSON.stringify(valid),before);
 for(const columns of [['A',' a '],['','B'],['   ','B'],['A','A']])
  assert.throws(()=>migrate(makeColumns(columns)),/table contains invalid rows or cells/);
}
console.log('PASS unique table id validation and empty workbook selection');
"""
        result = subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__ == '__main__':
    unittest.main()
