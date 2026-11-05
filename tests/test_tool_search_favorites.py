"""Find a tool recents/pins/browse: preferences module parity, guarded storage, bounds, ARIA and CI."""
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFS = (ROOT / "src/tool-prefs.js").read_text(encoding="utf-8")
SEARCH = (ROOT / "src/tool-search.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


def bundled(tag):
    marker = '<script id="' + tag + '">\n'
    assert HTML.count(marker) == 1, tag
    return HTML.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")


class ToolSearchFavoritesTests(unittest.TestCase):
    def test_bundle_parity_and_order(self):
        self.assertEqual(PREFS.rstrip("\n"), bundled("promath-tool-prefs"))
        self.assertEqual(SEARCH.rstrip("\n"), bundled("promath-tool-search"))
        ids = re.findall(r'<script id="([^"]+)">', HTML)
        self.assertEqual(ids[-2:], ["promath-tool-prefs", "promath-tool-search"])
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-tool-prefs", "src/tool-prefs.js"),\n    ("promath-tool-search", "src/tool-search.js"),\n]', build)

    def test_safety(self):
        for source in (PREFS, SEARCH):
            for forbidden in ("eval(", "new Function(", "innerHTML", "fetch(", "XMLHttpRequest", "<!--", "-->", "<script", "</script"):
                self.assertNotIn(forbidden, source)
        # Only the preferences module touches browser storage, and every access is guarded.
        self.assertNotIn("localStorage", SEARCH)
        self.assertEqual(PREFS.count("localStorage"), 2)
        for line in PREFS.splitlines():
            if "localStorage" in line:
                self.assertRegex(line, r"try\{|^\s+const raw=", line)
        self.assertIn("catch{persisted=false;return null;}", PREFS)
        self.assertIn("let persisted=true;\nfunction read(){", PREFS)
        self.assertIn("catch{persisted=false;}", PREFS)
        self.assertNotIn("document.", PREFS)


    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_initial_storage_failure_and_recovery_are_reported(self):
        # Execute the production module against failing, corrupt and recoverable
        # Storage implementations, rather than testing only its source text.
        js = r"""
const assert=require('assert'),fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('src/tool-prefs.js','utf8');
function load(storage){
 const math={};
 vm.runInNewContext(source,{window:{MathStudio:math,localStorage:storage}});
 return math.toolPrefs;
}
const blocked={getItem(){throw Error('SecurityError')},setItem(){throw Error('SecurityError')}};
let prefs=load(blocked);
assert.equal(prefs.persisted(),false,'blocked read must not claim persistence');
assert.equal(prefs.addRecent('panel:fft-details'),true);
assert.deepEqual(Array.from(prefs.recent()),['panel:fft-details']);
assert.equal(prefs.setPinned('panel:fft-details',true),true);
assert.deepEqual(Array.from(prefs.pinned()),['panel:fft-details']);
assert.equal(prefs.persisted(),false,'in-memory fallback must remain session-only');

let raw='{not valid json';
const recover={getItem(){return raw},setItem(key,value){raw=value}};
prefs=load(recover);
assert.equal(prefs.persisted(),false,'corrupt preferences were not restored');
assert.equal(prefs.addRecent('panel:brent-details'),true);
assert.equal(prefs.persisted(),true,'successful rewrite must recover persistence');
assert.deepEqual(JSON.parse(raw).recents,['panel:brent-details']);

for(const invalid of ['null','[]','"text"','42']){
 raw=invalid;prefs=load(recover);
 assert.equal(prefs.persisted(),false,'invalid storage root must be session-only: '+invalid);
 assert.deepEqual(Array.from(prefs.recent()),[]);
 assert.equal(prefs.addRecent('panel:fft-details'),true);
 assert.equal(prefs.persisted(),true,'valid rewrite restores persistence: '+invalid);
 assert.deepEqual(JSON.parse(raw).recents,['panel:fft-details']);
}

// A corrupt list type must not discard the other valid list.
raw=JSON.stringify({v:1,recents:['panel:fft-details'],pins:'invalid'});
prefs=load(recover);
assert.equal(prefs.persisted(),false,'malformed pin list requires repair');
assert.deepEqual(Array.from(prefs.recent()),['panel:fft-details']);
assert.deepEqual(Array.from(prefs.pinned()),[]);
assert.equal(prefs.setPinned('panel:matrix-tools',true),true);
assert.equal(prefs.persisted(),true,'rewriting repaired lists restores persistence');
assert.deepEqual(JSON.parse(raw).pins,['panel:matrix-tools']);

let writable=false,stored=null;
const quota={getItem(){return stored},setItem(key,value){if(!writable)throw Error('QuotaExceededError');stored=value}};
prefs=load(quota);
assert.equal(prefs.persisted(),true,'readable empty storage is available initially');
prefs.addRecent('panel:matrix-tools');
assert.equal(prefs.persisted(),false,'failed write reports session-only status');
writable=true;
prefs.addRecent('panel:fft-details');
assert.equal(prefs.persisted(),true,'later successful save clears failure');
assert.deepEqual(JSON.parse(stored).recents,['panel:fft-details','panel:matrix-tools']);

// Invalid IDs must not enter the session or saved preferences.
const invalids=['','  ','panel:fft-details\n','panel:fft-details\u007f','x'.repeat(201)];
for(const id of invalids){
 assert.equal(prefs.addRecent(id),false,'invalid recent ID '+JSON.stringify(id));
 assert.equal(prefs.setPinned(id,true),false,'invalid pinned ID '+JSON.stringify(id));
}
stored=JSON.stringify({v:1,recents:[' ','panel:fft-details\n','panel:fft-details','panel:fft-details'],pins:['\u0000','panel:matrix-tools']});
prefs=load(quota);
assert.deepEqual(Array.from(prefs.recent()),['panel:fft-details']);
assert.deepEqual(Array.from(prefs.pinned()),['panel:matrix-tools']);
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_namespaced_key_and_bounds(self):
        self.assertIn("KEY='promath-tool-search-prefs-v1'", PREFS)
        self.assertIn("MAX_RECENT=8", PREFS)
        self.assertIn("MAX_PINS=20", PREFS)
        self.assertIn("out.includes(id)", PREFS)  # Dedupe.
        self.assertIn("M.toolPrefs=Object.freeze(", PREFS)
        # Search filters stored IDs against the live index so removed tools are dropped.
        self.assertIn("const openable=id=>byId.get(id)?.status==='available';", SEARCH)
        self.assertIn("prefs.recent(openable)", SEARCH)
        self.assertIn("prefs.pinned(openable)", SEARCH)
        self.assertIn("const wasPersisted=prefs.persisted?.();", SEARCH)
        self.assertIn("Preferences are now saved to this browser.", SEARCH)

    def test_accessible_groups_pins_and_browse(self):
        for needle in ("'role','group'", "'aria-labelledby'", "'Recent tools'", "'Pinned tools'", "'aria-pressed'",
                       "(on?'Unpin ':'Pin ')+item.title", "pin.tabIndex=-1", "e.code==='KeyP'", "Alt+P",
                       "'Browse all tools'", "ts-browse-group", "min-width:40px;min-height:40px", ".ts-pin:focus-visible"):
            self.assertIn(needle, SEARCH)
        # Browse items reuse the existing open path rather than routing on their own.
        self.assertIn("if(openItem(item))remember(item);", SEARCH)
        for key in ("recent:", "pinned:", "pin:", "browse:"):
            self.assertIn(" " + key, SEARCH.split("M.toolSearch=Object.freeze(", 1)[1])

    def test_ci_registration(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_tool_search_favorites.py", workflow)


if __name__ == "__main__":
    unittest.main()
