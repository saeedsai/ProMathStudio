"""Seeded random tools: PCG32 reference vectors, determinism, sampler moments, chi-square GOF, Monte Carlo/Halton, bundle parity and safety."""
import json
import math
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "random-tools.js"
STATS = ROOT / "src" / "statistics-tools.js"
MASK64 = (1 << 64) - 1
MUL = 6364136223846793005


class Pcg32:
    """Independent Python reference of PCG32 XSH-RR 64/32 (pcg32_srandom_r / pcg32_random_r)."""

    def __init__(self, seed, stream=54):
        self.state = 0
        self.inc = ((stream << 1) | 1) & MASK64
        self.next()
        self.state = (self.state + seed) & MASK64
        self.next()

    def next(self):
        old = self.state
        self.state = (old * MUL + self.inc) & MASK64
        xorshifted = (((old >> 18) ^ old) >> 27) & 0xFFFFFFFF
        rot = old >> 59
        return ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & 0xFFFFFFFF

    def float(self):
        a, b = self.next(), self.next()
        return ((a >> 5) * 67108864 + (b >> 6)) / 9007199254740992


# Integrands in Node are fixed JavaScript models (test-only); the module always calls MathStudio.numerical.evaluate.
NODE_SCRIPT = r"""
const models={'x1*x2':e=>e.x1*e.x2,'x*y':e=>e.x*e.y,'4*(x^2+y^2<1)':e=>e.x*e.x+e.y*e.y<1?4:0,'exp(x+y)':e=>Math.exp(e.x+e.y),'x1+x2+x3+x4+x5+x6':e=>e.x1+e.x2+e.x3+e.x4+e.x5+e.x6,'1/x':e=>{if(e.x===0)throw Error('division');return 1/e.x;},'q':e=>{throw Error('Unknown variable "q"');}};
global.window={MathStudio:{numerical:{evaluate:(expr,vars)=>{const f=models[expr];if(!f)throw Error('unknown model');return f(vars);}}}};
global.document={getElementById:()=>null};
require(process.argv[1]);require(process.argv[2]);
const M=window.MathStudio,R=M.random,S=M.statistics,out={};
const seq=(seed,stream,n)=>{const g=R.pcg32(seed,stream);return Array.from({length:n},()=>g.u32());};
out.ref42=seq(42,54,6);out.seed0=seq(0,54,5);out.big=seq(2**40+5,7,5);out.maxSeed=seq(Number.MAX_SAFE_INTEGER,54,3);
{const g=R.pcg32(9);out.floats=[g.float(),g.float(),g.float()];}
const det=d=>{const p={a:0,b:1,mu:0,sigma:1,lambda:3,k:2,theta:1,alpha:2,beta:3,n:20,p:0.4,weights:'1 2 3'},run=s=>R.sample({distribution:d,params:p,n:500,seed:s}).values.join();return run(7)===run(7)&&run(7)!==run(8);};
out.det=['uniform','normal','exponential','gamma','beta','poisson','binomial','discrete','permutation'].map(det);
const moments=[['uniform',{a:-2,b:3}],['normal',{mu:1,sigma:2}],['exponential',{lambda:2}],['gamma',{k:0.5,theta:2}],['gamma',{k:3,theta:1.5}],['beta',{alpha:2,beta:5}],['poisson',{lambda:4}],['poisson',{lambda:50}],['binomial',{n:10,p:0.3}],['binomial',{n:1000,p:0.6}],['discrete',{weights:'1 2 3 4'}]];
out.moments=moments.map(([d,p])=>{const r=R.sample({distribution:d,params:p,n:100000,seed:2026}),st=S.describe(r.values);return {d,p,n:r.n,mean:st.mean,variance:st.sampleVariance,tm:r.theoreticalMean,tv:r.theoreticalVariance,min:st.min,max:st.max,ints:r.values.every(Number.isInteger)};});
const pmfPois=(l,k)=>Math.exp(-l+k*Math.log(l)-S.logGamma(k+1)),pmfBin=(n,p,k)=>Math.exp(S.logGamma(n+1)-S.logGamma(k+1)-S.logGamma(n-k+1)+k*Math.log(p)+(n-k)*Math.log(1-p));
// Bin integer samples into lo..hi with both tails merged into the end bins.
const binned=(values,pmf,lo,hi)=>{const obs=new Array(hi-lo+1).fill(0);for(const x of values)obs[Math.max(0,Math.min(hi-lo,x-lo))]++;
 const p=[];for(let k=lo;k<=hi;k++)p.push(pmf(k));let below=0;for(let k=0;k<lo;k++)below+=pmf(k);p[0]+=below;p[p.length-1]=1-p.slice(0,-1).reduce((s,x)=>s+x,0);return S.chisqGof(obs,p).pValue;};
out.gofPoisson=binned(R.sample({distribution:'poisson',params:{lambda:4},n:20000,seed:11}).values,k=>pmfPois(4,k),0,11);
out.gofPtrs=binned(R.sample({distribution:'poisson',params:{lambda:30},n:20000,seed:12}).values,k=>pmfPois(30,k),15,46);
out.gofBinom=binned(R.sample({distribution:'binomial',params:{n:10,p:0.3},n:20000,seed:13}).values,k=>pmfBin(10,0.3,k),0,8);
out.gofBtrs=binned(R.sample({distribution:'binomial',params:{n:200,p:0.25},n:20000,seed:14}).values,k=>pmfBin(200,0.25,k),32,68);
{const v=R.sample({distribution:'discrete',params:{weights:[5,0,1,3,1]},n:20000,seed:15}).values,c=[0,0,0,0,0];for(const x of v)c[x]++;out.zeroWeight=c[1];out.gofAlias=S.chisqGof([c[0],c[2],c[3],c[4]],[5,1,3,1]).pValue;}
{const c=[0,0,0,0];for(let s=0;s<8000;s++)c[R.permutation(4,s)[0]-1]++;out.gofShuffle=S.chisqGof(c,[1,1,1,1]).pValue;}
{const w=R.withoutReplacement(1000,1000,3);out.worFull=new Set(w).size===1000&&Math.min(...w)===1&&Math.max(...w)===1000;const k=R.withoutReplacement(1e9,5000,4);out.worSparse=new Set(k).size===5000&&k.every(x=>Number.isInteger(x)&&x>=1&&x<=1e9);}
out.perm=[...R.permutation(10,1)].sort((a,b)=>a-b).join()==='1,2,3,4,5,6,7,8,9,10';
{const r=R.sample({distribution:'normal',n:100000,seed:1}),t=R.toTable(r);out.table={headers:t.headers,rows:t.rows.length,last:t.rows[t.rows.length-1].at(-1),first:t.rows[0][0]===String(Number(r.values[0].toPrecision(12)))};const s=R.toTable(R.sample({distribution:'uniform',n:10,seed:1}));out.small={headers:s.headers,rows:s.rows.length};}
out.halton=[R.halton(1,1),R.halton(2,1),R.halton(3,3),R.radicalInverse(11,2)];
out.mc=R.integrate({expression:'x1*x2',n:10000,seed:5});out.hal=R.integrate({expression:'x*y',n:10000,method:'halton'});
out.pi=R.integrate({expression:'4*(x^2+y^2<1)',n:100000,seed:3});
out.d6=R.integrate({expression:'x1+x2+x3+x4+x5+x6',dimension:6,lower:'0',upper:'1 2 3 4 5 6',n:20000,method:'halton-shift',seed:2});
out.conv=R.convergence({expression:'exp(x+y)',maxN:10000,seed:1});
out.trunc=R.integrate({expression:'exp(x+y)',n:1000000,budgetMs:1});
const errs={sigma:()=>R.sample({distribution:'normal',params:{mu:0,sigma:0}}),p:()=>R.sample({distribution:'binomial',params:{n:5,p:1.2}}),N:()=>R.sample({n:100001}),N0:()=>R.sample({n:0}),
 seed:()=>R.sample({seed:-1}),seedFrac:()=>R.pcg32(1.5),unif:()=>R.sample({distribution:'uniform',params:{a:1,b:1}}),w:()=>R.sample({distribution:'discrete',params:{weights:'0 0'}}),wneg:()=>R.sample({distribution:'discrete',params:{weights:'1 -1'}}),
 wor:()=>R.sample({distribution:'withoutReplacement',params:{population:10},n:11}),dist:()=>R.sample({distribution:'cauchy'}),d7:()=>R.integrate({expression:'x1*x2',dimension:7}),d0:()=>R.integrate({expression:'x1*x2',dimension:0}),
 box:()=>R.integrate({expression:'x1*x2',lower:'0 1',upper:'1 1'}),boxLen:()=>R.integrate({expression:'x1*x2',lower:'0 0 0'}),mcN:()=>R.integrate({expression:'x1*x2',n:1000001}),method:()=>R.integrate({expression:'x1*x2',method:'sobol'}),
 empty:()=>R.integrate({expression:''}),pole:()=>R.integrate({expression:'1/x',dimension:1,lower:-1,upper:1,method:'halton',n:1000}),unknown:()=>R.integrate({expression:'q'}),gammaK:()=>R.sample({distribution:'gamma',params:{k:-1,theta:1}})};
out.errors={};for(const [k,f] of Object.entries(errs)){try{f();out.errors[k]=null;}catch(e){out.errors[k]=e.message;}}
console.log(JSON.stringify(out));
"""


