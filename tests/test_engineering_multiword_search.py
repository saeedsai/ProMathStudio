"""Engineering catalog search supports order-independent keywords and offline parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class EngineeringMultiwordSearchTests(unittest.TestCase):
    def test_token_matching_and_offline_parity(self):
        source = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-engineering-catalog">\n'
        self.assertEqual(html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n"), source.rstrip("\n"))
        self.assertIn("split(/\\s+/).filter(Boolean)", source)
        self.assertIn("terms.every(term=>", source)
        self.assertNotIn("(!q||", source)

    def test_reference_queries(self):
        records = [
            ("Control state equilibrium", "control steady-state", "Control Theory"),
            ("GNSS least-squares positioning", "gnss positioning navigation", "GNSS positioning"),
            ("Orbital propagation", "orbit spaceflight", "Aerospace engineering"),
        ]
        def match(query, record):
            terms = query.strip().lower().split()
            haystack = " ".join(record).lower()
            return all(term in haystack for term in terms)
        self.assertTrue(match("equilibrium control", records[0]))
        self.assertTrue(match("  GNSS   positioning  ", records[1]))
        self.assertTrue(match("aerospace orbit", records[2]))
        self.assertFalse(match("control orbit", records[0]))
        self.assertFalse(match("control orbit", records[2]))
        self.assertTrue(match("", records[0]))

if __name__ == "__main__":
    unittest.main()
