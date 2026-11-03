"""GNSS least-squares positioning: static contract and independent numerical references (via Node)."""
import json
import math
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "gnss-tools.js"
A = 6378137.0
F = 1 / 298.257223563
E2 = F * (2 - F)
C = 299792458.0
RADIUS = 26560e3


def embedded(html, tag):
    marker = f'<script id="{tag}">\n'
    start = html.index(marker) + len(marker)
    return html[start:html.index("</script>", start)]


def llh_to_ecef(lat, lon, h):
    p, l = math.radians(lat), math.radians(lon)
    n = A / math.sqrt(1 - E2 * math.sin(p) ** 2)
    return [(n + h) * math.cos(p) * math.cos(l), (n + h) * math.cos(p) * math.sin(l), (n * (1 - E2) + h) * math.sin(p)]


def enu_axes(lat, lon):
    p, l = math.radians(lat), math.radians(lon)
    east = [-math.sin(l), math.cos(l), 0.0]
    north = [-math.sin(p) * math.cos(l), -math.sin(p) * math.sin(l), math.cos(p)]
    up = [math.cos(p) * math.cos(l), math.cos(p) * math.sin(l), math.sin(p)]
    return east, north, up


def satellites(lat, lon, h, bias_s, geometry, noise=None):
    """Independent synthesis: satellites at RADIUS along given az/el lines of sight."""
    r = llh_to_ecef(lat, lon, h)
    east, north, up = enu_axes(lat, lon)
    rows = []
    for i, (az, el) in enumerate(geometry):
        a, e = math.radians(az), math.radians(el)
        ce, cn, cu = math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), math.sin(e)
        u = [ce * east[k] + cn * north[k] + cu * up[k] for k in range(3)]
        ru = sum(r[k] * u[k] for k in range(3))
        t = -ru + math.sqrt(ru * ru - sum(x * x for x in r) + RADIUS * RADIUS)
        s = [r[k] + t * u[k] for k in range(3)]
        rho = math.dist(s, r) + C * bias_s + (noise[i] if noise else 0.0)
        rows.append({"x": s[0], "y": s[1], "z": s[2], "rho": rho})
    return r, rows


def inverse(m):
    n = len(m)
    a = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        d = a[c][c]
        a[c] = [v / d for v in a[c]]
        for r in range(n):
            if r != c:
                f = a[r][c]
                a[r] = [v - f * w for v, w in zip(a[r], a[c])]
    return [row[n:] for row in a]


def gram(rows):
    return [[sum(r[i] * r[j] for r in rows) for j in range(len(rows[0]))] for i in range(len(rows[0]))]


def run_node(script):
    harness = ("const fs=require('fs'),vm=require('vm');global.window={MathStudio:{}};"
               "global.document={getElementById:()=>({})};"
               "vm.runInThisContext(fs.readFileSync('src/gnss-tools.js','utf8'));const G=window.MathStudio.gnss;")
    out = subprocess.run(["node", "-e", harness + script], cwd=ROOT, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stdout + out.stderr)
    return json.loads(out.stdout)


GEOMETRY = [[0, 60], [90, 35], [180, 45], [270, 30], [45, 15], [225, 75], [315, 20]]


