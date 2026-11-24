"""Unit-aware Engineering simulation inputs: source parity, safe parsing and CI registration."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringSimUnitsTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "src/engineering-visuals.js").read_text(encoding="utf-8")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_bundle_parity_and_load_order(self):
        bundled = self.html.split('<script id="promath-engineering-visuals">\n', 1)[1].split("</script>", 1)[0]
        self.assertEqual(self.source.rstrip("\n"), bundled.rstrip("\n"))
        self.assertLess(self.html.index('<script id="promath-units-tools">'),
                        self.html.index('<script id="promath-engineering-visuals">'))

    def test_reuses_shared_units_module_at_call_time(self):
        self.assertIn("U=M.units", self.source)
        self.assertIn("U.convert(", self.source)
        self.assertIn("U.dimensions(", self.source)
        # No duplicated conversion tables, no dynamic evaluation.
        self.assertNotIn("0.3048", self.source)
        self.assertNotIn("4.4482216152605", self.source)
        self.assertIsNone(re.search(r"\beval\(|new Function", self.source))

    def test_expected_units_declared_for_simulation_fields(self):
        for frag in ("length:'m'", "modulus:'GPa'", "height:'mm'", "inductance:'mH'", "capacitance:'µF'",
                     "initial:'°C'", "altitude:'km'", "density:'kg/m^3'", "'kN/m':'kN'"):
            self.assertIn(frag, self.source)

    def test_ci_registers_smoke_last(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8").rstrip()
        self.assertIn("run: python tests/smoke_engineering_sim_units.py", workflow)


if __name__ == "__main__":
    unittest.main()
