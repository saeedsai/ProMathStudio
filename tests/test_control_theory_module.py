"""Control Theory controller extracted to src/control-theory.js: declared, embedded exactly, safe."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ControlTheoryModuleTests(unittest.TestCase):
    def test_extracted_module_parity(self):
        source = (ROOT / "src/control-theory.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('<script id="promath-control-theory">\n'), 1)
        bundled = html.split('<script id="promath-control-theory">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn('("promath-control-theory", "src/control-theory.js")',
                      (ROOT / "scripts/build.py").read_text(encoding="utf-8"))
        self.assertNotIn("eval(", source)
        self.assertNotIn("new Function(", source)
        # Existing Control Theory browser regressions remain registered.
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        for smoke in ("smoke_control_theory.py", "smoke_control_a11y.py", "smoke_control_equilibrium.py"):
            self.assertIn("python tests/" + smoke, workflow)


if __name__ == "__main__":
    unittest.main()
