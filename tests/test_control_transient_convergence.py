"""Control RK4 step-doubling feature and offline bundle regression."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ControlRK4ConvergenceTests(unittest.TestCase):
    def test_rk4_refinement_reuses_canonical_solver_and_keeps_bundle_in_sync(self):
        source = (ROOT / 'src/control-equilibrium.js').read_text(encoding='utf-8')
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        marker = '<script id="promath-control-equilibrium">\n'
        self.assertEqual(source.rstrip('\n'), html.split(marker, 1)[1].split('</script>', 1)[0].rstrip('\n'))
        self.assertIn("studio.odeTools.solveSystem(", source)
        self.assertIn("lastTransient.steps<=500", source)
        self.assertIn("lastTransient.steps*2", source)
        self.assertIn("Math.max(Math.abs(end[1]-fineEnd[1]),Math.abs(end[2]-fineEnd[2]))", source)
        self.assertIn("RK4 step-doubling |x_N - x_2N|∞:", source)
        self.assertIn("not a global error bound", source)
        self.assertIn("Step-doubling comparison unavailable", source)

if __name__ == '__main__':
    unittest.main()
