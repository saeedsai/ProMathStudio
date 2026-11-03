"""Brent pole/jump refusal: offline parity and CI registration."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BrentPoleGuardTests(unittest.TestCase):
    def test_parity_and_registration(self):
        source = (ROOT / "src/brent-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-brent-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        for phrase in ("Suspected pole near x ≈ ", "Suspected jump discontinuity near x ≈ ",
                       "No root is claimed (heuristic classification)", "10*endpointMax"):
            self.assertIn(phrase, source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_brent_pole_guard.py", workflow)


if __name__ == "__main__":
    unittest.main()
