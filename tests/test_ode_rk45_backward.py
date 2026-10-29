"""Backward adaptive RK45 source/bundle consistency and syntax regression."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BackwardAdaptiveRK45(unittest.TestCase):
    def test_bundle_parity_and_signed_step_guard(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, embedded)
        adaptive = source.split("function solveAdaptive(", 1)[1].split(
            "function solveSystem(", 1)[0]
        self.assertIn("direction=Math.sign(span)", adaptive)
        self.assertIn("while(direction*(t1-t)>0)", adaptive)
        self.assertIn("h=direction*Math.min(Math.abs(h),Math.abs(remaining))", adaptive)
        self.assertIn("const remaining=t1-t", adaptive)
        self.assertIn("const quantum=timeResolution(t,direction)", adaptive)
        self.assertIn("h=nextT-t", adaptive)
        self.assertIn("if(Math.abs(h)<=quantum)throw Error", adaptive)
        self.assertIn("if(t1===t0)throw Error", adaptive)
        self.assertIn("forward or backward", adaptive)

    def test_node_syntax(self):
        result = subprocess.run(
            ["node", "--check", str(ROOT / "src/ode-tools.js")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