class RandomToolsTests(unittest.TestCase):
    def test_source_is_embedded_and_registered(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-random-tools">\n'
        self.assertEqual(html.count(marker), 1)
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)].rstrip("\n"), SOURCE.read_text(encoding="utf-8").rstrip("\n"))
        self.assertLess(html.index('<script id="promath-nonlinear-fit">'), html.index(marker))
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-nonlinear-fit", "src/nonlinear-fit.js"),\n    ("promath-random-tools", "src/random-tools.js"),', build)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_random_tools.py", workflow)

    def test_no_dynamic_code_network_or_unseeded_random(self):
        src = SOURCE.read_text(encoding="utf-8")
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"<!--", r"-->", r"<script", r"</script", r"Math\.random", r"crypto\."):
            self.assertIsNone(re.search(pattern, src, flags=re.IGNORECASE), pattern)
        self.assertEqual(src.count("innerHTML"), 1, "only the static panel template may use innerHTML")
        self.assertIn("M.numerical.evaluate(expression,env)", src)
        self.assertIn("period 2^64", src)

    def test_python_reference_generator(self):
        # Published pcg32-demo vector for pcg32_srandom(42, 54).
        g = Pcg32(42, 54)
        self.assertEqual([g.next() for _ in range(6)], [0xA15C02B7, 0x7B47F409, 0xBA1D3330, 0x83D2F293, 0xBFA4784B, 0xCBED606E])

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_node_references(self):
        r = json.loads(subprocess.run(["node", "-e", NODE_SCRIPT, str(STATS), str(SOURCE)], check=True, capture_output=True, text=True, timeout=300).stdout)

        def ref(seed, stream, n):
            g = Pcg32(seed, stream)
            return [g.next() for _ in range(n)]

        self.assertEqual(r["ref42"], [0xA15C02B7, 0x7B47F409, 0xBA1D3330, 0x83D2F293, 0xBFA4784B, 0xCBED606E])
        self.assertEqual(r["seed0"], ref(0, 54, 5))
        self.assertEqual(r["big"], ref(2**40 + 5, 7, 5))
        self.assertEqual(r["maxSeed"], ref(2**53 - 1, 54, 3))
        g = Pcg32(9)
        self.assertEqual(r["floats"], [g.float(), g.float(), g.float()])
        self.assertTrue(all(r["det"]), r["det"])
        for m in r["moments"]:
            n, var = m["n"], m["tv"]
            # Mean within 5 standard errors; variance within 6% (all distributions here have modest kurtosis).
            self.assertLess(abs(m["mean"] - m["tm"]), 5 * math.sqrt(var / n), m)
            self.assertLess(abs(m["variance"] - var) / var, 0.06, m)
            if m["d"] in ("poisson", "binomial", "discrete"):
                self.assertTrue(m["ints"], m)
            if m["d"] == "uniform":
                self.assertTrue(-2 <= m["min"] and m["max"] < 3, m)
            if m["d"] == "beta":
                self.assertTrue(0 < m["min"] and m["max"] < 1, m)
        for key in ("gofPoisson", "gofPtrs", "gofBinom", "gofBtrs", "gofAlias", "gofShuffle"):
            self.assertGreater(r[key], 0.001, (key, r[key]))
        self.assertEqual(r["zeroWeight"], 0)
        self.assertTrue(r["worFull"] and r["worSparse"] and r["perm"])
        self.assertEqual(r["table"]["headers"], ["value_%d" % i for i in range(1, 18)])
        self.assertEqual(r["table"]["rows"], 6000)
        self.assertEqual(r["table"]["last"], "")  # 100000 = 16·6000 + 4000, so the last column is padded
        self.assertTrue(r["table"]["first"])
        self.assertEqual(r["small"], {"headers": ["value"], "rows": 10})
        self.assertEqual(r["halton"][0], [0.5])
        self.assertEqual(r["halton"][1], [0.25])
        h3 = r["halton"][2]
        self.assertAlmostEqual(h3[0], 0.75, places=15)
        self.assertAlmostEqual(h3[1], 1 / 9, places=15)  # 3 = 10 in base 3
        self.assertAlmostEqual(h3[2], 0.6, places=15)
        self.assertAlmostEqual(r["halton"][3], 0.8125, places=15)  # 11 = 1011b -> 0.1101b
        mc = r["mc"]
        self.assertEqual(mc["n"], 10000)
        self.assertLess(abs(mc["estimate"] - 0.25), 3 * mc["standardError"], mc)
        self.assertAlmostEqual(mc["standardError"], math.sqrt(7 / 144 / 10000), delta=0.0003)
        self.assertIsNone(r["hal"]["standardError"])
        self.assertLess(abs(r["hal"]["estimate"] - 0.25), abs(mc["estimate"] - 0.25))
        self.assertLess(abs(r["pi"]["estimate"] - math.pi), 3 * r["pi"]["standardError"], r["pi"])
        self.assertEqual(r["d6"]["volume"], 720)
        self.assertLess(abs(r["d6"]["estimate"] - 720 * 10.5) / (720 * 10.5), 0.01, r["d6"])
        rows = r["conv"]["rows"]
        self.assertEqual([x["n"] for x in rows], [100, 1000, 10000])
        exact = (math.e - 1) ** 2
        self.assertLess(abs(rows[-1]["halton"] - exact), abs(rows[0]["halton"] - exact))
        self.assertLess(rows[-1]["standardError"], rows[0]["standardError"] / 5)
        self.assertTrue(r["trunc"]["truncated"] and r["trunc"]["n"] < 1000000, r["trunc"]["n"])
        e = r["errors"]
        self.assertTrue(all(e.values()), e)
        self.assertIn("σ must be positive", e["sigma"])
        self.assertIn("[0, 1]", e["p"])
        self.assertIn("1 to 100000", e["N"])
        self.assertIn("0 to 2^53", e["seed"])
        self.assertIn("1 to 6", e["d7"])
        self.assertIn("must exceed lower bound 2", e["box"])
        self.assertIn("1 or 2 values", e["boxLen"])
        self.assertIn("must not exceed", e["wor"])
        self.assertIn("positive sum", e["w"])
        self.assertIn("Integrand undefined at sample", e["pole"])


if __name__ == "__main__":
    unittest.main()
