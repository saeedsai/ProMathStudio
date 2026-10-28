"""Regression guard for Data Tables formula and code library."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
html = (ROOT / "index.html").read_text(encoding="utf-8")

def test_library_present_in_standalone_and_module():
    for code in (source, html):
        assert 'id="dt-code-library"' in code
        assert 'id="dt-library-search"' in code
        assert 'renderDataLibrary()' in code
        assert "target.dispatchEvent(new Event('input',{bubbles:true}))" in code

def test_library_inserts_without_executing():
    assert "entry.kind==='Python' ? $('dt-python-code') : lastLibraryCell" in source
    assert "target.setRangeText(entry.sample,start,end,'end')" in source
    assert "Select a spreadsheet data cell first." in source
    library = source.split("const dataLibrary = [", 1)[1].split("];", 1)[0]
    for name in ("SUM", "AVERAGE", "MIN", "MAX", "COUNT", "IF", "Filter rows", "Group and sum"):
        assert "name:'" + name + "'" in library
    assert 'eval(' not in library
    assert 'new Function(' not in library

def test_source_matches_inline_bundle():
    assert source.strip() in html
