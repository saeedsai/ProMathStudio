"""RK45 stage overflow is recoverable only for explicitly tagged numeric bounds."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class RK45OverflowClassificationTests(unittest.TestCase):
    def test_offline_parity_and_explicit_error_tags(self):
        source=(ROOT/'src/ode-tools.js').read_text(encoding='utf-8')
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        marker='<script id="promath-ode-tools">\n'
        embedded=html.split(marker,1)[1].split('</script>',1)[0]
        self.assertEqual(source,embedded)
        self.assertIn("error.code=label==='Derivative'&&!Number.isFinite(value)?'RK45_DOMAIN_NONFINITE':'RK45_STAGE_BOUND'",source)
        self.assertIn("error?.code!=='RK45_STAGE_BOUND'",source)
        self.assertIn("lastOverflowStage",source)

    @unittest.skipUnless(shutil.which('node'),'Node.js required')
    def test_recoverable_and_nonrecoverable_cases(self):
        js=r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const body=src.slice(src.indexOf('function finite('),src.indexOf('function solveSystem('));
const evaluate=(expr,{t,y})=>{
 if(expr==='finite_guard')return y>10?1e13:-1000*y;
 if(expr==='reverse_guard')return y>10?1e13:1000*y;
 if(expr==='nonfinite_stage')return t>0?Infinity:1;
 if(expr==='spoof'){if(t>0)throw Error('became non-finite or exceeded magnitude 1e12');return 1;}
 if(expr==='initial_overflow')return 1e13;
 return 1;
};
const solve=new Function('evaluate','const MAX=1e12;const M={numerical:{evaluate}};'+body+';return solveAdaptive;')(evaluate);
for(const opts of [
 {expression:'finite_guard',t0:0,t1:1,y0:1,maxSteps:5000},
 {expression:'reverse_guard',t0:1,t1:0,y0:1,maxSteps:5000}
]){
 const result=solve(opts);
 assert(result.stageOverflowRejected>0);
 assert.equal(result.attempts,result.steps+result.rejected);
 assert.match(result.lastOverflowStage,/^k[2-7]$|^y[45]$/);
 assert.equal(result.rows.at(-1)[0],opts.t1);
 assert(Math.abs(result.rows.at(-1)[1])<1e-6);
}
for(const expr of ['nonfinite_stage','spoof','initial_overflow']){
 assert.throws(()=>solve({expression:expr,t0:0,t1:1,y0:1}),/RK45 k[12] derivative failed/);
}
assert.throws(()=>solve({expression:'finite_guard',t0:0,t1:1,y0:1,maxSteps:4}),
 /attempts=4\/4.*bounded stage-overflow retries=4.*last bounded stage=/);
const smooth=solve({expression:'smooth',t0:0,t1:1,y0:0});
assert.equal(smooth.stageOverflowRejected,0);
assert.equal(smooth.lastOverflowStage,null);
assert(Math.abs(smooth.rows.at(-1)[1]-1)<1e-12);
console.log('PASS structured RK45 overflow classification, budget, forward/backward');
"""
        result=subprocess.run(['node','-e',js],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PASS structured RK45',result.stdout)

if __name__=='__main__':
    unittest.main()
