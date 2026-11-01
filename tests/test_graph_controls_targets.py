"""Regression guard for Graph axis/import touch target CSS and offline module parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GraphControlTargetsTests(unittest.TestCase):
    def test_minimum_height_and_bundle_parity(self):
        source = (ROOT / "src/data-tables.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        inline = html.split('<script id="mathstudio-data-tables">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, inline)
        self.assertIn(
            "#graph-panel .graph-controls input,#dt-advanced .graph-data-grid select,"
            "#dt-advanced .graph-data-grid button,#dt-advanced .graph-data-grid input[type=file]"
            "{min-height:40px;box-sizing:border-box}",
            source,
        )


if __name__ == "__main__":
    unittest.main()
