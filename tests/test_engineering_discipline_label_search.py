"""Engineering catalog searchable display labels and preserved offline bundle."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringDisciplineLabelSearchTests(unittest.TestCase):
    def test_readable_discipline_labels_are_searchable(self):
        source = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-engineering-catalog">\n'
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(bundled, source.rstrip("\n"))
        self.assertIn("...t.disciplines.map(id=>disciplines.find(d=>d.id===id).title)", source)
        self.assertIn("terms.every(term=>", source)
        self.assertIn("toLocaleLowerCase().includes(term)", source)
        self.assertIn("['aerospace','Aerospace engineering']", source)
        self.assertIn("['gnss','GNSS positioning']", source)


if __name__ == "__main__":
    unittest.main()
