"""Control transient two-series graph handoff: DOM action, mapping, invalidation and bundle parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ControlTransientPlotTests(unittest.TestCase):
    def test_bundle_and_action(self):
        src = (ROOT / "src/control-equilibrium.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-control-equilibrium">\n', 1)[1].split("</script>", 1)[0]
        self.assertEqual(src.rstrip("\n"), embedded.rstrip("\n"))
        self.assertIn('id="ct-eq-transient-plot" disabled', html)
        self.assertIn("studio.graphData.clearExtra()", src)
        self.assertIn("by('dt-add-series').click()", src)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_plot_both_states_and_stale_guard(self):
        js = r"""
const fs=require('fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const nodes={},ids=['ct-equilibrium','ct-eq-size','ct-eq-matrix','ct-eq-forcing',
'ct-eq-status','ct-eq-output','ct-eq-run','ct-eq-stability-run',
'ct-eq-stability-status','ct-eq-stability-output','ct-eq-initial','ct-eq-t0',
'ct-eq-t1','ct-eq-steps','ct-eq-transient-run','ct-eq-transient-table',
'ct-eq-transient-plot','ct-eq-transient-status','ct-eq-transient-output',
'dt-graph-table','dt-chart-type','dt-graph-x','dt-graph-y','dt-plot-table','dt-add-series'];
for(const id of ids)nodes[id]={value:'',textContent:'',disabled:id.includes('transient-table')||id.includes('transient-plot'),events:{},
 addEventListener(k,fn){this.events[k]=fn;},dispatchEvent(e){this.events[e.type]?.();},
 click(){this.events.click?.();}};
Object.assign(nodes['ct-eq-size'],{value:'2'});
nodes['ct-eq-matrix'].value='2,0;0,3';nodes['ct-eq-forcing'].value='4,9';
nodes['ct-eq-initial'].value='0,0';nodes['ct-eq-t0'].value='0';
nodes['ct-eq-t1'].value='1';nodes['ct-eq-steps'].value='80';
const rows=[[0,0,0],[1,1.5,2.5]];
let imported=null,mode='',graph=null,clearCount=0;
const studio={engineeringSolvers:{},odeTools:{solveSystem:()=>({rows,steps:80})},
 dataTables:{importData(table,name){imported={table,name};return {id:'sheet-7'};}},
 advanced:{mode(next){mode=next;}},
 graphData:{clearExtra(){clearCount++;graph={points:rows.map(r=>({x:r[0],y:r[1]})),extra:[]};},
 getState(){return graph;}}};
nodes['dt-plot-table'].events.click=()=>{
 assert.equal(nodes['dt-chart-type'].value,'line');
 assert.equal(nodes['dt-graph-x'].value,'0');
 assert.equal(nodes['dt-graph-y'].value,'1');
 graph={points:rows.map(r=>({x:r[0],y:r[1]})),extra:[]};
};
nodes['dt-add-series'].events.click=()=>{
 assert.equal(nodes['dt-graph-y'].value,'2');
 graph.extra.push({mapping:{x:0,y:2},table:{headers:['t','x1','x2'],rows}});
};
vm.runInNewContext(fs.readFileSync('src/control-equilibrium.js','utf8'),
 {window:{MathStudio:studio},document:{getElementById:id=>nodes[id]},Event:class{constructor(type){this.type=type;}}});
nodes['ct-eq-transient-run'].click();
assert.equal(nodes['ct-eq-transient-plot'].disabled,false);
nodes['ct-eq-transient-plot'].click();
assert.equal(mode,'graph');assert.equal(clearCount,1);
assert.equal(imported.name,'CONTROL_TRANSIENT');
assert.equal(Array.from(imported.table.headers).join(','),'t,x1,x2');
assert.equal(imported.table.rows.length,2);
assert.equal(nodes['dt-graph-table'].value,'sheet-7');
assert.equal(graph.extra[0].mapping.y,2);
assert.match(nodes['ct-eq-transient-status'].textContent,/Plotted x1\(t\) and x2\(t\)/);
nodes['ct-eq-matrix'].value='bad';nodes['ct-eq-matrix'].events.input();
assert.equal(nodes['ct-eq-transient-plot'].disabled,true);
assert.equal(nodes['ct-eq-transient-table'].disabled,true);
nodes['ct-eq-transient-run'].click();
assert.match(nodes['ct-eq-transient-output'].textContent,/No current trajectory/);
console.log('PASS Control transient plot mapping, invalidation and offline contract');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True,
                                text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS Control transient plot", result.stdout)

if __name__ == "__main__":
    unittest.main()
