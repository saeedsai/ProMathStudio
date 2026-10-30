"""Project table import validates finite numbers and preserves valid table values."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js is required")
class TableImportFiniteNumbers(unittest.TestCase):
    def test_table_cell_types_migration_and_standalone_parity(self):
        script = r"""
const fs=require('fs'),assert=require('assert'),vm=require('vm');
const source=fs.readFileSync('src/project-schema.js','utf8');
const html=fs.readFileSync('index.html','utf8');
const marker='<script id="promath-project-schema">\n';
const a=html.indexOf(marker);assert(a>=0);
const start=a+marker.length,end=html.indexOf('</script>',start);
assert.strictEqual(html.slice(start,end).trimEnd(),source.trimEnd());
const window={MathStudio:{}};vm.runInNewContext(source,{window});
const migrate=window.MathStudio.projectSchema.migrate;
const basic=()=>({format:'mathstudio-project',version:2,notebook:[],tables:{
 selected:'sheet-1',tables:[{id:'sheet-1',name:'Data1',columns:['A','B'],rows:[[1,2]]}]}});
for(const cell of [NaN,Infinity,-Infinity,[],{},[1],{value:2},()=>0]){
 const input=basic();input.tables.tables[0].rows[0][1]=cell;
 assert.throws(()=>migrate(input),/table contains invalid rows or cells/);
}
for(const cell of [null,true,false,'3.5',0,1e-300,-1e12]){
 const input=basic();input.tables.tables[0].rows[0][1]=cell;
 assert.strictEqual(migrate(input).tables.tables[0].rows[0][1],cell);
}
const legacy=basic();legacy.version=1;
assert.strictEqual(migrate(legacy).version,2);
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
