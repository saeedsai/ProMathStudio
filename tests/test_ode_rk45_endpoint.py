"""Static regression for RK45 representable time steps and standalone bundle parity."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RK45EndpointSource(unittest.TestCase):
    def test_source_bundle_and_time_precision_guards(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-ode-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        adaptive = source.split("function solveAdaptive(", 1)[1].split("function solveSystem(", 1)[0]
        self.assertIn("const quantum=timeResolution(t,direction)", adaptive)
        self.assertIn("h=nextT-t", adaptive)
        self.assertIn("t=nextT", adaptive)
        self.assertIn("if(Math.abs(h)<=quantum)throw Error", adaptive)
        self.assertNotIn("Math.abs(t1-t)<=Math.max(", adaptive)

    def test_node_syntax(self):
        result = subprocess.run(["node", "--check", str(ROOT / "src/ode-tools.js")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
