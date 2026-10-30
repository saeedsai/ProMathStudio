"""RK45 output timestamps must advance strictly and expose machine-resolution steps."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class RK45MonotonicTimeTests(unittest.TestCase):
    def test_standalone_source_parity(self):
        src=(ROOT/'src/ode-tools.js').read_text(encoding='utf-8').rstrip('\n')
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        inline=html.split('<script id="promath-ode-tools">\n',1)[1].split('</script>',1)[0].rstrip('\n')
        self.assertEqual(src,inline)
        self.assertIn("direction*(nextT-t)>0",src)
        self.assertIn("quantumLimitedAcceptedSteps",src)

    @unittest.skipUnless(shutil.which('node'), 'Node.js required')
    def test_forward_backward_ulp_monotonic_and_smooth_reference(self):
        script=r"""
const fs=require('fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const kernel=src.slice(src.indexOf('function finite('),src.indexOf('function solveSystem('));
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:(e,{y})=>e==="one"?1:e==="y"?y:NaN}};'+kernel+';return solveAdaptive;')();
const quantum=1/8192;
for(const [a,b,delta] of [[1e12-quantum,1e12,quantum],[1e12,1e12-quantum,-quantum]]){
 const out=solve({expression:'one',t0:a,t1:b,y0:0});
 assert.equal(out.rows.at(-1)[0],b);
 assert(Math.abs(out.rows.at(-1)[1]-delta)<1e-12);
 assert(out.quantumLimitedAcceptedSteps>=1);
 assert(out.quantumLimitedAcceptedSteps<=out.steps);
 assert.equal(out.rows.length,out.steps+1);
 const direction=Math.sign(b-a);
 for(let j=1;j<out.rows.length;j++)assert(direction*(out.rows[j][0]-out.rows[j-1][0])>0);
}
for(const [a,b,y0,expected] of [[0,1,1,Math.E],[1,0,Math.E,1]]){
 const out=solve({expression:'y',t0:a,t1:b,y0,tolerance:1e-10});
 assert(Math.abs(out.rows.at(-1)[1]-expected)<1e-8);
 assert.equal(out.quantumLimitedAcceptedSteps,0);
 for(let j=1;j<out.rows.length;j++)assert(Math.sign(b-a)*(out.rows[j][0]-out.rows[j-1][0])>0);
}
assert.throws(()=>solve({expression:'one',t0:1,t1:1}),/End time/);
console.log('PASS RK45 forward/backward strict time grid and near-ULP warnings');
"""
        completed=subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=25)
        self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
        self.assertIn('PASS RK45',completed.stdout)

if __name__=='__main__':
    unittest.main()
