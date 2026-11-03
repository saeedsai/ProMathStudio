"""Complex Graph UI controller extracted to src/complex-graph.js: declared, embedded exactly, registered."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ComplexGraphModuleTests(unittest.TestCase):
    def test_extracted_module_parity_and_registration(self):
        source = (ROOT / "src/complex-graph.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('<script id="promath-complex-graph">\n'), 1)
        bundled = html.split('<script id="promath-complex-graph">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn('("promath-complex-graph", "src/complex-graph.js")',
                      (ROOT / "scripts/build.py").read_text(encoding="utf-8"))
        # The controller stays DOM-guarded and free of dynamic evaluation.
        self.assertIn("if(!root)return;", source)
        self.assertNotIn("eval(", source)
        self.assertNotIn("new Function(", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_complex_graph_module.py", workflow)


if __name__ == "__main__":
    unittest.main()
