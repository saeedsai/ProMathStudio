"""Implicit/parametric/polar curve module: bundle parity, safety and CI registration."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SOURCE = (ROOT / "src" / "graph-curves.js").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
BUILD = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")


class GraphCurvesModuleTest(unittest.TestCase):
    def test_bundle_matches_source_once(self):
        marker = '<script id="promath-graph-curves">\n'
        self.assertEqual(HTML.count(marker), 1)
        embedded = HTML.split(marker, 1)[1].split("</script>", 1)[0]
        self.assertEqual(embedded.rstrip("\n"), SOURCE.rstrip("\n"))
        self.assertIn('("promath-graph-curves", "src/graph-curves.js")', BUILD)
        self.assertLess(HTML.index('<script id="promath-complex-graph">'), HTML.index(marker))

    def test_no_dynamic_code_or_network(self):
        for banned in ("eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket", "import(",
                       "<!--", "-->", "<script", "</script", "document.write"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, SOURCE)
        # innerHTML is assigned exactly once, from a static template with no interpolation.
        self.assertEqual(SOURCE.count("innerHTML="), 1)
        template = SOURCE.split("root.innerHTML=", 1)[1].split(";\n", 1)[0]
        self.assertNotIn("${", template)
        self.assertIsNone(re.search(r"'\+[A-Za-z_$(]", template.replace("'+\n'", "")))

    def test_uses_safe_evaluator_and_public_api(self):
        self.assertIn("M.numerical.evaluate(expr,env)", SOURCE)
        self.assertIn("M.graphCurves=api", SOURCE)
        for name in ("implicit", "parametric", "polar", "draw"):
            self.assertRegex(SOURCE, r"const api=\{[^}]*\b" + name + r"\b")
        self.assertIn("dataTables.importData(t,name)", SOURCE)

    def test_accessible_controls(self):
        for fragment in ("root.id='curves-details'", 'role="status" aria-live="polite"', 'role="img"',
                         'for="curves-type"', 'for="curves-expr"', 'for="curves-samples"', "min-height:42px",
                         "curves-error"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SOURCE)

    def test_workflow_registers_browser_smoke(self):
        self.assertIn("run: python tests/smoke_graph_curves.py", WORKFLOW)
        self.assertTrue((ROOT / "tests" / "smoke_graph_curves.py").is_file())


if __name__ == "__main__":
    unittest.main()
