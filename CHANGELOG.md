## 2026-10-23 — Advanced mathematics and contextual interface

- Linear, polynomial, exponential, logarithmic, power and Gaussian regression from Data Tables, including fitted graph overlays, R², RMSE and sample counts.
- Forward/inverse Laplace and Fourier notation and SymPy calculations.
- ODE/PDE analytical solution options via SymPy dsolve/pdsolve (limited supported classes).
- 72 additional physics equations in six organized categories.
- Floating Symbols/Examples/Options/Help menus and collapsible advanced settings.
- Added advanced math regression tests, source module and documentation.

## 2026-10-23 — Data Tables and data-driven charts

- Fifth workspace with multiple editable spreadsheet-style tables, column editing, formulas, row filter/sort, and browser-backed project persistence.
- Relational INNER/LEFT/RIGHT/FULL JOIN, UNION ALL/DISTINCT, INTERSECT, EXCEPT, all producing new tables.
- CSV/TSV/JSON import and CSV/JSON export moved into Data Tables; old chart importer remains as an advanced mapping control there.
- Cross-workspace plots of X/Y/Z data plus grouped bar and pie charts.
- About and README contain author/contact; MIT license added.
- Browser tests, standalone HTML source and developer build script.

# Changelog

Changes are documented in functional groups; historical version numbers are not reconstructed where no tagged release is available.

## 2026-10-23 — CSV and JSON imports for graphing

- Import local CSV, TSV and JSON numeric tables into the 2D and 3D Graph workspace.
- Added X/Y/Z mapping, row preview, scatter/connected-line style, complete-grid mesh overlay and Fit axes to data.
- Data overlays equation curves/surfaces and is preserved in exported project JSON.
- Added sample datasets, data import documentation and CI browser smoke coverage.

## 2026-10-23 — Connected workspace footer layout

- Moved the shared Working equation/Connected Workspaces panel from the top to the bottom of every workspace tab.
- Kept exactly one shared panel and preserved expression state, project save/load, calculator, solver and graph routing.
- Sending an equation to another tool now scrolls to the destination above the footer.
- Added desktop/mobile layout regression tests.

## 2026-10-23 — 3D constrained-curve graphing

- Plot `y=f(x)` together with `z=g(x,y)` as a highlighted 3D curve on the surface.
- Support uppercase `Y`, `×` multiplication, multiline shared workspace input, and existing multi-surface plots.
- Add Chromium regression coverage and graphing documentation.

## 2026-10-23 — Initial GitHub publication and documentation

- Published the connected single-page HTML mathematical application as `index.html`.
- Four interactive workspaces: calculator, equation editor, symbolic solver, 2D/3D graphs.
- Shared working equation, source dropdown, cross-workspace transfer, notebook and project JSON backup.
- Browser-executed SymPy with Pyodide CDN download for advanced operations.
- Mathematical input library, live math notation, Python snippets, LaTeX and Word export, PNG graph export.
- Added full user/developer documentation, static and browser smoke tests, CI and Pages deployment workflow.

## Known limitations

See `docs/FEATURES_AND_LIMITATIONS.md`. In particular, the built-in offline solver is not a complete CAS; SymPy download and hosted deployment must be validated in the target browser/environment.
