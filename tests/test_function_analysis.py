"""Function analysis / inequality module: source-bundle parity, build order, safety and CI registration."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/function-analysis.js"


class FunctionAnalysisModuleTests(unittest.TestCase):
    def setUp(self):
        self.source = SOURCE.read_text(encoding="utf-8").rstrip("\n")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_bundle_parity_and_placement(self):
        marker = '<script id="promath-function-analysis">\n'
        self.assertEqual(self.html.count(marker), 1)
        bundled = self.html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(self.source, bundled)
        numerical = self.html.index('<script id="promath-numerical-data">\n')
        closing = self.html.index("</script>\n", numerical) + len("</script>\n")
        self.assertTrue(self.html.startswith(marker, closing), "module must follow numerical-data")

    def test_build_registration(self):
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        entry = '("promath-function-analysis", "src/function-analysis.js"),'
        self.assertIn(entry, build)
        self.assertLess(build.index('("promath-numerical-data", "src/numerical-data.js"),'), build.index(entry))

    def test_reuses_shared_kernels_and_is_safe(self):
        for phrase in ("M.numerical.scalarRoots", "rejectedSignChanges", "M.numerical.evaluate",
                       "M.minimizeTools", "M.functionAnalysis=", 'role="status" aria-live="polite"',
                       'role="img"', "function-analysis-details", "Save to Data Tables"):
            self.assertIn(phrase, self.source)
        for banned in ("eval(", "new Function", "fetch(", "XMLHttpRequest", "<!--", "-->"):
            self.assertNotIn(banned, self.source)
        self.assertIsNone(re.search(r"<script|</script", self.source, flags=re.IGNORECASE))
        # User text reaches the DOM only through textContent/attributes.
        self.assertEqual(self.source.count("innerHTML"), 1)
        self.assertNotIn("innerHTML+=", self.source)

    def test_honest_numerical_labels(self):
        for phrase in ("not a symbolic proof", "Sampled estimate", "heuristic", "not a proof"):
            self.assertIn(phrase, self.source)

    def test_ci_registration(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_function_analysis.py", workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_*.py'", workflow)


if __name__ == "__main__":
    unittest.main()
