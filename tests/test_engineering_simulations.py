"""Engineering simulation kernels: parity, load order, stated assumptions, catalog status and CI."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringSimulationTests(unittest.TestCase):
    def test_kernel_parity_assumptions_and_registration(self):
        source = (ROOT / "src/engineering-simulations.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-engineering-simulations">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        order = [html.index('<script id="%s">' % tag) for tag in
                 ("promath-numerical-data", "promath-ode-tools", "promath-engineering-simulations",
                  "promath-engineering-catalog", "promath-engineering-visuals")]
        self.assertEqual(order, sorted(order))
        self.assertNotIn("document.", source, "kernels must stay DOM-free")
        self.assertNotIn("eval(", source)
        self.assertNotIn("new Function(", source)
        self.assertEqual(source.count("assumptions:'"), 11, "every simulation states its model assumptions")
        self.assertIn("M.odeTools.solveSystem(", source)
        self.assertIn("M.numerical.heat1D(", source)
        catalog = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8")
        for tool in ("structures.beam.deflection", "aerospace.orbit.propagation", "circuits.rlc.series.transient",
                     "mechanics.projectile.drag", "thermal.conduction.rod", "thermal.cycle.analysis",
                     "circuits.network.analysis", "fluids.pipe.network", "electronics.digital.logic"):
            row = next(line for line in catalog.splitlines() if line.strip().startswith("['" + tool + "'"))
            self.assertTrue(row.rstrip(",]").endswith("'engineering','eng-visuals'"), tool)
        for planned in ("gnss.positioning.least.squares", "control.frequency.response", "signals.spectral.analysis"):
            row = next(line for line in catalog.splitlines() if line.strip().startswith("['" + planned + "'"))
            self.assertIn("not yet implemented", row)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_engineering_simulations.py", workflow)


if __name__ == "__main__":
    unittest.main()
