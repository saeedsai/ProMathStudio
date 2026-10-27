## Unreleased — high-precision expression keyboard workflow (2026-10-27)

- Added Ctrl+Enter / Cmd+Enter to evaluate the high-precision expression from the editor, with dedicated Playwright regression; no change to decimal computation or graph rendering. Pending CI and deployment.

## Unreleased — exactness indicators for high-precision decimal division (2026-10-27)

- Corrected decimal division metadata and expression status: exact terminating quotients (such as `1/8`) are reported exact, whereas rounded quotients (such as `1/3`) remain explicitly marked rounded. Verified through bounded integer cross-products; added focused browser regression cases and preserved all 2D/3D graph work. Pending full CI and Pages release.

## Unreleased — bounded high-precision expression evaluation (2026-10-27)

- Added offline Calculator → High precision decimal expressions with parentheses, unary signs and operator precedence, reusing exact BigInt decimal arithmetic and 16–80 digit half-even division at each division step. Bounded 120 tokens, 16 nested levels, 300-digit operands; rejects invalid tokens, implicit multiplication and division by zero without dynamic evaluation.
- Added focused Playwright numeric, negative, boundary, stale-result and mobile UI regression to mandatory Quality. Kept the modular source and standalone HTML synchronized; existing graph, fitting and ordinary Calculator behavior unchanged.

## Unreleased — bounded high-precision decimal arithmetic (2026-10-27)

- Added Calculator → High precision task with exact BigInt decimal addition, subtraction and multiplication, plus 16–80 significant-digit half-even division, bounded 300-digit operands and explicit errors.
- Added mandatory offline Playwright reference/negative/UI regression; synchronized modular and standalone builds. Standard Calculator binary64 behavior remains unchanged. Full precision roadmap remains partial until broader expression and mathematical function support and verified release.

## 2026-10-27 — Graph axes, multi-surface plots and camera controls (dev candidate)

- Direct Axes & grid access for editable X/Y/Z bounds, optional uniform spacing and labeled numeric 3D axes.
- Support z/z2/z3 3D surface definitions on separate lines. Preserve user-written 2D and 3D expressions and ranges when switching graph modes, plotting tables or resetting the view.
- Pan using Pan 3D, Shift/right-drag, scroll zoom toward pointer, preserve camera offset in project state. Add mandatory browser regression; release gates pending.

## 2026-10-27 — Curve-fit residual diagnostics (dev candidate)

- Added R²/RMSE/MAE/SSE and per-point measured/predicted/residual diagnostics for bounded 2D curve fits. Download a safe numeric CSV without modifying source tables. Disable export before a valid fit, after clearing, or after failed refit.
- Added `tests/smoke_fit_diagnostics.py` numerical/reference, invalid-input and Playwright CSV download coverage; mandatory Quality step. Release requires exact dev/PR/main Quality and Pages verification.

## 2026-10-27 — XLSX formula token boundary correction (PR #31 released)

- **UI-TASK-RESTORE (dev candidate):** Remember the last selected task independently for each of the five workspaces during the current page session; preserve the correct active button, description and form when returning. Adds a focused desktop/mobile browser regression and mandatory Quality gate. No localStorage/project schema change.
- **UI-PROGRESSIVE-WORKSPACES (dev candidate):** Task-first navigation in five workspaces, optional calculator display/history, variable assumptions, graph axes/table chart and generated Python forms collapsed until selected; retains existing mathematical engines. Adds desktop/mobile Playwright regression and mandatory CI coverage.
- **Released via PR #32 (2026-10-27):** selected-variable SymPy real/positive/negative/integer assumptions, restricted scalar solve, contradiction rejection, validated project persistence and new worker/browser regression. Dev, PR and main Quality passed; GitHub Pages deployment succeeded for main `91bbf1cc3016c7b53a3142b44eb39bedb2270f7e`.

