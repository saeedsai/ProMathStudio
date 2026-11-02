"""Cusp root screening metadata, offline parity and CI registration."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarRootCuspTests(unittest.TestCase):
    def test_cusp_metadata_and_standalone_parity(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-numerical-data">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        for phrase in ("localSlopeWarnings:[]", "const localSlopeWarnings=[];",
                       "warning='possible-cusp'", "localSlopeWarnings.push(warning);",
                       "Math.abs(halfLeft)>=0.7*Math.abs(left)",
                       "Possible non-smooth cusp roots (heuristic):",
                       "not a mathematical certificate"):
            self.assertIn(phrase, source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_scalar_root_cusps.py", workflow)


if __name__ == "__main__":
    unittest.main()
