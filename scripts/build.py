"""Rebuild standalone HTML from modular JavaScript without changing script spacing."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
index = root / "index.html"
text = index.read_text(encoding="utf-8")

modules = [
    ("mathstudio-data-tables", "src/data-tables.js"),
    ("promath-advanced-features", "src/advanced-features.js"),
    ("promath-numerical-data", "src/numerical-data.js"),
    ("promath-interpolation-tools", "src/interpolation-tools.js"),
    ("promath-context-actions", "src/context-actions.js"),
    ("promath-matrix-tools", "src/matrix-tools.js"),
    ("promath-ode-tools", "src/ode-tools.js"),
    ("promath-minimize-tools", "src/minimize-tools.js"),
    ("promath-brent-tools", "src/brent-tools.js"),
    ("promath-xlsx-tools", "src/xlsx-tools.js"),
    ("promath-xlsx-import", "src/xlsx-import.js"),
    ("promath-project-schema", "src/project-schema.js"),
    ("promath-precision-tools", "src/precision-tools.js"),
    ("promath-workspace-tasks", "src/workspace-tasks.js"),
]
for tag, source in modules:
    marker = f'<script id="{tag}">\n'
    start = text.index(marker) + len(marker)
    end = text.index("</script>", start)
    original = text[start:end]
    trailing_newlines = original[len(original.rstrip("\n")):]
    module_source = (root / source).read_text(encoding="utf-8").rstrip("\n")
    text = text[:start] + module_source + trailing_newlines + text[end:]

index.write_text(text, encoding="utf-8")
print("Rebuilt standalone index.html")
