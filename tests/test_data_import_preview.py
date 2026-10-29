"""Guard transactional Data Tables file preview and standalone/module parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src/data-tables.js').read_text(encoding='utf-8')
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')


class DataImportPreviewTests(unittest.TestCase):
    def test_import_requires_confirmation(self):
        start = SOURCE.index("  $('dt-import').addEventListener('change'")
        end = SOURCE.index('  // Existing chart-data importer', start)
        handler = SOURCE[start:end]
        self.assertIn('pendingTableImport={', handler)
        self.assertIn('renderTableImportPreview(file.name,tbl)', handler)
        self.assertNotIn('makeTable(', handler)
        self.assertIn("$('dt-import-confirm').addEventListener('click'", SOURCE)
        self.assertIn('const t=makeTable(name,tbl.headers,tbl.rows)', SOURCE)

    def test_escape_and_cancel_discard_pending_data(self):
        self.assertIn("tableImportPreview.addEventListener('keydown'", SOURCE)
        self.assertIn("event.key!=='Escape'", SOURCE)
        self.assertIn("pendingTableImport=null;", SOURCE)
        self.assertIn("sample.replaceChildren(head,body)", SOURCE)

    def test_standalone_matches_module(self):
        start = HTML.index('/* ProMathStudio Data Tables workspace.')
        end = HTML.index('</script>', start)
        self.assertEqual(HTML[start:end], SOURCE)


if __name__ == '__main__':
    unittest.main()
