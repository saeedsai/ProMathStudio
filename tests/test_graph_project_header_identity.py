"""Project graph dataset headers must be unique and preserve source/bundle parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"),"Node.js required")
class GraphHeaderIdentity(unittest.TestCase):
    def test_duplicate_headers_and_legacy_migration(self):
        js=r"""
const fs=require('fs'),assert=require('assert'),vm=require('vm');
const source=fs.readFileSync('src/project-schema.js','utf8');
const html=fs.readFileSync('index.html','utf8');
const marker='<script id="promath-project-schema">\n';
const a=html.indexOf(marker);assert(a>=0);
const b=a+marker.length;
assert.equal(html.slice(b,html.indexOf('</script>',b)).trimEnd(),source.trimEnd());
const window={MathStudio:{}};vm.runInNewContext(source,{window});
const migrate=window.MathStudio.projectSchema.migrate;
const sample=(version=2)=>({format:'mathstudio-project',version,notebook:[],
 graph:{dataset:{headers:['Time','Value'],rows:[[0,2],[1,3]]}}});
for(const version of [1,2]){
 const valid=sample(version),out=migrate(valid);
 assert.equal(out.version,2);
 assert.deepEqual([...out.graph.dataset.headers],['Time','Value']);
 assert.deepEqual(out.graph.dataset.rows[1],[1,3]);
 for(const duplicate of [['Time','Time'],['Value','Value']]){
  const invalid=sample(version);invalid.graph.dataset.headers=duplicate;
  assert.throws(()=>migrate(invalid),/duplicate column names/);
 }
}
const nonstring=sample();nonstring.graph.dataset.headers=['Time',null];
assert.throws(()=>migrate(nonstring),/invalid cells/);
"""
        result=subprocess.run(["node","-e",js],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__=="__main__":
    unittest.main()