- Corrected XLSX import/export row-reference rewriting to preserve numeric function names such as LOG10/ATAN2, scientific notation (1E3), longer identifiers and quoted literals, while continuing to shift real cell and quoted-sheet references.
- Added a dedicated browser regression `tests/smoke_xlsx_formula_tokens.py` and mandatory Quality step; synchronized both modules with the standalone HTML bundle. Exact dev Quality 40486708265, PR #31 Quality 40488048299 and main Quality 40488465426 passed all 41 steps; Pages 40488463589 succeeded for main 6e50b82b203d9233a2fcacd6c4dd829e2eb59a3c.

## 2026-10-27 — Bounded offline XLSX import and transactional round-trip (PR #31 released)

- Added ZIP central/local-header, CRC and decompressed-size validation; supports stored/DEFLATE workbooks with one or two sheets, shared/inline strings, numeric values, formulas and Excel header-row reference translation. Rejects external links, unsafe paths, malformed XML, oversized/duplicate entries and unsupported workbook parts.
- Added replacement confirmation and rollback-safe Data Tables import UI, new `src/xlsx-import.js`, synchronized standalone HTML, `tests/smoke_xlsx_import.py`, mandatory Quality step and documentation. Released via PR #31 with exact-head dev, PR and main Quality passing 41 steps, and Pages/branch cleanup succeeded; independent interactive hosted Pages smoke remains unavailable.

## 2026-10-27 — Bounded offline two-sheet XLSX export (PR #30 released; main Quality and Pages green)

- Added dependency-free OpenXML/ZIP STORE export of one or two Data Tables sheets with numbers, text, blanks, formulas, quoted sheet references and header-row reference translation. Enforced size, name, XML control-character and row/column limits.
- Added `src/xlsx-tools.js`, synchronized standalone HTML, `tests/smoke_xlsx_export.py`, mandatory Quality step and Data Tables documentation. Exact dev Quality 40477182475, PR #30 Quality 40477470396, main Quality 40477823491, Pages 40477822871 and branch cleanup 40477823537 all succeeded for main `83e52f0a4c46cca13d9a03ad38801599a830762a`. Import and secure transactional round-trip remain pending; hosted interactive Pages verification unavailable.

## 2026-10-27 — Brent-Dekker bracketed root refinement (PR #29 released; exact main Quality and Pages green)

- Added bounded offline real root refinement with residual validation, strict input limits, browser UI and one-row Data Tables export; previous root search remains intact.
- Added `tests/smoke_root_brent.py` to mandatory Quality; synchronized `src/brent-tools.js` and standalone `index.html`. Local JS numerical reference checks passed; exact dev Quality 40470847711, PR #29 Quality 40471141184, and main Quality 40472294062 passed all 38 steps; Pages 40472293001 and branch cleanup 40472294108 succeeded for main `ebd8932e19cae5168742cd8412207277e04121d5`. Hosted interactive Pages smoke was unavailable (`DisabledError`).

## 2026-10-27 — Bounded offline 1D golden-section minimization (PR #28 released; main Quality and Pages green)

- Added a finite-interval, unimodal scalar minimizer with safe numeric expression evaluation, endpoint comparison, tie/flat handling, configurable tolerance and bounded iteration budget.
- Added Solver numerical UI, stale-export invalidation, Data Tables result handoff, new Playwright numerical/UI regression and mandatory Quality gate. Kept standalone index synchronized with `src/minimize-tools.js`.
- Local isolated Node references and stub-browser UI passed; exact dev Quality 40465011424, PR #28 Quality 40465273067 and main Quality 40465533827 each passed 37 steps; Pages 40465532792 and branch cleanup 40465533622 succeeded on main `c50d3377213cb3961732623624197894adcf9ed2`. Independent hosted interactive Pages smoke unavailable (DisabledError).

## 2026-10-27 — Bounded barycentric polynomial interpolation (PR #27 released; exact main Quality and Pages green)

