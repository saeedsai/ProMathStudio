"""Guard canonical Engineering LU metadata, reuse and standalone source parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringLuRouteTests(unittest.TestCase):
    def test_single_canonical_route_and_bundle(self):
        source = (ROOT / 'src/engineering-catalog.js').read_text(encoding='utf-8').rstrip('\n')
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        marker = '<script id="promath-engineering-catalog">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split('</script>', 1)[0].rstrip('\n')
        self.assertEqual(source, bundled)
        self.assertEqual(source.count("['matrix.lu.real.small'"), 1)
        self.assertIn("'calculator','matrix','mat-lu']", source)
        self.assertIn('if(t.route.focusId)', source)
        self.assertNotIn('function lu(', source)
        matrix = (ROOT / 'src/matrix-tools.js').read_text(encoding='utf-8')
        self.assertIn("['mat-lu','lu']", matrix)
        self.assertIn('function lu(A)', matrix)


if __name__ == '__main__':
    unittest.main()
