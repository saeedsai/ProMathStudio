"""Saved Matrix project drafts: schema boundaries and standalone parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class MatrixProjectSchema(unittest.TestCase):
    def test_draft_dimensions_values_and_legacy_migration(self):
        script = r"""
const fs=require('fs'),assert=require('assert'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
for(const [id,path] of [['promath-project-schema','src/project-schema.js'],
                         ['promath-matrix-tools','src/matrix-tools.js']]){
 const marker='<script id="'+id+'">\n',a=html.indexOf(marker);
 assert(a>=0,'standalone module '+id);
 const start=a+marker.length,end=html.indexOf('</script>',start);
 assert.strictEqual(html.slice(start,end).trimEnd(),fs.readFileSync(path,'utf8').trimEnd());
}
const window={MathStudio:{}};vm.runInNewContext(fs.readFileSync('src/project-schema.js','utf8'),{window});
const migrate=window.MathStudio.projectSchema.migrate;
const matrix=()=>({rows:3,cols:2,bRows:2,bCols:3,
 a:['1','0','-2.5','', '3e-2','0'],b:['1','0','0','0','1','0'],
 rhs:['1','2','3'],weights:['1','1','2.5']});
const project=()=>({format:'mathstudio-project',version:2,notebook:[],matrix:matrix()});
assert.strictEqual(migrate(project()).matrix.a[4],'3e-2');
const legacy=project();delete legacy.matrix;legacy.version=1;
assert.strictEqual(migrate(legacy).version,2);
for(const change of [
 m=>m.rows=4,m=>m.cols=1,m=>m.bRows=0,m=>m.bCols='2',
 m=>m.a.pop(),m=>m.b.push('0'),m=>m.rhs=['1'],m=>m.weights=['1','2',{}],
 m=>m.a[0]='Infinity',m=>m.a[0]='0x10',m=>m.a[0]='x',
 m=>m.a[0]=1,m=>m.a[0]='1'.repeat(81)
]){
 const candidate=project();change(candidate.matrix);
 assert.throws(()=>migrate(candidate),/saved Matrix/,String(change));
}
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
