"""Linear programming (two-phase simplex) and Nelder-Mead reference, failure and safety checks."""
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "optimization-tools.js"

NODE = r"""
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const fns={
 rosen:e=>100*(e.y-e.x**2)**2+(1-e.x)**2,
 himm:e=>(e.x**2+e.y-11)**2+(e.x+e.y**2-7)**2,
 box:e=>(e.x-3)**2+(e.y+1)**2,
 sphere3:e=>(e.x-1)**2+(e.y+2)**2+(e.z-0.5)**2,
 logx:e=>{if(e.x<=0)throw Error('domain');return e.x-Math.log(e.x)+(e.y-1)**2;},
};
const M={numerical:{evaluate:(ex,env)=>{if(!fns[ex])throw Error('Unknown expression');const v=fns[ex](env);if(!Number.isFinite(v))throw Error('nonfinite');return v;}}};
vm.runInNewContext(fs.readFileSync('src/optimization-tools.js','utf8'),{window:{MathStudio:M},document:{getElementById:()=>null}});
const same=(a,b)=>assert.equal(JSON.stringify(a),JSON.stringify(b));
const O=M.optimization,close=(a,b,t=1e-9)=>assert(Math.abs(a-b)<=t,a+' vs '+b);
assert(Object.isFrozen(O));
// Wyndor Glass (Hillier & Lieberman): x=(2,6), z=36.
let r=O.linprog('max: 3x1 + 5x2\nx1 <= 4\n2x2 <= 12\n3x1 + 2x2 <= 18');
assert.equal(r.status,'optimal');close(r.x[0],2);close(r.x[1],6);close(r.objective,36);
same(r.binding,[2,3]);close(r.constraints[0].slack,2);assert(r.maxViolation<1e-9);
// Structured input gives the same answer.
const s=O.linprog({sense:'max',c:[3,5],A:[[1,0],[0,2],[3,2]],b:[4,12,18],types:['<=','<=','<=']});
close(s.objective,36);
// Mixed >= / = / <= minimization: x=(2.5,1.5), z=9.5.
r=O.linprog('# comment line\nmin: 2x1+3*x2\nx1+x2 >= 4\nx1 - x2 = 1\nx1 <= 3  # trailing comment');
assert.equal(r.status,'optimal');close(r.x[0],2.5);close(r.x[1],1.5);close(r.objective,9.5);same(r.binding,[1,2]);
// Negative right-hand side is normalised: x1-x2>=-2 with max x2, x1<=1 -> x=(1,3), z=3.
r=O.linprog('max: x2\nx1 - x2 >= -2\nx1 <= 1');close(r.x[0],1);close(r.x[1],3);close(r.objective,3);
// Beale's cycling example terminates under Bland's rule: z*=-1/20 at x=(1/25,0,1,0).
r=O.linprog('min: -0.75x1+150x2-0.02x3+6x4\n0.25x1-60x2-0.04x3+9x4<=0\n0.5x1-90x2-0.02x3+3x4<=0\nx3<=1');
assert.equal(r.status,'optimal');close(r.objective,-0.05,1e-12);close(r.x[0],0.04,1e-12);close(r.x[2],1,1e-12);assert(r.iterations<50);
// Redundant equality is removed after phase 1.
r=O.linprog('min: x1\nx1+x2=2\n2x1+2x2=4');assert.equal(r.status,'optimal');close(r.x[1],2);assert.equal(r.removedRedundantRows,1);
// Unicode operators and degenerate vertex.
r=O.linprog('max: x1+x2\nx1 ≤ 1\nx2 ≤ 1\nx1+x2 ≤ 2');close(r.objective,2);
// Infeasible and unbounded detection.
r=O.linprog('max: x1+x2\nx1+x2 <= 1\nx1+x2 >= 3');assert.equal(r.status,'infeasible');assert.match(r.message,/Infeasible/);
r=O.linprog('max: x1+x2\nx1 - x2 <= 1');assert.equal(r.status,'unbounded');assert.match(r.message,/Unbounded/);
r=O.linprog('min: -x1\nx2 <= 3');assert.equal(r.status,'unbounded');
// 10x10 boundary works; 11 variables / constraints are rejected.
const ten=Array.from({length:10},(_,i)=>'x'+(i+1)).join('+');
r=O.linprog('max: '+ten+'\n'+Array.from({length:10},(_,i)=>'x'+(i+1)+' <= '+(i+1)).join('\n'));close(r.objective,55);
for(const [text,pattern] of [
 ['','Enter'],['3x1+5x2\nx1<=4','first line'],['max: 3x1+5x2','at least one constraint'],
 ['max: x1+x11\nx1<=1','at most 10 variables'],['max: x1\n'+Array(11).fill('x1<=1').join('\n'),'At most 10 constraints'],
 ['max: x1\nx1 < 4','strict'],['max: x1\nx1 <= 4 <= 5','exactly one'],['max: x1\nx1 <= y','single number'],
 ['max: 3x1 5x2\nx1<=1','separated'],['max: x1\nx1 <= 1e999','finite'],['max: 2^x1\nx1<=1','cannot read'],
 ['max: x0\nx0<=1','x1 to x10'],['max: x1\nx1 <= abc','single number'],['max: x1\n<= 3','linear expression']]){
 assert.throws(()=>O.linprog(text),new RegExp(pattern,'i'),text);
}
assert.throws(()=>O.linprog({sense:'max',c:[1,NaN],A:[[1,1]],b:[1],types:['<=']}),/finite/);
assert.throws(()=>O.linprog({sense:'up',c:[1],A:[[1]],b:[1],types:['<=']}),/Sense/);
// Nelder-Mead references.
let n=O.nelderMead({expression:'rosen',start:[-1.2,1]});
assert(n.converged);close(n.x[0],1,1e-5);close(n.x[1],1,1e-5);assert(n.f<1e-9);assert(n.gradient.norm<1e-3);
n=O.nelderMead({expression:'himm',start:'2.5, 2.5'});assert(n.converged);close(n.x[0],3,1e-5);close(n.x[1],2,1e-5);
n=O.nelderMead({expression:'sphere3',start:'0,0,0'});close(n.x[0],1,1e-5);close(n.x[1],-2,1e-5);close(n.x[2],0.5,1e-5);
// Optimum on the bound: x in [0,2] -> (2,-1); projected gradient ~0 while raw gradient is ~-2.
n=O.nelderMead({expression:'box',start:'1,0',lower:'0,-inf',upper:'2, inf'});
close(n.x[0],2,1e-7);close(n.x[1],-1,1e-5);assert(n.gradient.projectedNorm<1e-4);close(n.gradient.gradient[0],-2,1e-3);
same(n.gradient.activeBounds,[{variable:0,bound:'upper'}]);
// Start outside the bounds is projected.
n=O.nelderMead({expression:'box',start:[5,0],lower:[0,null],upper:[2,null]});assert(n.startProjected);close(n.x[0],2,1e-7);
// Domain errors at trial points are rejected rather than crashing: min x-ln x at x=1.
n=O.nelderMead({expression:'logx',start:'0.01,0'});close(n.x[0],1,1e-5);close(n.x[1],1,1e-5);
// Budget reported honestly.
n=O.nelderMead({expression:'rosen',start:[-1.2,1],maxEvaluations:30});assert.equal(n.converged,false);assert.match(n.status,/budget/);
for(const [o,pattern] of [
 [{expression:''},'1–1000'],[{expression:'rosen',start:'1'},'2 \\(x, y\\) or 3'],[{expression:'rosen',start:'1,2,3,4'},'2 \\(x, y\\) or 3'],
 [{expression:'rosen',start:'1,NaN'},'not a number'],[{expression:'rosen',start:[1,Infinity]},'finite'],
 [{expression:'rosen',start:'0,0',lower:'1,0',upper:'1,1'},'exceed'],[{expression:'rosen',start:'0,0',lower:'2,0',upper:'1,1'},'exceed'],
 [{expression:'rosen',start:'0,0',lower:'0'},'exactly 2'],[{expression:'rosen',start:'0,0',xTol:0},'between'],
 [{expression:'rosen',start:'0,0',maxEvaluations:5},'integer'],[{expression:'nope',start:'0,0'},'start point'],
 [{expression:'logx',start:'-1,0',lower:'-2,-inf'},'start point']]){
 assert.throws(()=>O.nelderMead(o),new RegExp(pattern),JSON.stringify(o));
}
console.log('ok');
"""


class OptimizationToolsTests(unittest.TestCase):
    def test_source_safety_and_bundle_registration(self):
        src = SOURCE.read_text(encoding="utf-8")
        for banned in ("<!--", "-->", "<script", "</script", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket"):
            self.assertNotIn(banned, src)
        self.assertNotRegex(src, r"innerHTML\s*\+?=\s*[^'\"]")
        self.assertIn("M.numerical.evaluate(expression", src)
        build = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")
        self.assertRegex(build, r'"promath-minimize-tools", "src/minimize-tools\.js"\),\n\s+\("promath-optimization-tools", "src/optimization-tools\.js"\)')
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertLess(html.index('<script id="promath-minimize-tools">'), html.index('<script id="promath-optimization-tools">'))
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_optimization_tools.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_numerical_references_and_failures(self):
        result = subprocess.run(["node", "-e", NODE], cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "ok")


if __name__ == "__main__":
    unittest.main()
