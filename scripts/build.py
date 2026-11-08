"""Rebuild standalone HTML from modular JavaScript without changing script spacing."""
from pathlib import Path
import os
import re
import stat
import sys
import tempfile

if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--check"):
    raise SystemExit("Usage: python scripts/build.py [--check]")

root = Path(__file__).resolve().parents[1]
index = root / "index.html"
if index.is_symlink():
    raise ValueError("Refusing to rewrite symlinked standalone index.html")
try:
    with index.open("r", encoding="utf-8", newline="") as source_file:
        text = source_file.read()
except UnicodeDecodeError as error:
    raise ValueError("Invalid UTF-8 in standalone index.html") from error
if "\r" in text:
    raise ValueError("Unexpected carriage return in standalone index.html")
if text.startswith("\ufeff"):
    raise ValueError("Unexpected UTF-8 BOM in standalone index.html")
if "\x00" in text:
    raise ValueError("Unexpected NUL character in standalone index.html")
if any(ord(char) < 32 and char not in "\n\t" for char in text):
    raise ValueError("Unexpected ASCII control character in standalone index.html")

original_index_text = text

modules = [
    ("mathstudio-data-tables", "src/data-tables.js"),
    ("promath-advanced-features", "src/advanced-features.js"),
    ("promath-numerical-data", "src/numerical-data.js"),
    ("promath-function-analysis", "src/function-analysis.js"),
    ("promath-interpolation-tools", "src/interpolation-tools.js"),
    ("promath-integration-tools", "src/integration-tools.js"),
    ("promath-vector-calculus", "src/vector-calculus.js"),
    ("promath-gnss-tools", "src/gnss-tools.js"),
    ("promath-context-actions", "src/context-actions.js"),
    ("promath-visual-controls", "src/visual-controls.js"),
    ("promath-matrix-tools", "src/matrix-tools.js"),
    ("promath-matrix-extras", "src/matrix-extras.js"),
    ("promath-control-equilibrium", "src/control-equilibrium.js"),
    ("promath-ode-tools", "src/ode-tools.js"),
    ("promath-stiff-ode", "src/stiff-ode.js"),
    ("promath-bvp-tools", "src/bvp-tools.js"),
    ("promath-minimize-tools", "src/minimize-tools.js"),
    ("promath-optimization-tools", "src/optimization-tools.js"),
    ("promath-fft-tools", "src/fft-tools.js"),
    ("promath-signal-filters", "src/signal-filters.js"),
    ("promath-brent-tools", "src/brent-tools.js"),
    ("promath-statistics-tools", "src/statistics-tools.js"),
    ("promath-uncertainty-tools", "src/uncertainty-tools.js"),
    ("promath-nonlinear-fit", "src/nonlinear-fit.js"),
    ("promath-random-tools", "src/random-tools.js"),
    ("promath-xlsx-tools", "src/xlsx-tools.js"),
    ("promath-xlsx-import", "src/xlsx-import.js"),
    ("promath-multivariate-tools", "src/multivariate-tools.js"),
    ("promath-project-schema", "src/project-schema.js"),
    ("promath-precision-tools", "src/precision-tools.js"),
    ("promath-units-tools", "src/units-tools.js"),
    ("promath-polynomial-tools", "src/polynomial-tools.js"),
    ("promath-workspace-tasks", "src/workspace-tasks.js"),
    ("promath-complex-graph", "src/complex-graph.js"),
    ("promath-graph-curves", "src/graph-curves.js"),
    ("promath-vector-fields", "src/vector-fields.js"),
    ("promath-control-theory", "src/control-theory.js"),
    ("promath-engineering-simulations", "src/engineering-simulations.js"),
    ("promath-engineering-catalog", "src/engineering-catalog.js"),
    ("promath-engineering-visuals", "src/engineering-visuals.js"),
    ("promath-tool-prefs", "src/tool-prefs.js"),
    ("promath-tool-search", "src/tool-search.js"),
]
drift_sources = []
source_snapshots = {}
for tag, source in modules:
    marker = f'<script id="{tag}">\n'
    if text.count(marker) != 1:
        raise ValueError(f"Expected exactly one standalone script marker: {tag}")
    start = text.index(marker) + len(marker)
    end = text.find("</script>", start)
    if end < 0:
        raise ValueError(f"Missing standalone script closing tag: {tag}")
    nested_script = re.search(r"<script(?=[\s/>])", text[start:end], flags=re.IGNORECASE)
    if nested_script is not None:
        raise ValueError(f"Nested script opening before standalone module close: {tag}")
    original = text[start:end]
    trailing_newlines = original[len(original.rstrip("\n")):]
    source_path = root / source
    if source_path.is_symlink() or source_path.parent.is_symlink():
        raise ValueError(f"Refusing symlinked standalone module source: {source}")
    if not source_path.is_file():
        raise FileNotFoundError(f"Missing standalone module source: {source}")
    try:
        with source_path.open("r", encoding="utf-8", newline="") as module_file:
            module_source = module_file.read()
        source_snapshots[source] = module_source
        if "\r" in module_source:
            raise ValueError(f"Unexpected carriage return in standalone module source: {source}")
        module_source = module_source.rstrip("\n")
    except UnicodeDecodeError as error:
        raise ValueError(f"Invalid UTF-8 in standalone module source: {source}") from error
    if not module_source.strip():
        raise ValueError(f"Empty standalone module source: {source}")
    if "\x00" in module_source:
        raise ValueError(f"Unexpected NUL byte in standalone module source: {source}")
    if any(ord(char) < 32 and char not in "\n\t" for char in module_source):
        raise ValueError(f"Unexpected ASCII control character in standalone module source: {source}")
    if module_source.startswith("\ufeff"):
        raise ValueError(f"Unexpected UTF-8 BOM in standalone module source: {source}")
    if "<!--" in module_source or "-->" in module_source:
        raise ValueError(f"Unsafe HTML comment delimiter in module: {source}")
    if re.search(r"<script(?=[\s/>])", module_source, flags=re.IGNORECASE):
        raise ValueError(f"Unsafe script opening sequence in module: {source}")
    if "</script" in module_source.lower():
        raise ValueError(f"Unsafe script closing sequence in module: {source}")
    replacement = module_source + trailing_newlines
    if original != replacement:
        drift_sources.append(source)
    text = text[:start] + replacement + text[end:]

