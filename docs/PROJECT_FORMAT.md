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

Select **Save project** to download `MathStudio_Project.json`. Current format identity and version:

```json
{
  "format": "mathstudio-project",
  "version": 1,
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

**Open project** reads a JSON file of at most **2 MB**, checks its format/version and notebook array, then requests confirmation. Import **replaces** current saved notebook, calculator history and graph settings; save your existing project first. The importer accepts format version 1 only. Invalid or corrupted input is rejected with a message.

## Privacy and synchronization

Project files are saved on the user's device through browser downloads. The app has no login, cloud project synchronization or server storage. SymPy library files load from a CDN, while math computations execute locally.

[Architecture](ARCHITECTURE.md) · [Backup troubleshooting](TROUBLESHOOTING.md)