class GnssStaticTests(unittest.TestCase):
    def setUp(self):
        self.src = SOURCE.read_text(encoding="utf-8")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_registered_after_vector_calculus(self):
        build = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")
        self.assertIn('    ("promath-vector-calculus", "src/vector-calculus.js"),\n    ("promath-gnss-tools", "src/gnss-tools.js"),\n', build)
        end = self.html.index("</script>\n", self.html.index('<script id="promath-vector-calculus">')) + len("</script>\n")
        self.assertTrue(self.html.startswith('<script id="promath-gnss-tools">\n', end))
        self.assertEqual(embedded(self.html, "promath-gnss-tools").rstrip("\n"), self.src.rstrip("\n"))

    def test_safe_source(self):
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"WebSocket", r"import\s*\("):
            self.assertIsNone(re.search(pattern, self.src), pattern)
        for token in ("<!--", "-->", "<script", "</script"):
            self.assertNotIn(token, self.src.lower())
        self.assertEqual(self.src.count(".innerHTML="), 1)
        self.assertNotIn("insertAdjacentHTML", self.src)
        self.assertIn("A=6378137,F=1/298.257223563", self.src)

    def test_accessible_ui_and_honest_scope(self):
        self.assertIn("area.id='gnss-details'", self.src)
        self.assertIn("panel.append(area)", self.src)
        self.assertIn('id="gnss-output" role="status" aria-live="polite"', self.src)
        self.assertIn('id="gnss-sky" width="300" height="300" role="img" aria-label=', self.src)
        self.assertIn("M.dataTables.importData(", self.src)
        self.assertIn("min-height:40px", self.src)
        self.assertIn("Sagnac", self.src)
        self.assertIn("no ephemeris decoding", self.src)
        catalog = (ROOT / "src" / "engineering-catalog.js").read_text(encoding="utf-8")
        row = next(l for l in catalog.splitlines() if l.strip().startswith("['gnss.positioning.least.squares'"))
        self.assertIn("'editor','numerical','gnss-run']", row)
        self.assertIn("No ionosphere", row)

    def test_quality_workflow_runs_browser_smoke(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_gnss_tools.py", workflow)


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class GnssNumericalTests(unittest.TestCase):
    def solve(self, rows, extra=""):
        return run_node("const r=G.solve({observations:%s%s});console.log(JSON.stringify(r));" % (json.dumps(rows), extra))

    def fails(self, rows, extra=""):
        return run_node("try{G.solve({observations:%s%s});console.log(JSON.stringify('no error'))}catch(e){console.log(JSON.stringify(e.message))}" % (json.dumps(rows), extra))

    def test_exact_pseudoranges_recover_position_and_bias(self):
        truth, rows = satellites(59.33, 18.06, 30, 1e-4, GEOMETRY)
        r = self.solve(rows)
        self.assertLess(math.dist(r["position"], truth), 1e-4)
        self.assertAlmostEqual(r["clockBiasSeconds"], 1e-4, delta=1e-15)
        self.assertAlmostEqual(r["clockBiasMeters"], C * 1e-4, delta=1e-4)
        self.assertLess(max(abs(v) for v in r["residuals"]), 1e-5)
        self.assertTrue(r["converged"])
        self.assertLessEqual(r["iterations"], 10)
        self.assertAlmostEqual(r["geodetic"]["latitude"], 59.33, delta=1e-10)
        self.assertAlmostEqual(r["geodetic"]["longitude"], 18.06, delta=1e-10)
        self.assertAlmostEqual(r["geodetic"]["height"], 30, delta=1e-4)
        for sat, (az, el) in zip(r["satellites"], GEOMETRY):
            self.assertAlmostEqual(sat["azimuth"], az, delta=1e-8)
            self.assertAlmostEqual(sat["elevation"], el, delta=1e-8)
        # Initial guess near the truth gives the same answer; exactly four satellites also work.
        guess = self.solve(rows, ",initial:%s" % json.dumps([truth[0] + 5000, truth[1] - 3000, truth[2] + 1000]))
        self.assertLess(math.dist(guess["position"], truth), 1e-4)
        four = self.solve(rows[:4])
        self.assertLess(math.dist(four["position"], truth), 1e-4)
        self.assertIsNone(four["sigma0"])
        self.assertEqual(four["redundancy"], 0)

    def test_noisy_residuals_match_linear_projection(self):
        noise = [0.8, -1.1, 0.4, 1.5, -0.6, 0.2, -0.9]
        truth, rows = satellites(-33.9, 151.2, 50, 2e-5, GEOMETRY, noise)
        r = self.solve(rows)
        # Independent prediction: v = (I - H (H^T H)^-1 H^T) noise at the true geometry.
        H = []
        for s in rows:
            d = [truth[k] - (s["x"], s["y"], s["z"])[k] for k in range(3)]
            n = math.hypot(*d)
            H.append([d[0] / n, d[1] / n, d[2] / n, 1.0])
        Q = inverse(gram(H))
        Htn = [sum(H[i][a] * noise[i] for i in range(len(H))) for a in range(4)]
        dx = [sum(Q[a][b] * Htn[b] for b in range(4)) for a in range(4)]
        predicted = [noise[i] - sum(H[i][a] * dx[a] for a in range(4)) for i in range(len(H))]
        for got, want in zip(r["residuals"], predicted):
            self.assertAlmostEqual(got, want, delta=1e-5)
        rms = math.sqrt(sum(v * v for v in predicted) / len(predicted))
        self.assertAlmostEqual(r["residualRms"], rms, delta=1e-6)
        sigma0 = math.sqrt(sum(v * v for v in predicted) / (len(predicted) - 4))
        self.assertAlmostEqual(r["sigma0"], sigma0, delta=1e-6)
        err = [r["position"][k] - truth[k] for k in range(3)]
        for k in range(3):
            self.assertAlmostEqual(err[k], dx[k], delta=1e-4)
        self.assertAlmostEqual(r["covariance"][0][0], sigma0 ** 2 * Q[0][0], delta=1e-5 * sigma0 ** 2 * Q[0][0])  # Q at truth vs at solution
        # Weights: sigma=2 for every satellite leaves the position unchanged and scales sigma0 by 1/2.
        weighted = self.solve([dict(o, sigma=2.0) for o in rows])
        self.assertLess(math.dist(weighted["position"], r["position"]), 1e-6)
        self.assertAlmostEqual(weighted["sigma0"], sigma0 / 2, delta=1e-6)
        # Down-weighting one satellite shifts the solution (weights are actually used).
        mixed = self.solve([dict(o, sigma=(100.0 if i == 3 else 1.0)) for i, o in enumerate(rows)])
        self.assertGreater(math.dist(mixed["position"], r["position"]), 1e-3)

    def test_symmetric_geometry_dop_reference(self):
        geometry = [[0, 90], [0, 30], [90, 30], [180, 30], [270, 30]]
        truth, rows = satellites(10, -70, 100, 0, geometry)
        r = self.solve(rows)
        H = [[math.cos(math.radians(el)) * math.sin(math.radians(az)), math.cos(math.radians(el)) * math.cos(math.radians(az)),
              math.sin(math.radians(el)), 1.0] for az, el in geometry]
        Q = inverse(gram(H))
        ref = {"gdop": math.sqrt(sum(Q[i][i] for i in range(4))), "pdop": math.sqrt(Q[0][0] + Q[1][1] + Q[2][2]),
               "hdop": math.sqrt(Q[0][0] + Q[1][1]), "vdop": math.sqrt(Q[2][2]), "tdop": math.sqrt(Q[3][3])}
        # Closed form for this symmetric geometry: east/north variance 1/(2 cos^2 30°) = 2/3.
        self.assertAlmostEqual(ref["hdop"], math.sqrt(4 / 3), delta=1e-12)
        try:
            import numpy as np
            Qn = np.linalg.inv(np.array(H).T @ np.array(H))
            self.assertAlmostEqual(ref["gdop"], float(np.sqrt(np.trace(Qn))), delta=1e-12)
        except ImportError:
            pass
        for key, value in ref.items():
            self.assertAlmostEqual(r["dop"][key], value, delta=1e-9, msg=key)

    def test_geodetic_round_trip(self):
        points = [[0, 0, 0], [90, 0, 0], [-90, 45, 1000], [59.33, 18.06, 30], [-33.9, 151.2, -50],
                  [45, -120, 20000e3], [0, 180, 5], [89.9999999, 10, 100], [12.5, 270, 8848]]
        script = "const P=%s;console.log(JSON.stringify(P.map(([a,b,h])=>{const x=G.geodeticToEcef(a,b,h);return {x,g:G.ecefToGeodetic(x)};})));" % json.dumps(points)
        for (lat, lon, h), out in zip(points, run_node(script)):
            ref = llh_to_ecef(lat, lon, h)
            self.assertLess(math.dist(out["x"], ref), 1e-6)
            back = llh_to_ecef(out["g"]["latitude"], out["g"]["longitude"], out["g"]["height"])
            self.assertLess(math.dist(back, ref), 1e-6, (lat, lon, h))
            self.assertAlmostEqual(out["g"]["height"], h, delta=1e-6)
        pole = run_node("console.log(JSON.stringify(G.ecefToGeodetic(0,0,%r)))" % (A * (1 - F) + 10))
        self.assertEqual(pole["latitude"], 90)
        self.assertAlmostEqual(pole["height"], 10, delta=1e-6)
        msg = run_node("try{G.ecefToGeodetic(1,2,3);console.log('\"no\"')}catch(e){console.log(JSON.stringify(e.message))}")
        self.assertIn("Earth centre", msg)

    def test_rejections(self):
        truth, rows = satellites(59.33, 18.06, 30, 1e-4, GEOMETRY)
        self.assertIn("At least 4 satellites", self.fails(rows[:3]))
        self.assertIn("At most 16", self.fails(rows * 3))
        # Lines of sight in one plane through the receiver (east-up plane) are singular.
        _, plane = satellites(59.33, 18.06, 30, 0, [[90, 10], [90, 50], [270, 20], [270, 70], [90, 80]])
        self.assertIn("Singular satellite geometry", self.fails(plane, ",initial:%s" % json.dumps(truth)))
        # Satellites on a common elevation cone cannot separate height from clock bias.
        _, cone = satellites(59.33, 18.06, 30, 0, [[0, 30], [72, 30], [144, 30], [216, 30], [288, 30]])
        self.assertIn("Singular satellite geometry", self.fails(cone))
        self.assertIn("Did not converge", self.fails(rows, ",maxIterations:1"))
        self.assertIn("sigma for every satellite", self.fails([dict(rows[0], sigma=1)] + rows[1:]))
        self.assertIn("sigma must be positive", self.fails([dict(o, sigma=0) for o in rows]))
        self.assertIn("finite", self.fails([dict(rows[0], rho="NaN")] + rows[1:]))
        msg = run_node("try{G.parseObservations('1 2 3');console.log('\"no\"')}catch(e){console.log(JSON.stringify(e.message))}")
        self.assertIn("Line 1", msg)
        parsed = run_node("console.log(JSON.stringify(G.parseObservations('# c\\n1,2,3,4\\n\\n5 6 7 8 0.5')))")
        self.assertEqual(parsed, [{"x": 1, "y": 2, "z": 3, "rho": 4}, {"x": 5, "y": 6, "z": 7, "rho": 8, "sigma": 0.5}])


if __name__ == "__main__":
    unittest.main()
