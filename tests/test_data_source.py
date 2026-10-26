"""Ensure standalone bundle, source module, and license are shipped."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class DataTablesStaticTests(unittest.TestCase):
 def test_data_module_is_bundled(self):
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  src=(ROOT/'src/data-tables.js').read_text(encoding='utf-8')
  self.assertIn('<script id="mathstudio-data-tables">',html)
  self.assertIn(src,html)
  self.assertIn('id="data-panel"',html)
  self.assertIn('mathstudio-tables-v1',html)
  matrix=(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8').rstrip('\n')
  self.assertIn('<script id="promath-matrix-tools">',html)
  self.assertIn(matrix,html)
  self.assertIn('id=\'mat-grid\'',matrix)
  self.assertIn('Saeedmsalehi1990@gmail.com',html)
  self.assertIn('MIT License',(ROOT/'LICENSE').read_text())
