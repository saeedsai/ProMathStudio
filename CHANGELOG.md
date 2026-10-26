## 2026-10-26 — Bounded matrix RREF and rank (PR #15 release)

- Added offline scaled-pivot RREF and numerical rank for 2×2 to 3×3/rectangular real matrices, row-relative `1e-12` threshold, and Calculator UI/editor handoff.
- Added reference/near-singular/scale-disparity/invalid/UI Playwright regression and required Quality CI step. Dev Quality 40364677757, PR Quality 40364921754, main Quality 40365233145 and Pages 40365232944 all passed; independent hosted interactive smoke unavailable.

## 2026-10-26 — Matrix A/B arithmetic (PR #14 release)

- Added independently sized second matrix grid, offline real addition/subtraction/multiplication, dimension checks and finite validation.
- Both grids invalidate stale results; output transfers to Equation Editor. New focused browser regression and required Quality CI step. Dev Quality 40359705677, PR Quality 40361385356, main Quality 40361638533 and Pages 40361638361 passed; hosted interactive smoke remains unverified.

## 2026-10-26 — Bounded symbolic limits (dev candidate)

- Added a SymPy Limit operation with approach-point and left/right/both direction controls, project settings and a `sin(x)/x` sample.
- Reuses safe AST worker; validates real constant points, rejects free parameters and complex/equality/matrix inputs, and reports nonexistent or oscillatory limits.
- Added a focused reference/UI regression and required Quality CI gate. PR, main CI and Pages verification pending.

## 2026-10-26 — Spreadsheet structural reference integrity (dev candidate)

- Insert/delete rows or columns through the toolbar or context menu now rewrite local and cross-sheet A1-style formula references, preserving `$` anchors and explicit `#REF!` for deleted cells.
- Fixed context-menu first-row off-by-one index; extended the safe numeric formula evaluator to accept anchored cells/ranges and propagate deleted-reference errors.
- Added focused Playwright structural/reference/persistence regression to required Quality CI. Sorting formula-linked sheets and automatic range shrinking remain separate gaps; release requires verified CI, PR and Pages deployment.

## 2026-10-26 — Python custom function composition in Calculator (PR #10 release)

- Resolve nested Python custom-function AST calls asynchronously via the existing isolated Pyodide worker, then evaluate surrounding arithmetic using the safe Calculator numeric AST.
- Preserve direct calls, short-circuit conditional branches, finite real argument/result validation, a 16-call limit, 60-second per-call timeout, and stale-worker cancellation.
- Added focused Playwright worker-mock regression and required CI step; actual Pyodide CDN execution remains unverified until online QA. Released via PR #10: dev push 40345246719, PR 40345588610, main Quality 40346260037 and Pages 40346262438 passed; live hosted interactive/CDN execution still unverified.

## 2026-10-26 — First-order RK4 ODE (development increment)

- Added a bounded, offline fourth-order Runge–Kutta initial-value solver for scalar real y'=f(t,y), with fixed interval, initial value, 4–1000 steps, finite-value guards and clear error handling.
- Added UI under Numerical methods, Data Tables output and 2D graph routing, deterministic standalone bundle integration, structural source consistency and focused Playwright reference/error/round-trip tests.
- This does **not** implement adaptive/stiff methods, vector systems, events or general ODE/PDE solving. Release pending exact-head full CI, verified dev-to-main PR and Pages deployment.

## 2026-10-26 — Small-matrix calculator (development increment)

- Added editable 2×2, 2×3, 3×2 and 3×3 real matrix grid under Calculator, with determinants and inverse on square matrices and transpose on any supported grid.
- Partial-pivoting elimination, Gauss–Jordan inversion, scaled singularity threshold, finite-value validation and inverse residual verification, with ability to transfer results to Equation Editor notation.
- New standalone `src/matrix-tools.js` included in `index.html` via `scripts/build.py`, structural bundle test, dedicated Playwright matrix regression in required CI; described limits in `docs/MATRIX_CALCULATOR.md`.
- Does **not** include arbitrary-dimensional matrix algebra, multiplication, eigen/SVD or complex matrices. Do not mark released until required green PR/main CI and Pages deploy evidence.

## 2026-10-26 — Nonlinear symbolic equation systems (dev milestone)

- Added **Auto / Linear only / Nonlinear polynomial** modes to the simultaneous equation UI.
- Auto preserves SymPy exact linear/free-parameter systems; polynomial nonlinear systems of bounded degree and dimension are solved via `nonlinsolve`, including multiple real or complex solution tuples.
- Added explicit bounded-input and unsupported-expression errors with regression coverage for signed solutions, contradictory systems, the linear path, and degree limits.
- Tracked under P0-SYMBOLIC-SYSTEMS. Release status requires green exact-head CI plus dev-to-main PR and Pages validation.

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
