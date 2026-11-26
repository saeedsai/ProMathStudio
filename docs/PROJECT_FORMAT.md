# Shared workspace, saved data and project files

## Working equation hub

The **Working equation** field is the shared source for sending expressions between editor, calculator, solver, 2D graph, 3D graph and notebook. The source dropdown can select drafts, calculator result/expression, solver input/results, graph lines, notebook entries and recent expressions. **Use open input** captures the active workspace input.

**Sending to Calculator:** a solved assignment such as `x=2` can send the numeric right-hand side; an unsolved equation like `x^2=2` is not quietly replaced by a side of the equality. Choose one solved root.

**Sending to Graph:** ordinary equalities are converted to difference/residual curves; 3D shows `z=f(x,y)`.

## Browser persistence

The application uses these localStorage keys:
- `mathstudio-equations-v1` — saved equation notebook.
- `mathstudio-calculator-history` — recent calculations.
- `mathstudio-connected-v1` — current working expression, origin and recent inputs.

Use project export for a portable backup. Private/incognito browsing, storage settings or clearing site data may delete browser-saved entries.

## JSON backup format

Select **Save project** to download `MathStudio_Project.json`. Current export format identity and version (version 2):

```json
{
  "format": "mathstudio-project",
  "version": 2,
  "date": "2026-10-23T00:00:00.000Z",
  "working": "x^2=1",
  "origin": "solver",
  "recent": [],
  "notebook": [],
  "calculator": {},
  "solver": {
    "expression": "x^2=1",
    "variable": "x",
    "operation": "solve",
    "engine": "auto"
  },
  "graph": {}
}
```

`calculator` and `graph` contain application-maintained state, including calculator history and graph mode, functions, bounds, camera and zoom. The abbreviated objects above are illustrative, not a complete validated JSON schema.

## Restoring projects

**Open project** reads a JSON file of at most **2 MB**, checks its format/version and notebook array, then requests confirmation. Import **replaces** current saved notebook, calculator history and graph settings; save your existing project first. The importer accepts legacy version 1 backups and version 2 backups, migrating version 1 to version 2 in memory without dropping supported workbook, formula, graph or notebook fields. New exports use version 2. Before confirmation, it validates notebook entries, calculator history, custom functions, graph datasets, table dimensions and cell sizes; unsupported versions, malformed structures and files larger than 2 MB are refused without changing the project. A restore-stage exception triggers a best-effort rollback to the previous in-memory project. Browser storage quota errors or a second failure during rollback cannot be guaranteed recoverable; save an independent backup before importing.

## Privacy and synchronization

Project files are saved on the user's device through browser downloads. The app has no login, cloud project synchronization or server storage. SymPy library files load from a CDN, while math computations execute locally.

[Architecture](ARCHITECTURE.md) · [Backup troubleshooting](TROUBLESHOOTING.md)

## Graph datasets in project backup

Version 1 projects now optionally include `graph.dataset`:

```json
{"name":"samples.csv","headers":["x","y","z"],"rows":[[0,1,2],[1,2,3]],"x":"0","y":"1","z":"2","style":"points"}
```

Graph state remains backward compatible: a missing dataset imports as no plotted data. **Save project** retains imported rows and mappings. The optional `extra` field stores up to 20 additional series; each entry contains a bounded name, a table with 2–32 headers and 1–6,000 rows, and a mapping with distinct X/Y columns plus a valid optional 2D/3D mode, Z column for 3D, and `points`, `line` or `grid` style. Each overlay must contain at least one numeric point for its selected axes. Malformed, over-limit or unrenderable overlays are rejected before import instead of being silently truncated or dropped. Legacy projects that omit `extra` remain supported. See [Data import](DATA_IMPORT.md).