def verify_source_snapshots():
    """Reject stale results if a module changed after it was assembled."""
    for source, snapshot in source_snapshots.items():
        source_path = root / source
        if source_path.is_symlink() or source_path.parent.is_symlink():
            raise RuntimeError(f"Standalone module changed during rebuild: {source}; retry")
        with source_path.open("r", encoding="utf-8", newline="") as current_source:
            if current_source.read() != snapshot:
                raise RuntimeError(f"Standalone module changed during rebuild: {source}; retry")


if "--check" in sys.argv[1:]:
    # The read-only check must not report success for a stale module snapshot.
    verify_source_snapshots()
    # Compare with the same snapshot used to assemble the bundle; do not
    # reopen index.html after modules have been processed.
    original_text = original_index_text
    if text != original_text:
        mismatch = next((i for i, (actual, expected) in enumerate(zip(original_text, text)) if actual != expected), min(len(original_text), len(text)))
        line = original_text.count("\n", 0, mismatch) + 1
        column = mismatch - original_text.rfind("\n", 0, mismatch)
        module_hint = (f" (modules: {', '.join(drift_sources[:3])}"
                       f"{', ...' if len(drift_sources) > 3 else ''}; mismatched modules: {len(drift_sources)})") if drift_sources else ""
        raise SystemExit(f"Standalone index.html is out of sync near line {line}, column {column}{module_hint}; run python scripts/build.py")
    print("Standalone index.html matches modular sources")
else:
    if text != original_index_text:
        # Stage the complete LF-normalized output beside index.html, then replace
        # it atomically. A failed write/rename must never truncate the live bundle.
        staged = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="\n",
                prefix=".promath-index-", suffix=".tmp",
                dir=index.parent, delete=False,
            ) as output:
                staged = Path(output.name)
                output.write(text)
                output.flush()
                os.fsync(output.fileno())
            staged.chmod(stat.S_IMODE(index.stat().st_mode))
            # A separate editor/build may have changed index.html while modules
            # were read. Never replace those newer edits with this stale snapshot.
            with index.open("r", encoding="utf-8", newline="") as current_file:
                if current_file.read() != original_index_text:
                    raise RuntimeError("Standalone index.html changed during rebuild; retry")
            # A module edited during assembly must not be published as stale code.
            # Compare complete source snapshots, not only mtimes (which can be
            # restored or have coarse resolution on some filesystems).
            verify_source_snapshots()
            os.replace(staged, index)
        finally:
            if staged is not None:
                staged.unlink(missing_ok=True)
        print("Rebuilt standalone index.html")
    else:
        # A no-op build must also reject modules modified after their first
        # read; otherwise it can falsely report a consistent bundle.
        verify_source_snapshots()
        print("Standalone index.html already up to date")
