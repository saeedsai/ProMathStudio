"""Thermodynamic cycle and DC network simulations: bundle parity, safety, catalog status and CI registration."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bundled(html, tag):
    return html.split('<script id="%s">\n' % tag, 1)[1].split("</script>", 1)[0].rstrip("\n")


class EngineeringThermoCircuitTests(unittest.TestCase):
    def test_kernels_visuals_catalog_and_workflow(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        sims = (ROOT / "src/engineering-simulations.js").read_text(encoding="utf-8").rstrip("\n")
        visuals = (ROOT / "src/engineering-visuals.js").read_text(encoding="utf-8").rstrip("\n")
        self.assertEqual(sims, bundled(html, "promath-engineering-simulations"))
        self.assertEqual(visuals, bundled(html, "promath-engineering-visuals"))
        for name in ("function thermoCycle(", "function dcNetwork(", "function parseNetlist(", "function solveDense("):
            self.assertIn(name, sims)
        self.assertIn("thermoCycle,dcNetwork,parseNetlist", sims)
        for forbidden in ("eval(", "new Function(", "document.", "fetch(", "XMLHttpRequest"):
            self.assertNotIn(forbidden, sims)
        for marker in ("<!--", "-->", "<script", "</script"):
            self.assertNotIn(marker, sims)
            self.assertNotIn(marker, visuals)
        self.assertIn("{id:'cycle',tool:'thermal.cycle.analysis'", visuals)
        self.assertIn("{id:'network',tool:'circuits.network.analysis'", visuals)
        self.assertIn("case 'cycle':", visuals)
        self.assertIn("case 'network':", visuals)
        self.assertIn("cycle:{T1:'K',P1:'kPa'", visuals)
        catalog = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8")
        for tool, disciplines in (("thermal.cycle.analysis", "'mechanical aerospace'"),
                                  ("circuits.network.analysis", "'electrical electronics'")):
            row = next(line for line in catalog.splitlines() if line.strip().startswith("['" + tool + "'"))
            self.assertTrue(row.rstrip(",]").endswith("'engineering','eng-visuals'"), tool)
            self.assertIn(disciplines, row)
            self.assertNotIn("not yet implemented", row)
        # Physics-tagged tools must not gain an accidental "ode" substring match.
        for line in catalog.splitlines():
            m = re.match(r"\s*\['([a-z0-9.-]+)','[^']*','([^']*)','([^']*)','([^']*)'", line)
            if m and "physics" in m.group(3).split() and m.group(1) != "ode.ivp.scalar":
                self.assertNotIn("ode", (m.group(1) + " " + m.group(2) + " " + m.group(4)).lower(), m.group(1))
        row = next(line for line in catalog.splitlines() if line.strip().startswith("['fluids.pipe.network'"))
        self.assertIn("not yet implemented", row)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_engineering_thermo_circuits.py", workflow)


if __name__ == "__main__":
    unittest.main()
