"""Fixed-step scalar and coupled RK4 must reject unresolvable time grids."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RK4TimeResolutionTests(unittest.TestCase):
    def test_offline_bundle_parity(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("function rk4TimeGrid(", source)
        self.assertIn("midpoint===t||midpoint===next", source)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_scalar_and_system_reference_and_rejected_ulp_grid(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/ode-tools.js','utf8');
const kernel=source.slice(source.indexOf('function finite('),source.indexOf('const area='));
assert(kernel.includes('function rk4TimeGrid('));
const M={numerical:{evaluate:(expr,{y,z})=>{
 if(expr==='one')return 1;
 if(expr==='y')return y;
 if(expr==='z')return z;
 if(expr==='negY')return -y;
 throw Error('unexpected test expression');
}}};
const {solve,solveSystem}=new Function('M','const MAX=1e12;'+kernel+';return {solve,solveSystem};')(M);
for(const [t0,t1] of [[0,1],[1,0]]){
 const out=solve({expression:'one',t0,t1,y0:0,steps:40});
 assert(Math.abs(out.rows.at(-1)[1]-(t1-t0))<1e-12);
 assert(out.rows.every((row,i)=>i===0||Math.sign(t1-t0)*(row[0]-out.rows[i-1][0])>0));
}
const exp=solve({expression:'y',t0:0,t1:1,y0:1,steps:80});
assert(Math.abs(exp.rows.at(-1)[1]-Math.E)<1e-7);
const harmonic=solveSystem({expression:'z',expressionZ:'negY',t0:0,t1:1,y0:0,z0:1,steps:80});
assert(Math.abs(harmonic.rows.at(-1)[1]-Math.sin(1))<1e-7);
assert(Math.abs(harmonic.rows.at(-1)[2]-Math.cos(1))<1e-7);
const quantum=1/8192;
for(const [t0,t1] of [[1e12-quantum,1e12],[1e12,1e12-quantum]]){
 for(const run of [
  ()=>solve({expression:'one',t0,t1,y0:0,steps:4}),
  ()=>solveSystem({expression:'one',expressionZ:'negY',t0,t1,y0:0,z0:0,steps:4})
 ])assert.throws(run,/Fixed-step RK4 time resolution is insufficient/);
}
for(const [t0,t1] of [[1e12-1/1024,1e12],[1e12,1e12-1/1024]]){
 const scalar=solve({expression:'one',t0,t1,y0:0,steps:4});
 const coupled=solveSystem({expression:'one',expressionZ:'negY',t0,t1,y0:0,z0:0,steps:4});
 assert.equal(scalar.rows.length,5);
 assert.equal(coupled.rows.length,5);
 assert(Math.abs(scalar.rows.at(-1)[1]-(t1-t0))<1e-12);
}
console.log('PASS RK4 scalar/system time-resolution boundaries and references');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS RK4", result.stdout)


if __name__ == "__main__":
    unittest.main()
