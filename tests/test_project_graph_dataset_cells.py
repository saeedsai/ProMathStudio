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

const overlay=()=>({name:'OVERLAY',table:{headers:['t','w'],rows:[['0','2'],['1','4']]},
 mapping:{x:0,y:1,z:1,mode:'2d',style:'line'}});
const withOverlay=()=>{const data=basic();data.graph.dataset.extra=[overlay()];return data;};
const valid2d=withOverlay(),validSnapshot=JSON.stringify(valid2d);
assert.strictEqual(migrate(valid2d).graph.dataset.extra.length,1);
assert.strictEqual(JSON.stringify(valid2d),validSnapshot,'overlay validation must not mutate input');
const valid3d=withOverlay();
valid3d.graph.dataset.extra[0].table.headers.push('z');
valid3d.graph.dataset.extra[0].table.rows.forEach(row=>row.push('3'));
valid3d.graph.dataset.extra[0].mapping={x:0,y:1,z:2,mode:'3d',style:'grid'};
assert.strictEqual(migrate(valid3d).graph.dataset.extra.length,1);
const invalidOverlay=(mutate,pattern)=>{const data=withOverlay();mutate(data.graph.dataset);assert.throws(()=>migrate(data),pattern);};
invalidOverlay(set=>set.extra={},/graph dataset overlays/);
invalidOverlay(set=>set.extra=Array.from({length:21},overlay),/graph dataset overlays/);
invalidOverlay(set=>set.extra[0]={table:overlay().table},/graph dataset overlay is invalid/);
invalidOverlay(set=>set.extra[0].table.headers=['t'],/graph dataset overlay dimensions/);
invalidOverlay(set=>set.extra[0].table.rows[0][1]={bad:true},/graph dataset overlay has invalid cells/);
invalidOverlay(set=>set.extra[0].mapping.x=2,/graph dataset overlay mapping/);
invalidOverlay(set=>set.extra[0].mapping.x=1,/graph dataset overlay mapping/);
invalidOverlay(set=>set.extra[0].mapping.mode='4d',/graph dataset overlay mapping/);
invalidOverlay(set=>{
 set.extra[0].table.headers.push('z');
 set.extra[0].table.rows.forEach(row=>row.push('3'));
 set.extra[0].mapping.mode='3d';set.extra[0].mapping.z=1;
},/graph dataset overlay mapping/);
invalidOverlay(set=>set.extra[0].mapping.style='bad',/graph dataset overlay mapping/);
invalidOverlay(set=>set.extra[0].table.rows=[['a','b']],/graph dataset overlay has no numeric points/);
const legacyOverlay=withOverlay();legacyOverlay.version=1;
assert.strictEqual(migrate(legacyOverlay).version,2,'legacy v1 graph overlays remain supported');
const noExtra=basic();noExtra.graph.dataset.extra=null;
assert.strictEqual(migrate(noExtra).graph.dataset.extra,null,'null legacy overlay list remains tolerated');

const mapped3d=()=>{const data=basic();data.graph={mode:'3d',dataset:{
 headers:['time','value','height'],rows:[[0,1,2],[1,2,3]],x:'0',y:'1',z:'2',style:'line'}};return data;};
const validMapped=mapped3d(),mappedSnapshot=JSON.stringify(validMapped);
assert.strictEqual(migrate(validMapped).graph.dataset.x,'0');
assert.strictEqual(migrate(validMapped).graph.dataset.style,'line');
assert.strictEqual(JSON.stringify(validMapped),mappedSnapshot,'primary mapping validation must not mutate input');
const invalidPrimary=(mutate,pattern)=>{const data=mapped3d();mutate(data.graph);assert.throws(()=>migrate(data),pattern);};
invalidPrimary(graph=>graph.mode='4d',/graph mode is invalid/);
invalidPrimary(graph=>graph.dataset.x='3',/graph dataset mapping is invalid/);
invalidPrimary(graph=>graph.dataset.y='not-a-column',/graph dataset mapping is invalid/);
invalidPrimary(graph=>graph.dataset.z=-1,/graph dataset mapping is invalid/);
invalidPrimary(graph=>graph.dataset.x='1',/graph dataset mapping is invalid/);
invalidPrimary(graph=>graph.dataset.z='1',/graph dataset mapping is invalid/);
invalidPrimary(graph=>graph.dataset.style='dots',/graph dataset style is invalid/);
const legacyMapping=basic();delete legacyMapping.graph.dataset.x;delete legacyMapping.graph.dataset.y;
delete legacyMapping.graph.dataset.z;delete legacyMapping.graph.dataset.style;
assert.strictEqual(migrate(legacyMapping).version,2,'legacy datasets without selectors remain supported');
const valid2d=mapped3d();valid2d.graph.mode='2d';valid2d.graph.dataset.z='1';
assert.strictEqual(migrate(valid2d).graph.dataset.z,'1','2D may retain a dormant Z selector');
const invalid3dDefaults=basic();invalid3dDefaults.graph.mode='3d';
assert.throws(()=>migrate(invalid3dDefaults),/graph dataset mapping is invalid/);
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT,
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
