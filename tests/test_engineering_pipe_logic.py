"""Pipe network and digital logic simulations: bundle parity, safety, catalog status and CI registration."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bundled(html, tag):
    return html.split('<script id="%s">\n' % tag, 1)[1].split("</script>", 1)[0].rstrip("\n")


class EngineeringPipeLogicTests(unittest.TestCase):
    def test_kernels_visuals_catalog_and_workflow(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        sims = (ROOT / "src/engineering-simulations.js").read_text(encoding="utf-8").rstrip("\n")
        visuals = (ROOT / "src/engineering-visuals.js").read_text(encoding="utf-8").rstrip("\n")
        catalog = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8").rstrip("\n")
        self.assertEqual(sims, bundled(html, "promath-engineering-simulations"))
        self.assertEqual(visuals, bundled(html, "promath-engineering-visuals"))
        self.assertEqual(catalog, bundled(html, "promath-engineering-catalog"))
        for name in ("function pipeNetwork(", "function parsePipeNetlist(", "function colebrook(", "function swameeJain(",
                     "function frictionFactor(", "function digitalLogic(", "function parseLogicNetlist("):
            self.assertIn(name, sims)
        self.assertIn("pipeNetwork,parsePipeNetlist,frictionFactor,colebrook,swameeJain,digitalLogic,parseLogicNetlist", sims)
        # The pipe solver reuses the shared dense pivoted solver rather than adding another one.
        self.assertIn("solveDense(J,", sims)
        self.assertEqual(sims.count("function solveDense("), 1)
        for forbidden in ("eval(", "new Function(", "document.", "fetch(", "XMLHttpRequest", "innerHTML"):
            self.assertNotIn(forbidden, sims)
        for marker in ("<!--", "-->", "<script", "</script"):
            self.assertNotIn(marker, sims)
            self.assertNotIn(marker, visuals)
            self.assertNotIn(marker, catalog)
        self.assertIn("{id:'pipes',tool:'fluids.pipe.network'", visuals)
        self.assertIn("{id:'logic',tool:'electronics.digital.logic'", visuals)
        self.assertIn("case 'pipes':", visuals)
        self.assertIn("case 'logic':", visuals)
        self.assertIn("pipes:{density:'kg/m^3',viscosity:'Pa*s'}", visuals)
        self.assertIn("pipes:S.pipeNetwork,logic:S.digitalLogic", visuals)
        for tool, disciplines in (("fluids.pipe.network", "'fluids mechanical'"),
                                  ("electronics.digital.logic", "'electronics electrical'")):
            row = next(line for line in catalog.splitlines() if line.strip().startswith("['" + tool + "'"))
            self.assertTrue(row.rstrip(",]").endswith("'engineering','eng-visuals'"), tool)
            self.assertIn(disciplines, row)
            self.assertNotIn("not yet implemented", row)
            self.assertNotIn("physics", row)
            for word in ("orbit", "nodal"):
                self.assertNotIn(word, row.lower(), tool)
        for planned in ("gnss.positioning.least.squares", "control.frequency.response", "signals.spectral.analysis"):
            row = next(line for line in catalog.splitlines() if line.strip().startswith("['" + planned + "'"))
            self.assertIn("not yet implemented", row)
        # Physics-tagged tools must not gain an accidental "ode" substring match.
        for line in catalog.splitlines():
            m = re.match(r"\s*\['([a-z0-9.-]+)','[^']*','([^']*)','([^']*)','([^']*)'", line)
            if m and "physics" in m.group(3).split() and m.group(1) != "ode.ivp.scalar":
                self.assertNotIn("ode", (m.group(1) + " " + m.group(2) + " " + m.group(4)).lower(), m.group(1))
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_engineering_pipe_logic.py", workflow)


if __name__ == "__main__":
    unittest.main()
