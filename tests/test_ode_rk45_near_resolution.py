"""RK45 near time resolution: original-time vs rescaled-time references, forward and backward."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class RK45NearResolutionTests(unittest.TestCase):
    def test_original_vs_rescaled_time(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin);
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:(e,{t,y})=>y}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
const tol=1e-10;
// y'=y is autonomous: the exact answer depends only on the realised span S=|t1-t0|,
// so original large-offset time and rescaled time must agree with exp(+-S).
for(const [T0,span] of [[0,1],[1e6,1],[1e9,1],[1e11,1e-3],[1e11,1e-4],[1e9,1e-6]]){
 for(const dir of [1,-1]){
  const a=dir>0?T0:T0+span,b=dir>0?T0+span:T0,S=Math.abs(b-a);
  const y0=dir>0?1:Math.exp(S),ref=dir>0?Math.exp(S):1;
  const big=solve({expression:'y',t0:a,t1:b,y0,tolerance:tol,maxSteps:10000});
  const small=solve({expression:'y',t0:dir>0?0:S,t1:dir>0?S:0,y0,tolerance:tol,maxSteps:10000});
  const scaleBound=tol*(1+Math.abs(ref))*Math.max(1,big.steps);
  assert(Math.abs(big.rows.at(-1)[1]-ref)<=Math.max(scaleBound,1e-9),'original-time error '+T0+','+span+','+dir);
  assert(Math.abs(small.rows.at(-1)[1]-ref)<=Math.max(scaleBound,1e-9),'rescaled error');
  assert.strictEqual(big.rows.at(-1)[0],b);            // lands exactly on the requested end time
  assert.strictEqual(big.attempts,big.steps+big.rejected);
  // Direction is monotone in time.
  for(let i=1;i<big.rows.length;i++)assert(dir*(big.rows[i][0]-big.rows[i-1][0])>0);
  if(T0>=1e9&&span<=1e-4){            // span near float time resolution: warn, never certify
   assert(big.stageTimeCollisionAttempts>0,'collapsed stage times must be counted');
   assert.strictEqual(small.stageTimeCollisionAttempts,0);
  }
 }
}
// Failure path: an interval below time resolution is refused rather than returning a false answer.
assert.throws(()=>solve({expression:'y',t0:1e11,t1:1e11+1e-9,y0:1}),/./);
console.log('PASS RK45 near-resolution original vs rescaled');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS RK45 near-resolution", result.stdout)


    def test_subnormal_spans_use_one_representable_step_with_warning(self):
        script = r"""
const fs=require('fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin);
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:(e,{y})=>e==="one"?1:e==="y"?y:NaN}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
for(const [t0,t1,quantumSteps] of [
 [0,Number.MIN_VALUE,1],[Number.MIN_VALUE,0,1],
 [0,2*Number.MIN_VALUE,0],[2*Number.MIN_VALUE,0,0]
]){
 const out=solve({expression:'one',t0,t1,y0:0});
 assert.equal(out.rows.length,2);
 assert.equal(out.rows[0][0],t0);
 assert.equal(out.rows[1][0],t1);
 assert.equal(out.rows[1][1],t1-t0);
 assert.equal(out.steps,1);
 assert.equal(out.attempts,1);
 assert.equal(out.rejected,0);
 assert.equal(out.attempts,out.steps+out.rejected);
 assert.equal(out.stageTimeCollisionAttempts,1);
 assert.equal(out.stageTimeCollisionAcceptedSteps,1);
 assert.equal(out.quantumLimitedAcceptedSteps,quantumSteps);
 assert(Math.sign(t1-t0)*(out.rows[1][0]-out.rows[0][0])>0);
}
const state=solve({expression:'y',t0:0,t1:Number.MIN_VALUE,y0:1});
assert.equal(state.rows.at(-1)[1],1);
assert.equal(state.stageTimeCollisionAcceptedSteps,1);
console.log('PASS RK45 subnormal initial-step fallback, endpoints and collision warnings');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=25)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS RK45 subnormal", result.stdout)



    def test_repeated_fractional_stage_times_are_reported(self):
        script = r"""
const fs=require('fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin);
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:(e,{y})=>e==="one"?1:y}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
const ulp=1/8192,endpoint=1e12;
for(const direction of [1,-1]){
 const t0=direction>0?endpoint-20*ulp:endpoint;
 const t1=direction>0?endpoint:endpoint-20*ulp;
 const secondStart=t0+direction*ulp,secondH=direction*5*ulp;
 assert.equal(secondStart+4*secondH/5,secondStart+8*secondH/9);
 const out=solve({expression:'one',t0,t1,y0:0});
 assert.equal(out.rows[0][0],t0);
 assert.equal(out.rows.at(-1)[0],t1);
 assert.equal(out.attempts,3);
 assert.equal(out.steps,3);
 assert.equal(out.rejected,0);
 assert.equal(out.stageTimeCollisionAttempts,2);
 assert.equal(out.stageTimeCollisionAcceptedSteps,2);
 assert.equal(out.quantumLimitedAcceptedSteps,1);
 for(let i=1;i<out.rows.length;i++)
  assert(direction*(out.rows[i][0]-out.rows[i-1][0])>0);
}
console.log('PASS RK45 repeated fractional stage-time collisions');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=25)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS RK45 repeated fractional", result.stdout)


if __name__ == "__main__":
    unittest.main()
