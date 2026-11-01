"""Data Tables toolbar accessibility style and self-contained source parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DataToolbarTargetsTests(unittest.TestCase):
    def test_toolbar_controls_have_40px_minimum_and_bundle_parity(self):
        source = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        inline = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source.rstrip("\n"), inline)
        self.assertIn(".data-toolbar button{font-size:12px;min-height:40px}", source)
        self.assertIn(
            ".data-toolbar input,.data-toolbar select{min-height:40px;box-sizing:border-box",
            source,
        )
        self.assertNotIn(".data-toolbar button{font-size:12px;min-height:37px}", source)


if __name__ == "__main__":
    unittest.main()
