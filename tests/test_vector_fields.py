"""Vector field / streamline / slope field module: bundle parity, safety and CI registration."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SOURCE = (ROOT / "src" / "vector-fields.js").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
BUILD = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")


class VectorFieldsModuleTest(unittest.TestCase):
    def test_bundle_matches_source_once_after_graph_curves(self):
        marker = '<script id="promath-vector-fields">\n'
        self.assertEqual(HTML.count(marker), 1)
        embedded = HTML.split(marker, 1)[1].split("</script>", 1)[0]
        self.assertEqual(embedded.rstrip("\n"), SOURCE.rstrip("\n"))
        curves = HTML.index('<script id="promath-graph-curves">')
        self.assertEqual(HTML.index("</script>\n", curves) + len("</script>\n"), HTML.index(marker))
        self.assertIn('("promath-graph-curves", "src/graph-curves.js"),\n    ("promath-vector-fields", "src/vector-fields.js"),', BUILD)

    def test_no_dynamic_code_or_network(self):
        for banned in ("eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket", "import(",
                       "<!--", "-->", "<script", "</script", "document.write", "localStorage"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, SOURCE)
        self.assertEqual(SOURCE.count("innerHTML="), 1)
        template = SOURCE.split("root.innerHTML=", 1)[1].split(";\n", 1)[0]
        self.assertNotIn("${", template)
        self.assertIsNone(re.search(r"'\+[A-Za-z_$(]", template.replace("'+\n'", "")))

    def test_uses_safe_evaluator_and_public_api(self):
        self.assertIn("M.numerical.evaluate(expr,env)", SOURCE)
        self.assertEqual(SOURCE.count("M.numerical.evaluate("), 1)
        self.assertIn("M.vectorFields=api", SOURCE)
        for name in ("quiver", "streamline", "streamlines", "slopeField", "solution", "equilibria", "draw"):
            self.assertRegex(SOURCE, r"const api=\{[^}]*\b" + name + r"\b")
        self.assertIn("M.dataTables.importData(", SOURCE)
        self.assertIn("MAX_GRID=40", SOURCE)

    def test_accessible_controls_and_motion(self):
        for fragment in ("root.id='fields-details'", 'role="status" aria-live="polite"', 'role="img"',
                         'aria-pressed="false"', "prefers-reduced-motion: reduce", "for=\"fields-p\"",
                         'for="fields-q"', 'for="fields-f"', 'for="fields-seeds"', "min-height:42px",
                         "fields-error", "getElementById('curves-details')"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SOURCE)

    def test_workflow_registers_browser_smoke(self):
        self.assertIn("run: python tests/smoke_vector_fields.py", WORKFLOW)
        self.assertTrue((ROOT / "tests" / "smoke_vector_fields.py").is_file())


if __name__ == "__main__":
    unittest.main()