- Added offline global polynomial interpolation for 2–16 nodes, normalized barycentric weights, exact-knot preservation, conditioning guards and 1,000 in-domain queries; linear/PCHIP modes remain unchanged.
- Added polynomial method selection, Data Tables and Graphs handoff, numerical and browser regression tests, mandatory CI step, standalone HTML synchronization and mathematical limitations documentation.
- **RELEASED via PR #27:** exact dev Quality 40458678021 and PR Quality 40458884668 passed 36 steps each; merged main 47acdcb4079c5f113d0b8abc3bf8b9ea0f12e512. Main Quality 40459125293, Pages 40459124441 and cleanup 40459125216 succeeded. Hosted interactive Pages smoke unavailable (DisabledError); this does not certify live-browser behavior.

## 2026-10-27 — Shape-preserving cubic interpolation (PR #26 released; exact main Quality and Pages green)

- Added bounded offline PCHIP with monotone cubic Hermite slopes, exact-knot preservation, two-point linear fallback, method selector and Data Tables/Graphs export; linear mode remains default.
- Added tests/smoke_interpolation_pchip.py reference, monotonicity, invalid-input, stale-export and browser regression as mandatory Quality step; synchronized standalone index.html.
- Repaired existing linear browser regression's signature assertion to reflect the added optional method while retaining the linear-default and source-bundle assertions. Initial dev Quality 40453273799 failed at this outdated assertion; rerun exact-head checks after this repair.
- P1-NUMERIC-INTERPOLATION-PCHIP RELEASED via PR #26: exact dev Quality 40453415941 and PR Quality 40453668805 passed 35 steps each, including both interpolation regressions. Merged normally to main 35fe1443933b24edfd5c2c89ff2549b98667bcbb; main Quality 40454600848, Pages 40454600491 and branch cleanup 40454600839 succeeded. Initial dev CI 40453273799 failed on an outdated test source signature and was repaired without dropping behavioral assertions. Hosted interactive Pages smoke remains unavailable (site fetch inaccessible).

## 2026-10-27 — Bounded offline 1D linear interpolation (PR #25 released; main Quality and Pages green)

- Added a native piecewise-linear interpolator with strict sorted sample validation, finite-domain checks, active Data Tables x/y loading, and Data Tables/Graphs handoff.
- Fixed exact-knot precision loss for sample values with very different magnitudes and repaired an embedded-JavaScript newline escaping failure in the browser regression. Added exact-knot and parser regression coverage.
- Added focused Playwright regression `tests/smoke_interpolation_linear.py` to mandatory Quality CI and synchronized the standalone HTML build. Exact dev Quality 40447298379 and PR #25 Quality 40447592140 passed (34 steps); merged main `170849cec91a7da8932e7a08bd339a76902c17fd`, Pages 40447830774 succeeded. Main Quality 40447830885 passed all 34 steps; Pages 40447830774 and cleanup 40447830999 succeeded for exact main. Hosted live interactive smoke remains unavailable.
- Scope excludes extrapolation, cubic/spline interpolation, multidimensional interpolation and uncertainty estimates.

## 2026-10-27 — Bounded adaptive Simpson quadrature (PR #24 released; main Quality and Pages green)

- Added offline finite-interval adaptive Simpson integration with tolerance and evaluation budget controls, local error estimate, bounded subdivision and non-finite rejection. Existing fixed-step Calculator integration and numerical methods are preserved.
- Added focused Playwright reference/negative/budget/UI regression `tests/smoke_quadrature_adaptive.py` to mandatory Quality CI. Exact dev Quality 40441269844, PR #24 Quality 40441540706, main Quality 40441796530 (33 steps) and Pages deployment 40441795972 passed for main `4bc5287d0e20d906ee7c8278310480a9ef9120c8`; hosted interactive smoke unavailable.
- Scope excludes certified global error bounds, singular/improper, highly oscillatory and multidimensional integrals.

