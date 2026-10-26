## 2026-10-26 — Hourly development automation and delivery controls

- Added persistent `AGENTS.md` contract and living five-feature plan for autonomous hourly work toward the 26-Oct feature/gap inventory.
- Established `dev` as the sole new-development branch; `main` receives only validated promotions through pull requests.
- Changed full Quality Actions to run on pushes to both `dev` and `main`, and on pull requests to `main`.
- Added conservative main-only Actions cleanup for obsolete legacy branches after verifying branch commits are already on main, the branch is unprotected, and there is no open PR; failures preserve branches instead of losing unique work.
- Added tests validating the CI and branch-hygiene delivery contract. Branch protection still requires GitHub administration privileges for enforcement.

## 2026-10-23 — Context menus, Calculator BIN/HEX, and symbol routing

- Added contextual commands across five workspaces and their editable surfaces, with keyboard and touch access.
- Added copy/cut/paste, row/column/table modification, sort/filter and graph/image commands in right-click menus.
- Moved redundant Add Row shortcut to table menus/context options; retained visible discoverable primary controls.
- Added DEC/BIN/HEX input radix, BigInt standalone base conversion, and safe-integer bitwise functions.
- Fixed Math Library insertion to target Calculator's input when Calculator is selected.
- Added context-menu help, source module and browser regression tests.

## 2026-10-23 — Numerical methods and Python Data Tables

- Added real nonlinear root searches, damped Newton systems, 1D heat/Poisson finite-difference methods, numerical output tables, and graph routing.
- Calculator and editor now share numeric differentiation, definite integrals, finite sums and finite products; calculator also supports scalar variable assignments.
- Reorganized Data Tables into Table, Filter, Combine, Files and Python submenus, with non-destructive advanced numeric/text column filters.
- Added on-demand browser Python/pandas worker, captured output and import of returned DataFrames as new tables, plus runtime safeguards and explicit limits.
- Added documentation, browser/numerical regression tests and build integration. No claim of general numerical PDE support or verified first-use CDN behavior.

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
