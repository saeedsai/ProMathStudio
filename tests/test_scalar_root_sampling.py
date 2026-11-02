"""Configurable scalar-root sampling and offline standalone parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ScalarRootSamplingTests(unittest.TestCase):
    def test_sampling_controls_and_offline_parity(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-numerical-data">\n'
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("nInput('num-samples',350)", source)
        self.assertIn("Number.isInteger(samples)", source)
        self.assertIn("samples<20||samples>1600", source)
        self.assertIn("sampleSpacing:h", source)
        self.assertIn("Uniform sampling can miss oscillations", source)
        self.assertIn("result=scalarRoots(expr,v,a,b,{tolerance,samples});", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_scalar_root_sampling.py", workflow)

if __name__ == "__main__":
    unittest.main()
