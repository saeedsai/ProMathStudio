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

**Open project** reads a JSON file of at most **2 MB**, checks its format/version and notebook array, then requests confirmation. Import **replaces** current saved notebook, calculator history and graph settings; save your existing project first. The importer accepts legacy version 1 backups and version 2 backups, migrating version 1 to version 2 in memory without dropping supported workbook, formula, graph or notebook fields. New exports use version 2. Before confirmation, it validates notebook entries, calculator history, custom functions, graph datasets, table dimensions and cell sizes, and curve-fit preferences; a present Data Tables workspace must contain 1–20 sheets (the workspace always keeps at least one), while legacy projects that omit the `tables` object remain supported. Unsupported versions, malformed structures and files larger than 2 MB are refused without changing the project. A restore-stage exception triggers a best-effort rollback to the previous in-memory project. Browser storage quota errors or a second failure during rollback cannot be guaranteed recoverable; save an independent backup before importing.

### Custom functions in project backups

Each saved custom function has a case-insensitively unique name, 1–6 distinct argument identifiers and an explicit `formula` or `python` type (older entries without a type remain formula-compatible). The editor-reserved names `sin`, `cos`, `tan`, `sqrt`, `min`, `max`, `log`, `exp`, `abs`, `sum`, `if` and `pow` are rejected case-insensitively. Formula functions require a nonblank expression. Python functions require source containing a matching `def function_name(...)` declaration; source is stored as user-authored code and is **not executed during import**. Python syntax, runtime behavior and finite-real return values are checked only when the function is explicitly run in the isolated Pyodide worker. Import validation rejects malformed entries before confirmation and does not change the active project. The exposed custom-function restore API applies the same entry limits and reserved-name checks to its complete input list before replacing live functions or localStorage; a malformed direct restore is rejected atomically.

## Privacy and synchronization

Project files are saved on the user's device through browser downloads. The app has no login, cloud project synchronization or server storage. SymPy library files load from a CDN, while math computations execute locally.

[Architecture](ARCHITECTURE.md) · [Backup troubleshooting](TROUBLESHOOTING.md)

## Graph datasets in project backup

Version 1 projects now optionally include `graph.dataset`:

```json
{"name":"samples.csv","headers":["x","y","z"],"rows":[[0,1,2],[1,2,3]],"x":"0","y":"1","z":"2","style":"points"}
```

Graph state remains backward compatible: a missing dataset imports as no plotted data. A present dataset must contain 2–32 columns (each name at most 100 characters) and 1–6,000 rows, matching the live Graph importer. Its persisted X/Y axes (and Z in 3D) must have at least one row with finite decimal/scientific coordinates; empty or unrenderable datasets are rejected before confirmation rather than failing during restore. **Save project** retains imported rows and mappings. The optional `extra` field stores up to 20 additional series; each entry contains a bounded name, a table with 2–32 headers and 1–6,000 rows, and a mapping with distinct X/Y columns plus a valid optional 2D/3D mode, Z column for 3D, and `points`, `line` or `grid` style. Axis selectors in both primary datasets and overlays must be bounded base-10 integer indices (numbers or decimal integer strings); hexadecimal, binary, octal and exponent-form strings are rejected rather than coerced to another column. Overlay headers must be nonblank and unique after trimming and case-folding, matching primary Graph datasets. Each overlay must contain at least one numeric point for its selected axes. Malformed, over-limit or unrenderable overlays are rejected before import instead of being silently truncated or dropped. Legacy projects that omit `extra` remain supported. See [Data import](DATA_IMPORT.md).


## Primary Graph dataset mappings

A saved Graph dataset may omit its legacy `x`, `y`, `z` and `style` selectors; those projects retain the historical header-based defaults. When selectors are present, each axis must be a valid nonnegative safe-integer column index (number or a bounded base-10 integer string with optional surrounding whitespace or leading plus). Radix-prefixed and exponent-form strings, fractional/negative values, and overlong raw strings are rejected. X and Y must differ; a saved 3D graph must also use a distinct Z column. A saved graph mode must be `2d` or `3d`, and an explicit style must be `points`, `line` or `grid`. Invalid saved selectors are rejected before import confirmation rather than silently replaced with default columns. In 2D, the stored Z selector may overlap X or Y because it is dormant until switching to 3D.


## Saved curve-fit preferences

The optional `fit` object stores only the Curve fitting panel's selected model, polynomial degree and last generated graph equation. The model must be one of `none`, `linear`, `poly`, `exp`, `log`, `power` or `gaussian`; the degree is the string `2` through `6`; and `lastEquation` is a string of at most 2,000 characters. Missing, null or empty legacy selectors retain the existing defaults (`none` and `2`). Invalid types, unknown selections and overlong equations are rejected before project confirmation, so malformed fit preferences cannot silently clear or replace other workspace state. The project importer validates the complete state before calling the Curve fitting UI restore hook.

## Saved Matrix drafts

A present `matrix` object stores the Matrix workspace draft. Its A and B row/column dimensions must each be 2 or 3; A, B, RHS and weights arrays must match those dimensions. Each draft entry is a string of at most 80 characters. An empty string is allowed for an unfinished cell; nonempty values must use decimal/scientific notation, convert to a finite number, and have absolute value no greater than `1e12`. Radix-prefixed values, non-finite exponents and values outside the solver input bound are rejected. Version 1 projects that omit the optional Matrix object remain supported. Both project migration and the directly exposed Matrix restore API enforce the same numeric bounds; direct restore validates the complete draft before changing any grid input.


## Data Tables nested state version

The optional `tables` project object contains a nested Data Tables state. Its explicit `version` must be the supported integer `1`; legacy backups that omit the nested version remain accepted. Unknown, null or wrongly typed explicit versions are rejected before project confirmation, rather than being silently interpreted using the current v1 restore rules. The nested workbook must also contain at least one uniquely identified sheet when a selection is present, and `selected` must reference an existing sheet ID.


## Saved symbolic-solver controls

The optional `solver` object stores the Equation workspace expression and selector state. When present, `operation` must be one of `auto`, `expand`, `simplify`, `factor`, `solve`, `system`, `differentiate`, `integrate`, `limit`, `numeric`, `laplace`, `inverse_laplace`, `fourier`, `inverse_fourier`, `ode` or `pde`. The engine must be `auto`, `sympy` or `offline`; the limit direction must be `+-`, `-` or `+`. The saved variable is bounded to 24 characters and, when nonempty, must match the Equation solver's identifier syntax: a Unicode letter followed by Unicode letters, ASCII digits or underscores. The approach point is bounded to 80 characters, matching the live input controls. The expression remains bounded to 12,000 characters and optional ODE initial conditions to 160 characters.

Legacy projects may omit individual solver fields, and empty selector strings retain the workspace's existing defaults. Unknown explicit selector values and overlong control values are rejected before confirmation rather than silently becoming an empty selection or a default during restore. Rejection preserves the previously active project state.


## Saved Engineering Toolbox filter

The optional `engineering` project object stores the selected discipline and search query. `discipline` may be empty (all disciplines) or exactly one current stable ID: `physics`, `mechanical`, `electrical`, `electronics`, `fluids`, `aerospace`, `control`, `gnss` or `signals`. `query` must be a string of at most 200 characters. These IDs are checked against the canonical Engineering catalog by regression tests. Legacy projects that omit the object, or store it as `null`, remain supported. Unknown IDs, malformed types and overlong queries are rejected during schema preflight before the import confirmation prompt or any workspace restoration, rather than failing late and relying on rollback.

