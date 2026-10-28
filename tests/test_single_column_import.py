"""Guard standalone parity and opt-in single-column Data Tables import."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')
SOURCE = (ROOT / 'src/data-tables.js').read_text(encoding='utf-8')


class SingleColumnImportTests(unittest.TestCase):
    def test_graph_parser_is_opt_in(self):
        self.assertIn('function csvRows(text, options={})', HTML)
        self.assertIn('function jsonRows(text, options={})', HTML)
        self.assertIn("options.allowSingleColumn===true", HTML)
        self.assertIn("const minColumns=options.allowSingleColumn===true?1:2;", HTML)
        self.assertIn("if(table.headers.length<2||table.headers.length>MAX_COLS", HTML)

    def test_data_tables_only_opt_in(self):
        self.assertIn("const options={allowSingleColumn:true,delimiterHint:", SOURCE)
        self.assertIn('decoder.parseJSON(text,options):decoder.parseCSV(text,options)', SOURCE)
        self.assertIn("const tbl=/\\.json$/i.test(file.name)?window.MathStudio.graphData.parseJSON(text):window.MathStudio.graphData.parseCSV(text)", SOURCE)

    def test_standalone_parity(self):
        marker = '<script id="mathstudio-data-tables">\n'
        embedded = HTML.split(marker, 1)[1].split('</script>', 1)[0]
        self.assertEqual(embedded.rstrip('\n'), SOURCE.rstrip('\n'))


if __name__ == '__main__':
    unittest.main()
