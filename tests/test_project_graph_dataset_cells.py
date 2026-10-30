"""Graph dataset import must reject nested objects and nonfinite numeric cells."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class GraphDatasetProjectValidation(unittest.TestCase):
    def test_import_cell_types_and_standalone_parity(self):
        script = r"""
const fs=require('fs'),assert=require('assert'),vm=require('vm');
const source=fs.readFileSync('src/project-schema.js','utf8');
const html=fs.readFileSync('index.html','utf8');
const marker='<script id="promath-project-schema">\n';
const start=html.indexOf(marker);
assert(start>=0,'standalone project module present');
const end=html.indexOf('</script>',start+marker.length);
assert.strictEqual(html.slice(start+marker.length,end).trimEnd(),source.trimEnd());
const context={window:{MathStudio:{}}};vm.runInNewContext(source,context);
const migrate=context.window.MathStudio.projectSchema.migrate;
const basic=()=>({format:'mathstudio-project',version:2,notebook:[],
  graph:{dataset:{headers:['time','value'],rows:[[0,1],[1,2]]}}});
assert.strictEqual(migrate(basic()).graph.dataset.rows.length,2);
for(const cell of [{x:1},[1,2],[],{},()=>0,Symbol('cell'),Infinity,-Infinity,NaN]){
 const data=basic();data.graph.dataset.rows[0][1]=cell;
 assert.throws(()=>migrate(data),/graph dataset has invalid cells/);
}
for(const cell of [null,true,false,'1',3.25,0]){
 const data=basic();data.graph.dataset.rows[0][1]=cell;
 assert.strictEqual(migrate(data).graph.dataset.rows[0][1],cell);
}
const v1=basic();v1.version=1;assert.strictEqual(migrate(v1).version,2);
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT,
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
