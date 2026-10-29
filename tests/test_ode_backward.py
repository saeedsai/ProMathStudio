"""Static source/bundle parity and syntax check for backward RK4."""
from pathlib import Path
import subprocess
import unittest
ROOT = Path(__file__).resolve().parents[1]
class BackwardRK4(unittest.TestCase):
    def test_source_bundle_parity(self):
        src = (ROOT/"src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT/"index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-ode-tools">\n',1)[1].split("</script>",1)[0].rstrip("\n")
        self.assertEqual(src, embedded)
        self.assertIn("if(t1===t0)throw Error", src)
        self.assertIn("if(!Number.isFinite(h)||h===0)", src)
    def test_node_syntax(self):
        r = subprocess.run(["node","--check",str(ROOT/"src/ode-tools.js")],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
if __name__ == "__main__":
    unittest.main()
