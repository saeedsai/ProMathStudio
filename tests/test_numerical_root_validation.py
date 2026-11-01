"""Scalar root tolerance wiring, field-level errors and offline source parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RootValidationTests(unittest.TestCase):
    def test_scalar_tolerance_and_field_validation(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-numerical-data">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("scalar:['num-expression','num-variable','num-start','num-end','num-tolerance']", source)
        self.assertIn("result=scalarRoots(expr,v,a,b,{tolerance});", source)
        self.assertIn("if(!(b>a))invalidRoot('num-end'", source)
        self.assertIn("if(tolerance<=0||tolerance>0.01)invalidRoot('num-tolerance'", source)
        self.assertIn("field.setAttribute('aria-invalid','true')", source)
        self.assertIn("field.setAttribute('aria-describedby','num-output')", source)
        self.assertIn("else if(mode==='system')result=systemRoots", source)
        self.assertIn("function runNumerical(){clearRootErrors();try{", source)


if __name__ == "__main__":
    unittest.main()
