"""Canonical Engineering QR route: unique metadata, solver reuse and offline bundle parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringQrRouteTests(unittest.TestCase):
    def test_unique_qr_route_and_standalone_parity(self):
        source = (ROOT / 'src/engineering-catalog.js').read_text(encoding='utf-8').rstrip('\n')
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        marker = '<script id="promath-engineering-catalog">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split('</script>', 1)[0].rstrip('\n')
        self.assertEqual(source, bundled)
        self.assertEqual(source.count("['matrix.qr.real.small'"), 1)
        self.assertIn("'calculator','matrix','mat-qr']", source)
        self.assertIn("focusId:focusId||null", source)
        self.assertNotIn('function qr(', source)
        matrix = (ROOT / 'src/matrix-tools.js').read_text(encoding='utf-8')
        self.assertIn("['mat-qr','qr']", matrix)
        self.assertIn('function qr(A)', matrix)
        self.assertIn('orthogonality', matrix)

if __name__ == '__main__':
    unittest.main()