## 2026-10-27 — Coupled two-state RK4 IVP (PR #23 released; exact main Quality and Pages green)

- Added bounded offline two-state first-order RK4 with derivative expressions for y and z, separate initial conditions, safe numeric AST evaluation and finite-state checks. Data Tables receives t/y/z; Graphs plots y(t).
- Added harmonic-oscillator and driven-system numerical references, fourth-order refinement, invalid-input and browser export regression in `tests/smoke_ode_system.py`, registered as a required Quality step. Exact dev Quality 40435790677, PR Quality 40436030986, main Quality 40436220425 and Pages deployment 40436220120 succeeded for PR #23 (main e87099356b4ae9b650106650f6a40ba2897c3028); hosted interactive smoke remains unverified.
- Scope excludes stiff, backward, adaptive vector, higher-dimensional and certified-global-error ODE systems.

## 2026-10-27 — Adaptive scalar ODE RK45 (PR #22 released; main Quality and Pages green)

- Added bounded offline Dormand–Prince 5(4) scalar IVP integration with local error tolerance, accepted/rejected step diagnostics, maximum-attempt/underflow checks, and Data Tables/Graphs output.
- Retained existing fixed-step RK4 as default. Added RK45 method/tolerance/attempt controls, a focused Playwright regression and mandatory Quality gate. Isolated Node references for y'=y passed with tightening tolerance; exact dev Quality 40430429819, PR Quality 40430435679, main Quality 40430673781 and Pages 40430673177 passed for PR #22 (main 9217036aa68751813fd68c60c5e1ce633b70edea). Hosted interactive smoke remains unverified.
- Scope excludes stiff, vector, event-driven, backward and certified-global-error ODE solvers.

## 2026-10-27 — Nested spreadsheet IF evaluation (PR #22 released; main Quality and Pages green)

