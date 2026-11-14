"""Static contract for the numerical differentiation / vector calculus module."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "vector-calculus.js"


def embedded(html, tag):
    marker = f'<script id="{tag}">\n'
    start = html.index(marker) + len(marker)
    return html[start:html.index("</script>", start)]


class VectorCalculusTests(unittest.TestCase):
    def setUp(self):
        self.src = SOURCE.read_text(encoding="utf-8")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_registered_after_integration_tools(self):
        build = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")
        integ = '    ("promath-integration-tools", "src/integration-tools.js"),\n'
        self.assertIn(integ + '    ("promath-vector-calculus", "src/vector-calculus.js"),\n', build)
        end = self.html.index("</script>\n", self.html.index('<script id="promath-integration-tools">')) + len("</script>\n")
        self.assertTrue(self.html.startswith('<script id="promath-vector-calculus">\n', end))

    def test_bundle_matches_source(self):
        self.assertEqual(embedded(self.html, "promath-vector-calculus").rstrip("\n"), self.src.rstrip("\n"))

    def test_no_dynamic_code_network_or_markup_breakers(self):
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"WebSocket", r"import\s*\("):
            self.assertIsNone(re.search(pattern, self.src), pattern)
        for token in ("<!--", "-->", "<script", "</script"):
            self.assertNotIn(token, self.src.lower())
        self.assertIn("M.numerical.evaluate(expr,env)", self.src)
        self.assertEqual(self.src.count("M.numerical.evaluate("), 1)
        # innerHTML only receives the static template.
        self.assertEqual(self.src.count(".innerHTML="), 1)
        self.assertNotIn("insertAdjacentHTML", self.src)

    def test_public_api_and_accessible_ui(self):
        self.assertIn("M.vectorCalculus={derivative,gradient,hessian,jacobian,divergence,curl,laplacian,directional,compute}", self.src)
        self.assertIn("details');area.id='vectorcalc-details'", self.src)
        self.assertIn("panel.append(area)", self.src)
        self.assertIn('id="vc-output" role="status" aria-live="polite"', self.src)
        self.assertIn("M.dataTables.importData(", self.src)
        self.assertIn("min-height:40px", self.src)
        self.assertIn("Ridders", self.src)
        self.assertIn("heuristic, not certified", self.src)

    def test_quality_workflow_runs_browser_smoke(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_vector_calculus.py", workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_*.py'", workflow)


if __name__ == "__main__":
    unittest.main()
