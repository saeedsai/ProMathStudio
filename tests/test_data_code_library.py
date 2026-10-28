"""Structural regression for the Data Tables Functions & Code Library."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DataCodeLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_catalog_and_standalone_parity(self):
        self.assertIn(self.source, self.html)
        for key in ('dt-code-library', 'dt-library-search', 'dt-library-category'):
            self.assertIn('id="' + key + '"', self.source)
        for name in ('SUM', 'AVERAGE', 'MIN', 'MAX', 'COUNT', 'IF',
                     'Filter rows', 'Group and sum', 'INNER JOIN',
                     'UNION ALL', 'INTERSECT', 'EXCEPT'):
            self.assertIn("name:'" + name + "'", self.source)

    def test_cell_selection_survives_grid_rebuild(self):
        self.assertIn("lastLibraryCell={id:active()?.id,r:Number(event.target.dataset.row)", self.source)
        self.assertIn("t.rows[cell.r][cell.c]=entry.sample.slice(0,8000)", self.source)
        self.assertIn("save();render();", self.source)
        self.assertIn("cell.id!==t?.id", self.source)
        self.assertNotIn("lastLibraryCell=event.target;", self.source)

    def test_code_never_runs_on_insert(self):
        self.assertIn("target.setRangeText(entry.sample,start,end,'end')", self.source)
        self.assertIn("Code has not run.", self.source)
        self.assertIn("selector.value=entry.operation;", self.source)
        self.assertIn("entry.kind==='Operation'?'Choose':'Insert'", self.source)

if __name__ == "__main__":
    unittest.main()
