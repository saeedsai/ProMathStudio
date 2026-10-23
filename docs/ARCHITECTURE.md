# Architecture and implementation map

## Delivery model

- Entry point: repository-root `index.html` (CSS, HTML, JavaScript and embedded Python in one document).
- No JavaScript package build/bundler or backend is required.
- Math preview: client-side AST parser → MathML DOM; LaTeX and Python representations are generated from parsed input.
- Calculator: local AST numerical evaluator, including complex values.
- Offline CAS: local polynomial/rational operations.
- Full CAS: Pyodide Web Worker → SymPy Python runtime; payload is an AST-derived JSON job (not arbitrary Python eval).
- Graphing: local Canvas 2D with an AST-based function evaluator; 3D is a projected mesh that supports mouse interaction.
- Word: local DOCX package generation for editable Office Math elements.
- Connected hub: mediates editor/calculator/solver/graph state; browser storage + manual JSON project backup.

## Code layout inside index.html

| Section identifier/marker | Responsibility |
|---|---|
| `mathstudio-sympy-python` | Embedded Python/SymPy evaluator and guardrails |
| Main editor JavaScript | Tokenization, AST, math rendering, LaTeX, Word/export, notebook |
| CAS JavaScript | Offline transformations + Web Worker SymPy interface |
| `mathstudio-workspaces` | Calculator, tab navigation, canvas graphs |
| `mathstudio-connected-workspaces` | Shared working equation, result routing, project save/load |

Search these IDs in `index.html` rather than relying on static line numbers.

## Public integration surface (internal; not versioned API)

```javascript
window.MathStudio.parse(text);
window.MathStudio.latex(ast);
window.MathStudio.render(ast);
window.MathStudio.python(ast);
window.MathStudio.symbolic(/* app-specific args */);
window.MathStudio.advanced;
window.MathStudio.notebookBridge;
window.MathStudio.solverBridge;
window.MathStudio.bridge.transfer(destination, input, options);
window.MathStudio.bridge.export();
```

These are **internal** interfaces and can change. Verify call signatures in source before external integration. Do not expose evaluation functions to untrusted data without reviewing their permitted AST node set and parser guards.

## State and event flow

1. A user changes any workspace input. The bridge can mirror the current draft to the shared field.
2. A **Send to** action validates/selects an expression, switches destination, and updates that tool's input.
3. Calculator and CAS results dispatch browser custom events to the bridge, which surfaces recent results and routes individual roots.
4. Notebook changes persist to localStorage and can be selected from anywhere.
5. Save project serializes a versioned JSON snapshot; Open project validates format/version before restoring components.

## Security/availability choices

- SymPy loads from a hard-coded Pyodide v0.29.1 CDN URL in a Web Worker and imports the SymPy package.
- The embedded SymPy evaluator limits AST nodes and returned results; a browser can still become unresponsive on expensive algebra.
- Never treat arbitrary file imports as trusted; project restore is not a sandbox boundary.
- There is no server-held account, sync or database.
- Third-party code fetch is a supply-chain dependency when SymPy is loaded; use pinned versions, dependency review and CSP if deploying as a larger product.

[Development notes](DEVELOPMENT.md) · [Project format](PROJECT_FORMAT.md)

## Numerical mathematics and Python data-analysis module

`src/numerical-data.js` is embedded in `index.html` in the `promath-numerical-data` script after other math workspaces. It accesses the shared AST calculator via `MathStudio.advanced.numeric` and exposes pure numerical algorithms in `MathStudio.numerical` (nonlinear scalar roots, small systems, 1D heat and Poisson). The Data Tables menus move existing DOM elements without changing their IDs or event listeners. Filters hide displayed rows without editing the data source.

User-requested Python executes in a **separate Web Worker** with Pyodide and pandas, which needs a CDN on first use. Workbook data are copied to the worker; `result` DataFrames return as new tables. The worker has no DOM access, but arbitrary user Python is still potentially dangerous and may initiate network requests. No user-provided code runs automatically.