- Corrected nested IF evaluation in Data Tables: short-circuit unselected branches (including #REF!, cycles and divide-by-zero), allow IF inside arithmetic and aggregates, and parse top-level comparisons without confusing nested conditions or adjacent IF arithmetic.
- Added `tests/smoke_sheet_nested_if.py` with numeric, malformed, cross-sheet, cycle, UI and project save/reload coverage; made it mandatory in Quality CI. Offline isolated Node reference checks passed (7 positive and 4 negative); exact dev Quality 40430429819, PR Quality 40430435679, main Quality 40430673781 and Pages 40430673177 passed on main 9217036aa68751813fd68c60c5e1ce633b70edea. Hosted interactive smoke remains unverified.
- Scope: numeric spreadsheet formulas only; no Excel-compatible full expression grammar or XLSX import/export.

## 2026-10-27 — Bounded QR least-squares 3×2 solver (PR #21 released; exact-main Quality and Pages green)

- Added offline full-column-rank 3×2 real least squares using existing QR, residual and orthogonality diagnostics, RHS grid, and Equation Editor transfer.
- Added focused reference/negative/UI Playwright regression, required CI step and standalone bundle assertion. Exact dev Quality [40416944333](https://github.com/saeedsai/ProMathStudio/actions/runs/40416944333), PR Quality [40417169197](https://github.com/saeedsai/ProMathStudio/actions/runs/40417169197), main Quality [40418521710](https://github.com/saeedsai/ProMathStudio/actions/runs/40418521710) and Pages [40418521555](https://github.com/saeedsai/ProMathStudio/actions/runs/40418521555) passed. PR #21 merged to main `17f19af1a1a6179859a31163f3fbaf0855865471`. Independent hosted interactive smoke unavailable.

## 2026-10-26 — Project schema v2 release closeout

- PR #20 main `c32d486287ec2d6c13a872261fff83f94976ab7b` [Quality 40409820911](https://github.com/saeedsai/ProMathStudio/actions/runs/40409820911) and [Pages 40409819690](https://github.com/saeedsai/ProMathStudio/actions/runs/40409819690) succeeded. Bounded project-schema v2 is RELEASED with workflow-verified deployment; hosted interactive smoke remains unverified.

## 2026-10-26 — Project schema v2 and import rollback (PR #20 released)

- Export version-2 JSON project backups; accept and migrate legacy version-1 backups without dropping supported data.
- Validate notebook, history, custom functions, graph datasets and table dimensions before confirmation or mutation; reject future versions and malformed/oversize files.
- Snapshot current project and reapply it on a restore-stage failure; this is best-effort and cannot guarantee recovery from storage failures. Add dedicated browser rollback and migration regression to required Quality CI.
- **Released:** dev/PR Quality, main Quality 40409820911 and Pages 40409819690 passed on main `c32d486287ec2d6c13a872261fff83f94976ab7b`.

## 2026-10-26 — Thin QR decomposition (PR #19 released; exact-main Quality and Pages green)

- Added offline 2×2, 3×2 and 3×3 real economy QR with reorthogonalization, rank refusal, reconstruction/orthogonality diagnostics and Q/R editor transfer.
- Added a dedicated Playwright numerical regression and required Quality gate. Dev Quality 40400347060 and PR Quality 40400623469 passed; PR #19 merged to main a97f5f41, Pages 40401065476 succeeded. **Main Quality 40401065297 passed all 27 steps and Pages 40401065476 succeeded on a97f5f41.** Hosted interactive smoke unavailable.

## 2026-10-26 — Pivoted small-matrix LU decomposition (PR #18 released; exact-main Quality and Pages green)

- Added real 2×2/3×3 full-rank P·A=L·U decomposition with scaled row pivoting, permutation tracking, singular/near-singular refusal and row-relative reconstruction residual.
- Calculator shows P, L, U and transfers the chosen factor to Equation Editor. Added dedicated browser/numerical regression, bundle assertions, mandatory Quality workflow gate and documentation. Exact dev Quality 40391371254 and PR Quality 40391373319 passed; PR #18 merged to main a03e02de. Pages 40391704935 succeeded; main Quality 40391737573 passed all 26 steps and Pages 40391704935 succeeded for exact main; duplicate main run 40391704792 still pending, live interactive smoke unavailable.

## 2026-10-26 — Spreadsheet range deletion integrity (PR #18 merged; main Quality pending)

- Row/column deletion shrinks surviving same-sheet and cross-sheet aggregate ranges, preserving absolute anchors; fully removed ranges produce #REF! while scalar references retain existing behavior.
- Qualified SUM/AVG/MIN/MAX/COUNT ranges now evaluate. Cross-sheet ranges also participate safely in stable sorting, with atomic rejection if their rows would become noncontiguous. Added focused browser regressions, updated structural expectations and mandatory Quality gate. Candidate dev/PR Quality green; merged PR #18 and Pages deployment succeeded; main Quality 40391737573 passed; duplicate main run 40391704792 pending.

## 2026-10-26 — Spreadsheet row sorting with reference integrity (dev candidate)

- Stable sorting remaps same-sheet and cross-sheet formulas, including anchored references; contiguous ranges retain their referenced cells and noncontiguous ranges abort without mutation.
- Added `tests/smoke_sheet_sort_references.py`, required CI step and docs. Await exact-head Quality, PR, main and Pages verification.

## 2026-10-26 — Small real linear systems Ax=b (PR #16 released)

- Added offline 2×2/3×3 square Ax=b solver with scaled partial pivoting, nonunique/inconsistent diagnostics and row-relative backward residual validation. RHS grid, solve action, stale-result invalidation and Equation Editor column-vector transfer included.
- Added `tests/smoke_matrix_solve.py` browser/reference regression, required Quality CI step and static bundle assertion. Dev Quality 40373781557, PR Quality 40374084354, main Quality 40374484994 and Pages 40374485244 passed for the verified release. Hosted interactive smoke remains unverified.

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
