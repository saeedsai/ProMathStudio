"""Every src module must equal its embedded copy in index.html, and a rebuild must not change index.html."""
import ast
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build.py"


def declared_modules():
    tree = ast.parse(BUILD.read_text(encoding="utf-8"))
    for statement in tree.body:
        if (isinstance(statement, ast.Assign) and len(statement.targets) == 1
                and getattr(statement.targets[0], "id", "") == "modules"):
            return ast.literal_eval(statement.value)
    raise AssertionError("No declared module list in scripts/build.py")


def embedded(html, tag):
    marker = f'<script id="{tag}">\n'
    start = html.index(marker) + len(marker)
    return html[start:html.index("</script>", start)]


class BundleSourceParityTests(unittest.TestCase):
    def test_every_src_module_is_declared_and_embedded_exactly(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        modules = declared_modules()
        declared = {Path(path).name for _, path in modules}
        on_disk = {p.name for p in (ROOT / "src").glob("*.js")}
        self.assertEqual(on_disk, declared, "every src/*.js file must be declared in scripts/build.py")
        stale = [tag for tag, path in modules
                 if embedded(html, tag).rstrip("\n") != (ROOT / path).read_text(encoding="utf-8").rstrip("\n")]
        self.assertEqual(stale, [], "src is out of sync with the embedded bundle (a rebuild would regress): " + ", ".join(stale))

    def test_rebuild_leaves_index_html_byte_identical(self):
        modules = declared_modules()
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            (dest / "scripts").mkdir()
            shutil.copy2(BUILD, dest / "scripts" / "build.py")
            shutil.copy2(ROOT / "index.html", dest / "index.html")
            for _, path in modules:
                (dest / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / path, dest / path)
            subprocess.run([sys.executable, str(dest / "scripts" / "build.py")],
                           check=True, capture_output=True, text=True, timeout=30)
            self.assertEqual((dest / "index.html").read_bytes(), (ROOT / "index.html").read_bytes(),
                             "building from src must reproduce the committed index.html")

    def test_negative_control_detects_drift(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        tag, path = declared_modules()[0]
        source = (ROOT / path).read_text(encoding="utf-8")
        self.assertEqual(embedded(html, tag).rstrip("\n"), source.rstrip("\n"))
        self.assertNotEqual(embedded(html, tag).rstrip("\n"), (source + "\n// drift").rstrip("\n"))


if __name__ == "__main__":
    unittest.main()
