"""Rebuild standalone HTML from modular JavaScript without changing script spacing."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
index = root / "index.html"
text = index.read_text(encoding="utf-8")

modules = [
    ("mathstudio-data-tables", "src/data-tables.js"),
    ("promath-advanced-features", "src/advanced-features.js"),
    ("promath-numerical-data", "src/numerical-data.js"),
    ("promath-interpolation-tools", "src/interpolation-tools.js"),
    ("promath-integration-tools", "src/integration-tools.js"),
    ("promath-context-actions", "src/context-actions.js"),
    ("promath-visual-controls", "src/visual-controls.js"),
    ("promath-matrix-tools", "src/matrix-tools.js"),
    ("promath-control-equilibrium", "src/control-equilibrium.js"),
    ("promath-ode-tools", "src/ode-tools.js"),
    ("promath-stiff-ode", "src/stiff-ode.js"),
    ("promath-minimize-tools", "src/minimize-tools.js"),
    ("promath-optimization-tools", "src/optimization-tools.js"),
    ("promath-fft-tools", "src/fft-tools.js"),
    ("promath-brent-tools", "src/brent-tools.js"),
    ("promath-statistics-tools", "src/statistics-tools.js"),
    ("promath-uncertainty-tools", "src/uncertainty-tools.js"),
    ("promath-xlsx-tools", "src/xlsx-tools.js"),
    ("promath-xlsx-import", "src/xlsx-import.js"),
    ("promath-project-schema", "src/project-schema.js"),
    ("promath-precision-tools", "src/precision-tools.js"),
    ("promath-units-tools", "src/units-tools.js"),
    ("promath-workspace-tasks", "src/workspace-tasks.js"),
    ("promath-complex-graph", "src/complex-graph.js"),
    ("promath-graph-curves", "src/graph-curves.js"),
    ("promath-control-theory", "src/control-theory.js"),
    ("promath-engineering-simulations", "src/engineering-simulations.js"),
    ("promath-engineering-catalog", "src/engineering-catalog.js"),
    ("promath-engineering-visuals", "src/engineering-visuals.js"),
]
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
    if not source_path.is_file():
        raise FileNotFoundError(f"Missing standalone module source: {source}")
    try:
        module_source = source_path.read_text(encoding="utf-8").rstrip("\n")
    except UnicodeDecodeError as error:
        raise ValueError(f"Invalid UTF-8 in standalone module source: {source}") from error
    if not module_source.strip():
        raise ValueError(f"Empty standalone module source: {source}")
    if "\x00" in module_source:
        raise ValueError(f"Unexpected NUL byte in standalone module source: {source}")
    if module_source.startswith("\ufeff"):
        raise ValueError(f"Unexpected UTF-8 BOM in standalone module source: {source}")
    if "<!--" in module_source or "-->" in module_source:
        raise ValueError(f"Unsafe HTML comment delimiter in module: {source}")
    if re.search(r"<script(?=[\s/>])", module_source, flags=re.IGNORECASE):
        raise ValueError(f"Unsafe script opening sequence in module: {source}")
    if "</script" in module_source.lower():
        raise ValueError(f"Unsafe script closing sequence in module: {source}")
    text = text[:start] + module_source + trailing_newlines + text[end:]

index.write_text(text, encoding="utf-8")
print("Rebuilt standalone index.html")
