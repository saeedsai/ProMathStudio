"""Regression for full, inert saved-snippet inspection and source/bundle parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

class SnippetInspectionTests(unittest.TestCase):
    def test_readonly_full_source_and_safe_dom(self):
        self.assertIn('id="dt-snippet-inspect-code" readonly', SOURCE)
        self.assertIn("$('dt-snippet-inspect-code').value=entry.sample;", SOURCE)
        self.assertIn("$('dt-snippet-inspect-label').textContent=", SOURCE)
        self.assertIn("'View full snippet '+entry.name", SOURCE)
        start = SOURCE.index("inspect.addEventListener('click'")
        end = SOURCE.index("item.append(inspect,edit,remove);", start)
        self.assertNotIn('innerHTML', SOURCE[start:end])
        self.assertNotIn('eval(', SOURCE[start:end])
        self.assertNotIn('persistDataSnippets(', SOURCE[start:end])

    def test_keyboard_close_restores_focus_and_clears_source(self):
        self.assertIn("event.key==='Escape'&&!$('dt-snippet-inspect').hidden", SOURCE)
        self.assertIn("event.stopPropagation();closeSnippetInspection();", SOURCE)
        self.assertIn("$('dt-snippet-inspect-code').value='';", SOURCE)
        self.assertIn("if(target?.isConnected)target.focus();else $('dt-library-search').focus();", SOURCE)

    def test_standalone_parity(self):
        marker = '<script id="mathstudio-data-tables">\\n'
        embedded = HTML.split(marker, 1)[1].split('</script>', 1)[0]
        self.assertEqual(embedded.rstrip('\\n'), SOURCE.rstrip('\\n'))

if __name__ == "__main__":
    unittest.main()
