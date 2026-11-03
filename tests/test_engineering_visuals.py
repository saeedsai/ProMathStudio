"""Engineering animations module: parity, solver reuse, catalog linkage and CI registration."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringVisualsTests(unittest.TestCase):
    def test_module_parity_reuse_and_registration(self):
        source = (ROOT / "src/engineering-visuals.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-engineering-visuals">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        # Loads after the catalog it decorates.
        self.assertLess(html.index('<script id="promath-engineering-catalog">'), html.index('<script id="promath-engineering-visuals">'))
        # Reuses canonical kernels instead of adding new solvers.
        for call in ("M.odeTools.solveSystem(", "M.fftTools.fft(", "M.numerical.evaluate(",
                     "M.numerical.adaptiveSimpson(", "M.matrixTools.eigenSymmetric("):
            self.assertIn(call, source)
        self.assertNotIn("eval(", source)
        self.assertNotIn("new Function(", source)
        self.assertNotIn("innerHTML=", re.sub(r"area\.innerHTML='", "", source))
        self.assertIn("prefers-reduced-motion: reduce", source)
        self.assertIn("unavailable tool", source)
        catalog = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8")
        for tool in re.findall(r"tool:'([a-z0-9.-]+)'", source):
            self.assertIn("['" + tool + "',", catalog)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_engineering_visuals.py", workflow)


if __name__ == "__main__":
    unittest.main()
