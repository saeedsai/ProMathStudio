"""Graph project dataset header identity, mixed-cell migration and offline parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class GraphProjectHeaderCanonicalTests(unittest.TestCase):
    def test_bundle_parity(self):
        source=(ROOT/'src/project-schema.js').read_text(encoding='utf-8').rstrip('\n')
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        bundle=html.split('<script id="promath-project-schema">\n',1)[1].split('</script>',1)[0].rstrip('\n')
        self.assertEqual(source,bundle)
        self.assertIn('set.headers.map(h => h.trim().toLowerCase())',source)

    @unittest.skipUnless(shutil.which('node'), 'Node.js required')
    def test_v1_v2_mixed_cells_and_invalid_headers(self):
        js=r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const context={window:{MathStudio:{}}};
vm.runInNewContext(fs.readFileSync('src/project-schema.js','utf8'),context);
const migrate=context.window.MathStudio.projectSchema.migrate;
const make=(headers,version=2)=>({format:'mathstudio-project',version,notebook:[],
 graph:{dataset:{headers,rows:[[0,'alpha',true],[1,null,false]]}}});
for(const version of [1,2]){
 const valid=make([' Time ','Value','Enabled'],version);
 const original=JSON.stringify(valid);
 const out=migrate(valid);
 assert.equal(out.version,2);
 assert.equal(JSON.stringify(valid),original,'schema must not mutate input');
 assert.equal(JSON.stringify(out.graph.dataset.headers),JSON.stringify([' Time ','Value','Enabled']));
 assert.equal(JSON.stringify(out.graph.dataset.rows),JSON.stringify([[0,'alpha',true],[1,null,false]]));
 for(const headers of [
  [' Time ','time','Enabled'],['Value',' value ','Enabled'],
  [' ', 'Value','Enabled'],['Time','\t','Enabled'],['Time','','Enabled']]){
  const invalid=make(headers,version);
  assert.throws(()=>migrate(invalid),/graph dataset has (blank|duplicate) column names/);
 }
 const malformed=make(['Time','Value','Enabled'],version);
 malformed.graph.dataset.rows[0][1]={unexpected:1};
 assert.throws(()=>migrate(malformed),/invalid cells/);
}
console.log('PASS Graph dataset normalized headers, mixed cells and migration');
"""
        result=subprocess.run(['node','-e',js],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PASS Graph dataset',result.stdout)

if __name__=='__main__':
    unittest.main()
