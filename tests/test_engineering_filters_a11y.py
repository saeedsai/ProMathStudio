"""Engineering Toolbox filters: accessible 40px targets and standalone parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringFilterAccessibilityTests(unittest.TestCase):
    def test_filters_are_accessible_and_standalone_is_synchronized(self):
        source = (ROOT / 'src/engineering-catalog.js').read_text(encoding='utf-8').rstrip('\n')
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        marker = '<script id="promath-engineering-catalog">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split('</script>', 1)[0].rstrip('\n')
        self.assertEqual(source, bundled)
        self.assertIn('#engineering-panel input,#engineering-panel select{width:100%;min-width:0;min-height:40px;', source)
        self.assertIn('#engineering-panel input:focus-visible,#engineering-panel select:focus-visible{outline:3px', source)
        self.assertIn('id="eng-status" role="status" aria-live="polite"', source)
        self.assertIn('<label>Discipline<select id="eng-discipline"', source)
        self.assertIn('<label>Search tools<input id="eng-search"', source)


if __name__ == '__main__':
    unittest.main()
