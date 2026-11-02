"""Tiny-residual sign bracketing, source/bundle parity and CI registration."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarRootSignUnderflowTests(unittest.TestCase):
    def test_direct_sign_comparison_and_bundle_parity(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-numerical-data">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Math.sign(fa)===Math.sign(fb)", source)
        self.assertIn("Math.sign(fa)!==Math.sign(fm)", source)
        self.assertIn("fa===0||fb===0", source)
        self.assertNotIn("fa*fb>=0", source)
        self.assertNotIn("fa*fm<0", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_scalar_root_sign_underflow.py", workflow)


if __name__ == "__main__":
    unittest.main()
