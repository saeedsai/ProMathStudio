"""Expanded Engineering catalog must be unique, honest and bundled offline."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringDisciplinesExpansionTests(unittest.TestCase):
    def test_source_bundle_parity_and_nine_disciplines(self):
        source = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-engineering-catalog">\n'
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(bundled, source)
        for discipline in ("control", "gnss", "signals"):
            self.assertIn("['" + discipline + "'", source)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_unique_ids_and_planned_tool_status(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const source=fs.readFileSync('src/engineering-catalog.js','utf8');
const ids=[...source.matchAll(/^ \['([a-z]+(?:\.[a-z]+)+)'/gm)].map(x=>x[1]);
assert.equal(new Set(ids).size,ids.length,'tool IDs must be unique');
for(const id of ['gnss.positioning.least.squares','signals.spectral.analysis','control.frequency.response']){
 assert(ids.includes(id),id);
 const row=source.split('\n').find(x=>x.trimStart().startsWith("['"+id+"'"));
 assert(row && !/,'(calculator|graph|editor)'/.test(row),'planned workflows must not advertise executable route');
}
assert(source.includes("['control','Control Theory']"));
assert(source.includes("['gnss','GNSS positioning']"));
assert(source.includes("['signals','Signal engineering']"));
"""
        outcome = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(outcome.returncode, 0, outcome.stdout + outcome.stderr)


if __name__ == "__main__":
    unittest.main()
