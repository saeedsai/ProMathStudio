"""Scalar-root pole/jump/oscillation metadata, offline parity and CI registration."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarRootDiscontinuityTests(unittest.TestCase):
    def test_metadata_parity_and_registration(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-numerical-data">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        for phrase in ("rejectedLimit=20", "recordRejected(root,", "'possible-pole':'possible-jump'",
                       "denseOscillationIntervals++", "'under-resolved-oscillation'",
                       "Rejected sign changes (possible pole/jump): ",
                       "Under-resolved oscillation intervals: ", "heuristic classification"):
            self.assertIn(phrase, source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_scalar_root_discontinuity.py", workflow)


if __name__ == "__main__":
    unittest.main()
