- 2026-10-30 (MATH-ODE-RK45-OVERFLOW-035, dev QA): Adaptive RK45 now retries bounded intermediate-stage overflow with halved step, counts/report retries, preserves k1 hard failures and attempt/time-resolution bounds. Added Node numerical and mandatory Chromium/mobile regression; full CI and release pending.
- Control transient RK4 now reports optional step-doubling endpoint difference for up to 500 base steps, retaining original export and honest non-certified accuracy warning (dev QA pending).
- 2026-10-30 (CONTROL-TRANSIENT-TWO-STATE-033, dev QA): Added two-state Control transient trajectory for xdot=-Ax+b using existing coupled RK4, including forward/backward and singular-A references, strict numeric inputs, stale-export invalidation, Data Tables export and responsive UI. Added direct numerical test and mandatory Chromium regression. Release pending.
- 2026-10-30 (CI-ENGINEERING-SEARCH-REPAIR-034, dev QA): Corrected stale structural search assertion after all-term matching; [Quality 41083127664](https://github.com/saeedsai/ProMathStudio/actions/runs/41083127664) failed solely on obsolete `includes(q)` expectation. Retained all-term matching and added browser positive/negative regression. Exact new-head CI pending.
- Engineering Toolbox: search now matches multiple keywords in any order, preserving planned tool labels and offline support (UI-ENGINEERING-MULTIWORD-032; dev QA pending).
- 2026-10-30 (UI-ENGINEERING-SEARCH-031, dev QA): Engineering Toolbox search includes readable discipline display names, retaining canonical IDs, truthful planned status, offline parity, and browser/mobile navigation checks. Exact-head CI and deployment pending.
- 2026-10-30 (MATH-ODE-RK45-WORKLOAD-030, dev QA): Adaptive scalar RK45 reports longest consecutive rejected-step streak and warns on repeated rejections without claiming stiffness; adds exponential forward/backward numerical tests and mandatory Chromium mobile/error-recovery coverage. Exact-head CI and release pending.
- 2026-10-30 (UI-ENGINEERING-CATALOG-029, dev QA): Added Control Theory, GNSS Positioning and Signal Engineering to searchable Engineering Toolbox; truthful planned cards without fake actions, shared existing Control equilibrium route, source/bundle and Chromium regressions. Exact-head CI/PR/Pages pending.
- 2026-10-30 (ARCH-ENGINEERING-SHAPE-CODES-028, dev QA): Canonical solver registry rejects invalid 2x2/3x3 A dimensions and b vector sizes with structured INVALID_MATRIX_SHAPE / INVALID_VECTOR_LENGTH errors; added reference and recovery tests, standalone parity, exact release checks pending.
- 2026-10-30 (CONTROL-STABILITY-SYMMETRIC-027, dev QA): Added symmetric 2×2/3×3 Control perturbation stability action reusing Matrix Jacobi eigenanalysis, stable/unstable/marginal/near-zero-indeterminate classification, eigen residual and explicit equilibrium/nonsymmetric limitations. Added numerical and desktop/mobile browser regressions; exact-head CI/PR/Pages pending.
- 2026-10-30 (ARCH-ENGINEERING-CONTRACTS-026, dev QA): Canonical Matrix/Control solver registry now exposes immutable bounded input schemas, explicit physical-unit/full-rank assumptions and a nonthrowing structured execution result with stable registry error codes. Preserves existing throwing API and standalone bundle. New Node/Python numerical, negative and parity test plus extended Chromium browser regression; exact-head release verification pending.
- 2026-10-30 (UI-MATRIX-PROJECT-ROUNDTRIP-025, dev QA): Matrix calculator project backups now preserve A/B dimensions, cell drafts, right-hand side and weights; restore validates shape and bounded decimal strings, preserves keyboard focus, clears stale results, and supports older projects without Matrix state. Added schema and mandatory Chromium round-trip/mobile/rollback regression. Exact-head Quality and Pages release pending.
- 2026-10-30 (DATA-PROJECT-TABLE-FINITE-024, dev QA): Refuse nonfinite Data Table numeric cells on project import, including overflowing JSON number literals; preserve valid scalar cells, legacy migration and atomic rollback. Added Node/Python and Chromium regression coverage; exact CI/PR/Pages pending.
- 2026-10-30 (DATA-PROJECT-GRAPH-CELLS-023, dev QA): Reject nested object/array and nonfinite numeric cells in imported graph datasets; retain bounded valid scalar cells and v1 project migration. Added Node/Python regression with standalone parity. Exact-head CI, PR and Pages release pending.
- 2026-10-30 (MATH-ODE-RK45-STAGE-RESOLUTION-022, dev QA candidate): Warn when RK45 intermediate stage times collapse to current representable time at large epochs; count affected attempts/accepted steps, include failure context, preserve integration and exports. Added forward/backward one-ULP numerical and Chromium/mobile recovery regressions. Exact CI/PR/Pages pending.
- 2026-10-30 (UI-ENGINEERING-CATALOG-021, dev QA candidate): Added fifth Engineering Toolbox workspace with six discipline filters, searchable canonical entries, truthful available/planned labels and navigation to existing Matrix, Control and ODE tools without duplicate solvers or fake planned actions. Preserved offline bundle, original four workspaces and drafts; added source/bundle, keyboard, routing, search and mobile regressions. Exact dev CI/PR/main/Pages pending.
- 2026-10-30 (ARCH-CONTROL-EQUILIBRIUM-020, dev QA): Bounded Control equilibrium xdot=-Ax+b reuses canonical Matrix solver for 2×2/3×3, with residual diagnostics, stability/unit caveats, stale-result invalidation and responsive UI. New Node/Python and mandatory Chromium regression; exact-head CI/PR/Pages pending.
- 2026-10-30 (ARCH-ENGINEERING-SOLVER-REGISTRY-019, dev QA candidate): Added stable immutable runtime solver IDs for Matrix Ax=b and Inverse with strict input contract and metadata validation; both real UI buttons execute through the shared registry and existing scaled-pivot kernels. Added numerical, duplicate-ID, invalid/singular, standalone-parity and mandatory Chromium/mobile regressions. Cross-discipline toolbox UI is still planned; exact-head CI/PR/main/Pages pending.
- 2026-10-30 (UI-MATRIX-RESIZE-FOCUS-018, dev QA candidate): Preserve numeric-cell focus across Matrix A/B/RHS/weight grid rebuilds and clamp focus when dimensions shrink, without stealing focus from dimension selectors or altering surviving values. Added Node target/boundary and mandatory Chromium desktop/mobile regressions, standalone parity, and living roadmap update. Exact-head CI/PR/main/Pages pending.
- 2026-10-30 (UI-MATRIX-HOME-END-017, dev QA candidate): Added Home/End row-local and Ctrl+Home/End first/last-cell navigation across Matrix A/B/RHS/weight numeric grids. Matrix A labels now include matrix name. Preserved numeric values, arrows, Tab, all algorithms, transfer and offline bundle; added direct Node negative/target and mandatory Chromium mobile tests. Exact-head CI/PR/main/Pages pending.
- 2026-10-30 (UI-MATRIX-GRID-KEYBOARD-016, dev QA candidate): Added unmodified arrow-key focus movement in Matrix A/B/RHS/weight numeric grids, including 2×2/3×3 and single-column boundaries without accidentally stepping number values. Preserved Tab/modified shortcuts, input drafts, numerical algorithms, Equation Editor transfer and offline parity. Added Node target/boundary and mandatory Chromium keyboard/mobile regressions. Exact-head CI/PR/main/Pages verification pending.
- 2026-10-30 (UI-MATRIX-INPUT-GROUPS-015, dev QA candidate): Added collapsible Matrix B/RHS/weight sections, labeled Matrix A and operation-aware reopening without deleting input drafts. Preserved 16 actions and Equation Editor transfer; new structural, numerical, standalone and Chromium regression. Exact-head CI and promotion pending.
- 2026-10-30 (UI-MATRIX-CONTEXT-014, dev QA candidate): Split Matrix operation buttons from contextual Equation Editor result-transfer actions; show only the relevant LU/QR/Eigen/SVD selector for a successful calculation, hide all on edit/error, preserve 16 operations, factor choices and transfer. Added structural/parity and mandatory Chromium keyboard/mobile/transfer/error regression. Exact-head CI/PR/main/Pages pending.
- 2026-10-30 (MATH-MATRIX-CONDITION-GUIDANCE-013, dev QA candidate): Added heuristic κ∞ ≥ 1e8 numerical sensitivity guidance to 2×2/3×3 Ax=b and Inverse, explicitly distinguishing conditioning from residual and backward error. Reuses existing scaled-pivot solver; preserves singular recovery, editor transfer and offline parity. Added Node numerical/threshold/negative regression and mandatory Chromium two-consumer/mobile regression. Exact dev CI, PR, main Quality and Pages pending.
- 2026-10-30 (MATH-ODE-RK45-REJECTION-012, dev QA candidate): Added maximum rejected normalized local-error ratio, minimum rejected |Δt| and representable-time adjustment count to scalar RK45 diagnostics, including attempt-limit/underflow messages. Preserved adaptive acceptance logic, derivative guards, stale-export invalidation and offline standalone parity. Added Node stiff/nonstiff/reference/one-ULP/negative test `tests/test_ode_rk45_rejected_quality.py`, mandatory Chromium success/failure/recovery/mobile test `tests/smoke_ode_rk45_rejected_quality.py`, and numerical documentation. Local full checkout blocked by GitHub DNS; exact dev CI, PR/main Quality and Pages verification pending. The local-error ratio is not a global error guarantee.
- 2026-10-30 (MATH-ODE-RK45-STEP-QUALITY-011, dev QA candidate): Added minimum/maximum accepted absolute time-step and maximum accepted normalized embedded local-error ratio to scalar forward/backward RK45 output and UI, using actual rounded accepted steps (not rejected trials). Preserved existing local error acceptance, endpoint handling, stale export invalidation and offline standalone parity. Added Node numerical/reference/one-ULP/negative regression `tests/test_ode_rk45_step_quality.py`, mandatory Chromium success/failure/recovery/mobile regression `tests/smoke_ode_rk45_step_quality.py`, and updated numerical documentation. The ratio is an estimate, not a global error bound. Exact dev CI, PR, main Quality and Pages pending.
- 2026-10-30 (MATH-MATRIX-CONDITION-INF-010, dev QA candidate): Added infinity-norm condition number κ∞(A)=||A||∞·||A⁻¹||∞ to 2×2/3×3 Matrix Solve Ax=b and Inverse, reusing the existing scaled-pivot inverse. This is distinct from backward error and is not a forward-error guarantee. Valid solves retain editor transfer if the diagnostic is unavailable; singular and invalid input behavior unchanged. Added Node numerical/negative/scale/parity regression `tests/test_matrix_condition_infinity.py` and mandatory Chromium two-consumer/mobile/error-recovery regression `tests/smoke_matrix_condition_infinity.py`. Source and standalone HTML synchronized. Preserved the full legacy `M.matrixTools` export after structural CI failures; new API is added by a separate assignment without weakening existing compatibility tests. Exact-head CI, PR, main and Pages pending.
- 2026-10-30 (MATH-MATRIX-SHARED-INVERSE-008, dev QA candidate): Reused the existing scaled-partial-pivot Ax=b numerical solver for 2×2/3×3 matrix inversion by solving against identity columns, removing duplicate Gauss–Jordan elimination. Retained inverse residual and singular checks, no input mutation, UI/Equation transfer and offline standalone parity. Added Node reference/scaled/singular regression `tests/test_matrix_shared_solve_inverse.py`, registered Chromium scaled inverse, error recovery and 390px mobile smoke `tests/smoke_matrix_shared_solve_inverse.py`. Direct V8 numerical/negative smoke passed; exact-head CI/PR/main/Pages pending.
- 2026-10-29 (MATH-MATRIX-STRICT-TYPES-007, dev QA candidate): Rejected coercible nonprimitive matrix and Ax=b RHS inputs (arrays, objects, boxed numbers, BigInts, symbols, booleans) before Number() conversion; preserved valid decimal/scientific inputs, finite magnitude bounds and scaled partial-pivot solve. Added direct 2×2/3×3 reference, negative, singular/inconsistent and standalone bundle parity regression `tests/test_matrix_strict_types.py`; source and standalone synchronized. Exact-head CI, dev→main PR, main and Pages release pending.
- 2026-10-29 (MATH-ODE-RK45-PROGRESS-006, dev QA candidate): Added RK45 attempt-exhaustion and floating-time-resolution failure diagnostics with last time, target, attempted step, attempts, accepted/rejected counts and tolerance. Retained the Dormand–Prince algorithm, forward/backward behavior and stale-export invalidation. Added Node reference/boundary regression and Chromium failure/recovery regression; synchronized standalone HTML. Exact-head CI/PR/Pages pending.
- 2026-10-29 (MATH-ODE-RK45-DIAG-005, dev QA candidate): Added stage-aware scalar RK45 derivative failure diagnostics (k1–k7, time, state), preserving bounded numerical behavior and stale table/graph export invalidation. Added Node reference/invalid/overflow and Chromium recovery/mobile regressions to mandatory Quality. Source and standalone bundle synchronized; exact-head CI, PR, main and Pages pending.
- 2026-10-29 (MATH-MATRIX-WLS-RHS-002, dev QA candidate): Hardened both QR least-squares operations to accept only finite decimal/scientific RHS values (numbers or strings), rejecting Number()-coerced hexadecimal/binary/octal literals, arrays and objects. Weighted fitting now rejects array/object weight coercion. Added focused numerical regression with 51 assertions covering reference coefficients, weighted SSE, malformed input, positive weight bounds, 1e-9/1e9 scaling and near-rank loss. Updated standalone HTML; exact-head CI, PR and Pages require verification.
- 2026-10-29 (release checkpoint): Weighted 3×2 least-squares UI and prior dev changes merged through PR #95 to main at 352c1dd8549beb8cb0707012b7bd466d1fcd25c1; dev/main Quality and Pages runs succeeded. Independent live-browser confirmation was not available.
- 2026-10-29 (dev QA candidate, MATH-MATRIX-WLS-UI-001): Exposed bounded 3×2 QR weighted least squares in the Matrix calculator with three editable relative observation weights, weighted residual diagnostics and Equation Editor transfer. Preserved unweighted least squares, added Chromium reference/invalid-input/mobile regression and CI gate; exact-head CI, PR and Pages release require verification.\n- 2026-10-29 (dev QA candidate): Fixed scalar adaptive RK45 false step underflow at large time epochs and early endpoint snapping. RK45 now uses representable time increments and the actual rounded step, preserves forward/backward integration, and rejects impossible time-resolution tolerances explicitly. Added numerical/reference/static and Chromium UI/table/mobile regressions; exact-head CI/Pages pending.
- 2026-10-29 (dev QA candidate): Backward-time coupled two-state RK4, reverse oscillator and nonautonomous references, UI/table/graph regression, signed steps and forward compatibility; exact-head CI and release pending.
- 2026-10-29 (dev candidate; QA pending): Added signed-direction backward adaptive Dormand–Prince RK45 for scalar IVPs, preserving forward behavior, local-error rejection and ordered Data Tables/Graphs export. Added reverse exponential/nonautonomous reference, refinement/rejection, invalid-input and browser UI/mobile regression; coupled RK4 remains forward-only. No dependencies added.
- 2026-10-29 (dev candidate, CI/Pages pending): Enabled backward-time scalar fixed-step RK4 integration with signed step sizes, analytic reference/convergence tests, invalid-input checks, UI and Data Tables export. Adaptive RK45 and coupled RK4 remain forward-only; no new runtime dependencies.\n- 2026-10-29 (dev, full CI pending): Improved the Control Theory root-locus graph from unconnected sampled pole markers to continuous *sampled* branch trajectories using minimum-total-displacement pole assignment. Added guarded root-locus inputs, second/third-order reference checks, cancellation and invalid-input regressions, and a canvas path test (`tests/test_root_locus_tracking.py`). Near repeated poles and crossings remain approximate; no production deployment claimed.
- 2026-10-29 (dev, CI pending): Added mandatory Chromium Control Theory workbench regression covering Bode, Nyquist, root locus, Routh–Hurwitz, unity feedback, validation and responsive layout; integrated it into Quality workflow. This is a test/QA improvement, not a new controller algorithm. Deployment unverified.
- 2026-10-29 (dev, QA pending): Repaired 390px mobile workspace navigation overflow caused by unwrapped horizontal tabs in the computation-first redesign. The four workspace tabs now form a two-column responsive grid while preserving keyboard focus/activation. Added `tests/test_mobile_workspace_grid.py`; exact-head browser/Quality and production deployment remain unverified.
- 2026-10-29 (dev, pending exact-head CI): Repaired the app-startup JavaScript parsing regression caused by graph scripts inserted into the HTML-export literal; all inline executable scripts now parse. Added inline-script Node syntax regression and corrected sampled root-locus results to render as discrete points instead of false continuous branches. Production deployment unverified.
- 2026-10-29 (dev / CI pending): Added bounded continuous-time control analysis in Graphs with polynomial SISO transfer-function inputs, sampled Bode/Nyquist/root locus plots, Routh–Hurwitz table, and unity negative feedback. Structural regression added. Controller tuning, feedforward design and symbolic Laplace integration remain planned; release unverified.
- 2026-10-29 (dev, CI pending): Added a dedicated complex-number Graph workbench with 2D Argand plots and sampled 3D |f(z)| magnitude surfaces, presets z, z², inverse and exp, finite-input validation, accessible status and responsive canvas. Preserved existing real graph workflows. Structural regression added; deployment not yet confirmed.
- 2026-10-29 (dev, pending CI): Refreshed the entire interface with an original computational math-first design: stronger input/result hierarchy, teal navigation, palette/sidebar, consistent panels, focus visibility, mobile and reduced-motion refinements; added structural UI regression coverage. Deployment not yet verified.
## PR #90 merged — Rectangular SVD conditioning and cutoff (2026-10-29)

- [PR #90](https://github.com/saeedsai/ProMathStudio/pull/90) merged normally at main `2c286be5cefa164ffae6c27dad48db2eba74c465` after exact-head [PR Quality 40888207291](https://github.com/saeedsai/ProMathStudio/actions/runs/40888207291) passed **104/104 steps** at `5b4f623a5ebc6a8048d4a9dcbc5459e840f6974f`. Dev fast-forwarded without force. Main Quality, Pages publishing and hosted behavior remain unverified.
- Added 3×2/2×3 SVD absolute rank cutoff and condition assessment, scale-safe normalized condition ratio, and corrected UI size label. New structural/Chromium tests cover 80-digit near-rank-one references, transpose parity, invalid inputs, factor transfer and mobile. Direct V8 QA passed 500 deterministic matrices in addition to nine near-rank-one cases.

## Dev candidate — Rectangular SVD numerical-rank cutoff and conditioning (2026-10-29)

- Added scale-safe absolute numerical-rank cutoff and explicit condition assessment (rank deficient / well / moderately / ill-conditioned) to thin 3×2 SVD and transposed wide 2×3 SVD. Condition-number ratio is computed from normalized QR singular values to avoid avoidable scale-dependent rounding; zero matrices report rank-deficient diagnostics.
- Matrix UI now displays the cutoff and advisory for rectangular SVD and correctly labels the 2×3 option. Existing reconstruction and orthogonality rejection gates are unchanged.
- Added `tests/test_matrix_svd_rectangular_condition.py` for standalone/module parity and Node syntax, plus mandatory Chromium `tests/smoke_matrix_svd_rectangular_condition.py` using 80-digit rational orthonormal references, near-rank-one rank boundaries, scales 1e-12/1/1e11, wide transpose parity, invalid inputs, Equation Editor transfer and mobile layouts.
- Direct exact-source V8 checks passed nine rotated near-rank-one matrices at three scales (maximum observed small-singular-value relative error ~7.4e-5, reconstruction residual ~2.1e-16). Full CI/PR QA and Pages verification remain pending.

## PR #89 merged — 3×3 SVD conditioning and rank-cutoff diagnostics (2026-10-29)

- Released to `main` through ordinary expected-head [PR #89](https://github.com/saeedsai/ProMathStudio/pull/89), merge commit `aab6236604f0716487a56bf2d0d9ec56e4713d90`, after exact-head [PR Quality 40878671063](https://github.com/saeedsai/ProMathStudio/actions/runs/40878671063) passed **103/103 steps** at `622273b630ef07f8a658f26c714bb44d41ade416` (all successful, zero unresolved review threads). Dev fast-forwarded without force.
- Initial PR CI failed from malformed JS diagnostic text; repaired the quote and added a `node --check` structural regression before merging. Existing 3×3 SVD reconstruction and orthogonality gates remain unchanged. Scale-safe condition estimate, cutoff and risk advisory are now present in merged source.
- Main push Quality, GitHub Pages deployment and live hosted behavior are **not independently verified**: available connector exposes PR-triggered runs only, and direct Pages/Actions web fetch is disabled. Do not mark production deployed until confirmed.

### PR #89 CI recovery checkpoint (2026-10-29)

- Initial [PR Quality 40878422463](https://github.com/saeedsai/ProMathStudio/actions/runs/40878422463) failed the existing browser smoke because the new SVD diagnostic output concatenation omitted a closing JavaScript string quote. Fixed the source and standalone bundle, and strengthened the new structural test to run `node --check` on the matrix module so this syntax regression is caught before Chromium. No assertions or security gates were disabled. Exact repaired-head CI is pending.

## Dev candidate — Scale-safe 3×3 SVD condition diagnostics (2026-10-29)

- Extended the 3×3 SVD result with the relative numerical rank cutoff expressed in original input units and an explicit rank-deficient / well-conditioned / moderately conditioned / ill-conditioned assessment. Condition number now uses scaled singular values before multiplying by matrix magnitude to avoid avoidable overflow or underflow in the estimate. Zero-matrix diagnostics remain finite and explicit.
- Matrix Calculator displays the 3×3 SVD rank cutoff and condition assessment alongside U, S, V and reconstruction/orthogonality residuals; other SVD sizes preserve their existing presentation.
- Added `tests/test_matrix_svd_3x3_condition.py` and mandatory Chromium `tests/smoke_matrix_svd_3x3_condition.py` with 75-digit independent rational-rotation references at scales 1e-12/1/1e12, cutoff boundary cases, invalid input, factor transfer, mobile and no page errors. Module/standalone parity preserved. Pending exact-head PR Quality and production verification; no deployment claim.

## PR #88 merged — Thin wide 2×3 SVD (2026-10-29)

- Added real wide 2×3 thin SVD by transposing the tested 3×2 SVD and swapping U/V factors and orthogonality diagnostics. Matrix Calculator supports rank 0–2, U(2×2), S(2), V(3×2), reconstruction, conditioning and Equation Editor transfer.
- New structural test and mandatory Chromium regression cover independent analytic references, transpose-factor parity, zero/rank1/rank2/extreme scales, invalid input, UI factor transfer and mobile. Exact-source numeric spot checks passed 15 cases plus 200 deterministic matrix references (maximum discrepancy ~2.3e-15).
- [PR #88](https://github.com/saeedsai/ProMathStudio/pull/88) passed [Quality 40870173410](https://github.com/saeedsai/ProMathStudio/actions/runs/40870173410) at head `3e18358831442f2455c5c8ba4a2897cc8f005394` (102/102 steps); merged via expected-head ordinary PR at main `1e0367052f38cef3c8629460a4c59d4ff3e2dd38`. Dev fast-forwarded without force. **Main push Quality, Pages publish and hosted interactive behavior remain unverified** because PR-only connector workflow visibility and blocked direct Pages/web access. Not marked production verified.

## Dev candidate — Thin wide 2×3 SVD (2026-10-29)

- Added bounded real wide 2×3 thin SVD by transposing the validated 3×2 SVD, exchanging U/V factor shapes and orthogonality diagnostics. Supports ranks 0–2, singular values, conditioning, reconstruction, Matrix Calculator output and Equation Editor factor transfer. Existing square and 3×2 SVD preserved.
- Updated `src/matrix-tools.js` and standalone `index.html` in parity, plus Matrix Calculator scope note. Added structural `tests/test_matrix_svd_2x3.py` and mandatory Chromium `tests/smoke_matrix_svd_2x3.py` with independent analytic references, transpose parity, zero/rank1/rank2/extreme scales, invalid inputs, factor transfer and responsive layouts.
- Candidate remains **dev-only** until exact-head CI, reviewed PR, main Quality and Pages deployment are independently verified. Previous PR #87 was merged after [Quality 40862593177](https://github.com/saeedsai/ProMathStudio/actions/runs/40862593177) (101/101); production Pages remains unverified.

## PR #87 merged — Thin 3×2 SVD (2026-10-29)

- New thin real 3×2 SVD with pivoted scaled QR, twice-reorthogonalized Q and shared 2×2 factorization; reports U(3×2), S(2), V(2×2), numerical rank 0–2, conditioning, reconstruction and orthogonality. Matrix Calculator and Equation Editor factor transfer support 3×2; existing square SVD paths retained.
- Mandatory Chromium regression checks independent analytic singular-value references including rank-deficient and extreme-scale cases, invalid inputs, UI transfer and mobile layouts. The regression uses a relative rank cutoff only for zero singular-value roundoff, and strict relative checks for nonzero singular values.
- [PR #87](https://github.com/saeedsai/ProMathStudio/pull/87) passed exact-head [Quality 40862593177](https://github.com/saeedsai/ProMathStudio/actions/runs/40862593177) (101/101 steps) at `889c54ce1b21b5e22b311afc614f10784182910b` and merged ordinarily to main `c6d5f4efc7367ccaceb7bb912a883faf83b18989`. Main push Quality, Pages publish and hosted behavior remain **unverified**; do not mark deployed.

## Dev candidate — Thin 3×2 SVD diagnostics (2026-10-29)

- Added thin real 3×2 SVD with scaled pivoted QR, twice-reorthogonalized columns, and existing 2×2 SVD factorization. Exposes U (3×2), two singular values, V (2×2), rank 0–2, condition number, reconstruction and orthogonality diagnostics; retains existing 2×2 and 3×3 paths.
- Updated Matrix Calculator SVD dispatch and labels, standalone bundle, and Equation Editor transfer. Added mandatory Chromium regression `tests/smoke_matrix_svd_3x2.py` with independent analytic singular-value references, rank/scale/invalid cases, UI and responsive checks. CI, PR, main and Pages verification pending; not released.

## PR #86 merged — Shared 3×3 SVD pseudoinverse and rotated oracle QA (2026-10-29)

- Consolidated 3×3 Moore–Penrose pseudoinverse onto the validated 3×3 Jacobi SVD and preserved rank cutoff, condition diagnostics and four identity gates. Added independent 65-digit Decimal rational-rotation/scaling oracle, invalid-input, Equation transfer and responsive Chromium regression.
- First PR [Quality 40854024353](https://github.com/saeedsai/ProMathStudio/actions/runs/40854024353) failed a structural test requiring the removed duplicate Jacobi loop; corrected it to assert shared SVD convergence and pseudoinverse identity gates. Final exact-head [Quality 40854136591](https://github.com/saeedsai/ProMathStudio/actions/runs/40854136591) passed 100/100 steps at `8f5652a860b02023d0a18c82796d4dd25cfef1ae`. [PR #86](https://github.com/saeedsai/ProMathStudio/pull/86) merged at main `2846feb0ccc97dfc7cc7892c8e90d53f707d0aa3`; dev fast-forwarded without force. Main Quality and Pages/hosted verification remain unavailable; do not mark production deployed.

## Dev candidate — Rotated 3×3 pseudoinverse stability and shared SVD (2026-10-29)

- Reuse the validated one-sided Jacobi 3×3 SVD (`U`, `S`, `V`) when computing the 3×3 Moore–Penrose pseudoinverse, removing a duplicated singular-vector iteration while preserving the relative 1e-12 rank cutoff, condition advisory and all four Moore–Penrose residual gates.
- Add mandatory Chromium `tests/smoke_matrix_pseudoinverse_rotated.py` with independent 65-digit Decimal rational-rotation references, scaled rank-2 and rank-3 examples, four Moore–Penrose identities, validation failures, Equation transfer and responsive UI. Source module and standalone HTML remain synchronized. Release awaits exact-head Quality and PR checks; no Pages claim.

## PR #85 merged — 3×3 SVD and tiny nonzero matrix formatting (2026-10-29)

- [PR #85](https://github.com/saeedsai/ProMathStudio/pull/85) merged at `6c20f36a263d7e673f99a021cd5b05a3f5a26644` after exact-head [PR Quality 40850954000](https://github.com/saeedsai/ProMathStudio/actions/runs/40850954000) passed all 99 steps. Fixed new SVD browser test navigation without weakening assertions. 3×3 rank 0–3, reconstruction/orthogonality and mobile/factor transfer covered. GitHub Pages production verification still outstanding.

## 3×3 SVD QA correction (2026-10-29)

- Initial exact-head [PR #85 Quality 40850284532](https://github.com/saeedsai/ProMathStudio/actions/runs/40850284532) failed only the new 3×3 SVD Chromium regression at its responsive visibility check: the test had transferred to Equation Editor and did not return to Calculator. Corrected the test to restore the Matrix workspace before checking viewport visibility, retaining all assertions. New exact-head CI is pending; no production claim.

## Dev candidate — 3×3 real SVD diagnostics (2026-10-29)

- Added a bounded real 3×3 one-sided Jacobi SVD to Matrix Calculator (alongside existing 2×2), returning sorted singular values, U/V, numerical rank, condition number when full rank, and verified reconstruction/orthogonality residuals. Rank-deficient cases use orthogonal null-space completion; no dynamic evaluation or external libraries.
- Preserved SVD factor transfer to Equation and updated UI descriptions. Synchronized `src/matrix-tools.js` and bundled `index.html`. Added mandatory Chromium numerical/UI regression `tests/smoke_matrix_svd_3x3.py` for rank 0–3, scaled, rotated, ill-conditioned and invalid inputs, factor transfer and mobile layouts.
- This is a **dev candidate** only until exact-head PR Quality and production Pages verification are complete. It shares the current `dev`→`main` PR with the preceding tiny nonzero display correction.

## Dev checkpoint — Preserve tiny nonzero matrix results (2026-10-29)

- Preserve true nonzero matrix values below 1e-13 in result formatting rather than silently displaying them as zero; retain exact numeric zero as `0` and existing 12-significant-digit formatting.
- Synchronize `src/matrix-tools.js` and standalone `index.html`; add mandatory Chromium `tests/smoke_matrix_small_nonzero.py` covering 1e-14 transpose, result transfer, 390/768/1280 viewports and no page errors. Exact-head CI and PR release pending.
- [PR #84](https://github.com/saeedsai/ProMathStudio/pull/84) merged after [PR Quality 40846480766](https://github.com/saeedsai/ProMathStudio/actions/runs/40846480766) succeeded (97 steps); merged main `183421a23e943a0920bebabc76f39569c91ace92`; GitHub Pages verification still pending.

## Dev candidate — Ax=b RHS decimal validation (2026-10-29)

- Align right-hand-side vector input for Matrix Calculator solve(A,b) with the existing strict decimal/scientific matrix-entry grammar; reject JavaScript-only 0x/0b/0o forms and malformed inputs, retaining finite limits.
- Synchronize standalone `index.html` and `src/matrix-tools.js`; add mandatory `tests/smoke_matrix_rhs_decimal.py` Chromium UI/API regression for positive, negative, recovery and 390/768/1280 layouts. Exact-head CI, PR and Pages release are pending verification.

## PR #83 merged — Matrix decimal-only validation (2026-10-29)

- Corrected Matrix Calculator string input parsing, retaining decimal and scientific notation while rejecting hexadecimal, binary, octal and malformed forms; preserved 2×2/3×3 pseudoinverse behavior.
- Added structural parity and mandatory Chromium regression covering API validation, error recovery, and mobile layouts. Initial bundle newline parity failure fixed without relaxing tests. [PR Quality 40839418058](https://github.com/saeedsai/ProMathStudio/actions/runs/40839418058) passed 96/96 steps; [PR #83](https://github.com/saeedsai/ProMathStudio/pull/83) merged at `43cc4e68cd58e3d035235cda8e47e4087da4f66e`. Production Pages verification pending.

## Dev checkpoint — Matrix decimal-only validation and browser regression (2026-10-29)

- Reject JavaScript-only hexadecimal/binary/octal numeric prefixes and malformed string entries in matrix validation, while accepting signed decimal/scientific notation and preserving finite/magnitude bounds.
- Synchronize standalone HTML and module, add structural parity test and mandatory Chromium regression for direct API validation, UI rejection/recovery and responsive layouts. Release pending exact-head Quality and PR checks; no deployment claim.

## Released via PR #82 — 3×3 condition-risk diagnostics (2026-10-29)

- Matrix Calculator now exposes scientific-notation pseudoinverse singular values, the absolute numerical rank cutoff and a bounded 3×3 conditioning advisory (well/moderate/ill-conditioned or rank deficient), retaining strict instability rejection and Equation transfer. Corrected the UI cutoff label before merging.
- [dev Quality 40832920276](https://github.com/saeedsai/ProMathStudio/actions/runs/40832920276), [PR Quality 40832926954](https://github.com/saeedsai/ProMathStudio/actions/runs/40832926954), [main Quality 40833488246](https://github.com/saeedsai/ProMathStudio/actions/runs/40833488246) and [post-merge dev Quality 40833505946](https://github.com/saeedsai/ProMathStudio/actions/runs/40833505946) passed 95/95 workflow steps. [Pages 40833487595](https://github.com/saeedsai/ProMathStudio/actions/runs/40833487595) succeeded for main `505e44eb64a71a66d5c53e17d8c9184ec08b0b02`. Independent hosted interaction unavailable.

## Implemented on dev — 3×3 matrix condition-risk diagnostics (2026-10-29; release QA pending)

- Display scientific-notation singular values and numerical rank cutoff for matrix pseudoinverses; classify real 3×3 results as well-conditioned, moderately conditioned, ill-conditioned or rank deficient. Preserve the strict Moore–Penrose stability rejection and Equation transfer. Add independent rotated numerical oracle, scaled/near-dependent/invalid tests, structural parity and mandatory Chromium/mobile regression.
- Exact dev/PR/main Quality and Pages release gates remain pending; no production claim before verification.

## Released via PR #81 — Real 3×3 pseudoinverse (2026-10-29)

- Scaled one-sided Jacobi SVD supports bounded real 3×3 rank0–3 Moore–Penrose inverse, finite full-rank condition number, relative rank cutoff, four identity checks, invalid/unstable rejection, Equation transfer and offline standalone HTML. New structural and mandatory Chromium numerical/browser regression; previous 2×2/3×2/2×3 behavior preserved.
- [dev Quality 40826768921](https://github.com/saeedsai/ProMathStudio/actions/runs/40826768921), [PR Quality 40827183706](https://github.com/saeedsai/ProMathStudio/actions/runs/40827183706), [main Quality 40827675167](https://github.com/saeedsai/ProMathStudio/actions/runs/40827675167), [post-merge dev Quality 40827684515](https://github.com/saeedsai/ProMathStudio/actions/runs/40827684515) passed 94/94 steps; [Pages 40827674436](https://github.com/saeedsai/ProMathStudio/actions/runs/40827674436) succeeded for `main=128e578683e4f13960db6b3dd42f59c0add43ab5`. Independent hosted interaction unavailable.

## Implemented on dev — Real 3×3 pseudoinverse (2026-10-29; QA pending)

- Added scaled one-sided Jacobi SVD for rank 0–3 real 3×3 Moore–Penrose pseudoinverse, four identity residual checks, finite condition diagnostics, explicit instability rejection, Equation transfer and self-contained bundle parity. Added structural and mandatory Chromium numerical/reference/responsive regression; release awaits exact dev/PR/main Quality and Pages.

## Released via PR #80 — 2×2 pseudoinverse condition diagnostics (2026-10-29)

- Real 2×2 pseudoinverse now reports SVD singular values and finite condition numbers for full-rank matrices, null/rank-deficient diagnostics otherwise, retaining Moore–Penrose residual checks and editor transfer.
- [dev Quality 40823856638](https://github.com/saeedsai/ProMathStudio/actions/runs/40823856638), [PR Quality 40824282111](https://github.com/saeedsai/ProMathStudio/actions/runs/40824282111), [main Quality 40824722141](https://github.com/saeedsai/ProMathStudio/actions/runs/40824722141) and [post-merge dev Quality 40824732449](https://github.com/saeedsai/ProMathStudio/actions/runs/40824732449) all passed 93/93 steps. [Pages 40824721525](https://github.com/saeedsai/ProMathStudio/actions/runs/40824721525) succeeded for `main=4e30e9882270689e119aba67e0eceb0f7404bc23`; independent hosted interaction unavailable.

## Implemented on dev — 2×2 pseudoinverse condition diagnostics (2026-10-29; QA pending)

- Reuse scaled 2×2 SVD to return descending singular values and finite condition numbers only at numerical full rank, with null/rank-deficient diagnostics for zero and singular matrices, consistent with rectangular pseudoinverse results.
- Added structural and mandatory Chromium regressions for numerical references, relative rank cutoff, negative inputs, editor transfer and responsive UI; kept `index.html` synchronized. Release requires exact dev/PR/main Quality and Pages verification.

## Released via PR #79 — Matrix pseudoinverse conditioning (2026-10-29)

- Scaled, pivoted and reorthogonalized QR stabilizes near-dependent real 3×2/2×3 pseudoinverses, retains relative rank cutoff and Moore–Penrose checks, adds condition-number diagnostics and explicit numerical-instability rejection, and preserves 2×2 UI compatibility.
- Structural and Chromium regressions added, with negative, scaled, rank-cutoff, wide-duality, 2×2 compatibility and mobile cases. [dev Quality 40821822571](https://github.com/saeedsai/ProMathStudio/actions/runs/40821822571), [PR Quality 40822239669](https://github.com/saeedsai/ProMathStudio/actions/runs/40822239669), [main Quality 40822624404](https://github.com/saeedsai/ProMathStudio/actions/runs/40822624404) all passed 92/92 steps; [Pages 40822624083](https://github.com/saeedsai/ProMathStudio/actions/runs/40822624083) succeeded. [PR #79](https://github.com/saeedsai/ProMathStudio/pull/79) merged to `52b58b4bd99e2237ab6ccdb097ca8bbb711e550c`. Independent hosted interaction remains unavailable.

## Implemented on dev — Matrix pseudoinverse conditioning (2026-10-29; QA pending)

- Replaced cancellation-prone 3×2 Gram/Jacobi pseudoinverse with scaled pivoted QR and reorthogonalization; stable determinant-based small singular value, unchanged 1e-12 rank cutoff, Moore–Penrose checks, 2×3 transpose duality, condition diagnostics and explicit unstable-input rejection.
- Added structural and mandatory Chromium regressions for nearly coincident columns, scaled/zero/rank-deficient/invalid cases, wide transpose, numerical oracles and responsive UI. Await exact-head dev/PR/main Quality and Pages verification.

## Released via PR #78 — Wide 2×3 matrix pseudoinverse (2026-10-29)

- Matrix Calculator supports real wide 2×3 pseudoinverse using transpose duality of the existing scaled 3×2 Jacobi method; preserves the relative 1e-12 singular-value cutoff, rank 0/1/2 cases, four Moore–Penrose identity residuals, input validation, editor transfer and offline operation. Previous 2×2 and 3×2 paths remain available.
- Added `tests/test_matrix_pseudoinverse_wide.py` and mandatory Chromium `tests/smoke_matrix_pseudoinverse_wide.py` with numerical references, transpose duality, singular/zero/scaled inputs, least-norm solution, malformed inputs and 390/768/1280px UI. Updated the prior 3×2 negative case because 2×3 is now valid. **Release verified:** [dev Quality 40815230412](https://github.com/saeedsai/ProMathStudio/actions/runs/40815230412), [PR Quality 40815600999](https://github.com/saeedsai/ProMathStudio/actions/runs/40815600999), [main Quality 40816010524](https://github.com/saeedsai/ProMathStudio/actions/runs/40816010524) and [Pages deployment 40816009984](https://github.com/saeedsai/ProMathStudio/actions/runs/40816009984) succeeded (91/91 Quality steps). [PR #78](https://github.com/saeedsai/ProMathStudio/pull/78) merged to `6f933bd7dba9732b1eea2fe0bd0bbd56d3528bb9`; independent hosted interaction remains unavailable.
- Previously pending PRs #75, #76 and #77 have now had their main Quality and Pages **workflow** successes independently confirmed through the GitHub Actions runs API (see living ledger); interactive hosted verification remains unavailable.

## Merged to main — Graph Symbols numeric root, fraction and factorial (2026-10-29, PR #77; Pages verification pending)

- The Graph Symbols palette now enables existing numeric AST templates **Nth root** (`root(3,x)`), **Fraction** (`frac(a,b)`) and **Factorial** (`5!`) in both 2D and 3D Graph. Fraction placeholders must be replaced with graph variables or constants; root is real only on supported domains. Equation-only notation remains disabled in Graph and available in Equation.
- Added `tests/test_graph_palette_expansion.py` for whitelist/numeric grammar/CI coverage and mandatory Chromium `tests/smoke_graph_palette_expansion.py` for numeric reference values (cube root 8=2, 7/2=3.5, 5!=120), zero-division rejection, 2D/3D insertion and plotting, focus, notation gating and 390/768/1280px layouts. Source is in standalone `index.html`; no modular graph source exists. No new evaluator or arbitrary code execution.
- **Release status: merged through [PR #77](https://github.com/saeedsai/ProMathStudio/pull/77).** First [PR Quality 40810119082](https://github.com/saeedsai/ProMathStudio/actions/runs/40810119082) exposed a browser test-state bug (disabled-symbol drawer left open); corrected by explicit Escape dismissal without removing numerical assertions. Final exact-head [PR Quality 40810416911](https://github.com/saeedsai/ProMathStudio/actions/runs/40810416911) passed **90/90 steps**, including structural and Chromium suites. Reviewed six-file diff and zero unresolved review threads; SHA-checked ordinary merge produced `main=c2053405400588ae58cd09cc2a5b847f9584e9b1`. **Post-merge main Quality, Pages and hosted interaction remain unverified** because the connector exposes only PR-triggered workflow runs, commit statuses are empty and direct web/container access is unavailable. Do not mark Released until those gates are observed.

## Merged — Spreadsheet aggregate and custom-function numeric hardening (2026-10-29, PR #76; Pages verification pending)

- Data Tables preserves built-in `SUM`, `COUNT`, `MEDIAN`, `AVERAGE`, `AVG`, `MIN`, `MAX` and `IF` semantics even when imported/saved custom-function names collide. Nonreserved custom functions continue to compose with aggregates.
- Overflowing sums now report `#NUM!` instead of silently returning zero. Finite averages are accumulated with scaled terms to avoid unnecessary intermediate overflow. Invalid custom-function numerical evaluation produces a spreadsheet `#VALUE` error instead of a generic `#ERR` display; existing explicit `#...` errors are retained.
- Corrected the custom numeric evaluation bridge to bind already-parsed numbers directly, avoiding incorrect reinterpretation of scientific notation (for example `1e308`) as mathematical variables. Added large/small exponent reference tests to the structural and Chromium regression suites.
- Added structural `tests/test_sheet_numeric_hardening.py` and mandatory Chromium `tests/smoke_sheet_numeric_hardening.py` with numerical, collision, lazy-IF, workbook round-trip and responsive checks. **Merged via [PR #76](https://github.com/saeedsai/ProMathStudio/pull/76) after exact-head [PR Quality 40804400919](https://github.com/saeedsai/ProMathStudio/actions/runs/40804400919) passed all 89 steps. `main=28fdd036677af293ea1e649fc61e370e7e0f802a`. Post-merge main Quality, Pages and hosted interaction are not independently verified; do not mark deployed yet.**

## Merged — Transactional CSV / TSV / JSON import preview (2026-10-29, PR #75; Pages verification pending)

- Data Tables now validates a selected file before creating any sheet. A keyboard-focusable preview shows file name, row/column counts, column labels, duplicate/blank header warnings and up to three safely escaped sample rows. **Create table** commits; **Cancel import** or Escape discards the preview without changing the workbook.
- Existing CSV/TSV/JSON parser limits, one-column support, Unicode, formulas and graph XY validation are preserved. New mandatory Chromium `tests/smoke_data_import_preview.py` and structural `tests/test_data_import_preview.py` added; existing import smoke tests updated for explicit confirmation.
- **Release status: merged to `main` after 88/88 PR Quality steps; post-merge main Quality and GitHub Pages verification pending.** Do not mark deployed until those checks are observed.

## Released — Rectangular 3×2 Moore–Penrose pseudoinverse (2026-10-29, PR #74)

- Matrix calculator now supports real 3×2 A⁺ in addition to the existing 2×2 implementation, including rank-deficient and zero matrices. Scaled two-column Jacobi rotation, relative 1e-12 singular-value cutoff, finite-result guard and four Moore–Penrose identity residual checks. Output is 2×3 and transfers to Equation. 2×3/3×3 remain out of scope.
- Added mandatory browser `tests/smoke_matrix_pseudoinverse_rectangular.py` and structural `tests/test_matrix_pseudoinverse_rectangular.py` with numerical oracles, least-norm solution, input validation, 2×2 regression and mobile widths. **Released through [PR #74](https://github.com/saeedsai/ProMathStudio/pull/74):** dev [Quality 40791715101](https://github.com/saeedsai/ProMathStudio/actions/runs/40791715101) and PR [Quality 40792223068](https://github.com/saeedsai/ProMathStudio/actions/runs/40792223068) passed 87/87 steps; main [Quality 40792656828](https://github.com/saeedsai/ProMathStudio/actions/runs/40792656828) passed and [Pages 40792656403](https://github.com/saeedsai/ProMathStudio/actions/runs/40792656403) succeeded for `f8e254d94a1ae599437d7e0231754dce46dcd8f1`. Hosted interactive verification unavailable.
- Confirmed previous PR #73 post-merge [main Quality 40784717225](https://github.com/saeedsai/ProMathStudio/actions/runs/40784717225) passed and [Pages 40784715846](https://github.com/saeedsai/ProMathStudio/actions/runs/40784715846) succeeded for main `a226b3be`; hosted interactive verification unavailable.

## Merged to main — Full saved-snippet source inspection (2026-10-28, PR #73; Pages verification pending)

- Data Tables Functions & Code Library now provides a **View full** action for saved Formula/Python snippets. It displays the complete read-only source (up to 8,000 characters) in an accessible, scrollable preview without insertion or execution. Escape and Close dismiss the preview, clear the displayed code and restore focus. Catalog descriptions truncate long samples to 120 characters; built-in examples and existing Edit/Insert/Delete actions are preserved.
- Added structural `tests/test_data_snippet_inspection.py` and mandatory Chromium `tests/smoke_data_snippet_inspection.py` for 8,000-character source, HTML-injection text, storage immutability, Python nonexecution, focus restoration and 390/768/1280px. Updated Quality workflow and synchronized standalone `index.html`. **Merged via [PR #73](https://github.com/saeedsai/ProMathStudio/pull/73):** exact-head PR [Quality 40784222466](https://github.com/saeedsai/ProMathStudio/actions/runs/40784222466) passed 86/86 steps; merge commit `a226b3be31d80b90ad67399c178d8bb7d0fc5cf1`. Post-merge main Quality and Pages deployment could not be inspected with available workflow endpoints, so production verification remains pending.

## Released — Graph palette numeric validity (2026-10-28, PR #72)

- In 2D and 3D Graphs, the shared Symbols library now distinguishes known executable numeric templates (sin/cos, logarithms, constants, powers and other supported operations) from Equation-only notation. Non-plotting symbols are visible but disabled with an explanation; the full symbol library remains available in Equation. A context hint explains the distinction, and focus-based redraw handles programmatic workspace navigation.
- Added `tests/test_graph_palette_validity.py` and mandatory Chromium `tests/smoke_graph_palette_validity.py` for enabled/disabled entries, 2D/3D draft isolation, keyboard focus, Equation compatibility and 390/768/1280px layouts. **Released:** [PR #72 Quality 40777296427](https://github.com/saeedsai/ProMathStudio/actions/runs/40777296427) passed 85/85 steps; [main Quality 40777944534](https://github.com/saeedsai/ProMathStudio/actions/runs/40777944534) and [post-merge dev Quality 40777956663](https://github.com/saeedsai/ProMathStudio/actions/runs/40777956663) passed; [Pages 40777944359](https://github.com/saeedsai/ProMathStudio/actions/runs/40777944359) succeeded. Interactive hosted browser navigation remains unverified.

## Released — Nested spreadsheet custom-function composition (2026-10-28, PR #71)

- Data Tables now evaluates innermost custom functions and built-in aggregates in a shared bounded loop. Expressions such as `=SUM(TWICE(2),TWICE(SUM(A1:A3)))` and `=TWICE(TWICE(3))` work when the user defines `TWICE(x)=2*x`; lazy `IF` remains intact. The evaluator rejects invalid argument counts, non-finite results and excessive nesting without `eval` or `Function`.
- Added structural and mandatory Chromium regression for numeric references, cross-nesting, lazy IF, unknown functions, invalid arity, 41-deep nesting, workbook persistence, UI and responsive layouts. **Released:** [PR #71 Quality 40768400816](https://github.com/saeedsai/ProMathStudio/actions/runs/40768400816), [main Quality 40768958629](https://github.com/saeedsai/ProMathStudio/actions/runs/40768958629), [dev Quality 40768995115](https://github.com/saeedsai/ProMathStudio/actions/runs/40768995115) and [Pages 40768957690](https://github.com/saeedsai/ProMathStudio/actions/runs/40768957690) all succeeded.

## Released — Real 2×2 Moore–Penrose pseudoinverse (2026-10-28, PR #70)

- Added a Pseudoinverse button to the matrix calculator for invertible, rank-deficient, and zero 2×2 real matrices, with SVD-relative singular-value cutoff, numerical rank, Moore–Penrose residual diagnostics, and Equation Editor transfer. The existing inverse, SVD and other matrix operations are preserved.
- Added structural and mandatory Chromium numerical/UI/mobile regressions, including singular, zero, scaled, invalid and editor-transfer cases. **Released:** [dev Quality 40759480095](https://github.com/saeedsai/ProMathStudio/actions/runs/40759480095), [PR #70 Quality 40760282028](https://github.com/saeedsai/ProMathStudio/actions/runs/40760282028), [main Quality 40760948437](https://github.com/saeedsai/ProMathStudio/actions/runs/40760948437) and [Pages deployment 40760947939](https://github.com/saeedsai/ProMathStudio/actions/runs/40760947939) all succeeded.

## Released — Accessible saved-snippet import preview keyboard cancellation (2026-10-28, PR #69)

- Importing a saved snippet JSON file moves keyboard focus into its review preview. Escape dismisses the preview without writing to saved snippets and returns focus to the Import button; the existing Cancel button remains available.
- Expanded mandatory Chromium preview regression for immediate Escape dismissal and focus restoration at 390/768/1280px, plus structural assertions for preview focus and standalone source parity. **Released:** [PR #69 Quality 40755066897](https://github.com/saeedsai/ProMathStudio/actions/runs/40755066897), [main Quality 40755825780](https://github.com/saeedsai/ProMathStudio/actions/runs/40755825780) and [Pages 40755826828](https://github.com/saeedsai/ProMathStudio/actions/runs/40755826828) succeeded.

## Released — Single-column Data Tables CSV/TSV/JSON interchange (2026-10-28, PR #68)

- Import one-column CSV, TSV and JSON into Data Tables, including quoted Unicode/multiline cells and editable formulas from source CSV; retain strict two-coordinate requirements in Graphs.
- Added mandatory browser round-trip/rollback and structural parity regression coverage. [Dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/40751963576), [PR Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/40752718843), [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/40753328201) and [Pages deployment](https://github.com/saeedsai/ProMathStudio/actions/runs/40753327266) passed.

## Released — Saved-snippet JSON import preview and conflict-safe confirmation (2026-10-28, PR #67)

- Saved Data Tables snippet JSON imports now show a review summary plus a safely escaped, scrollable list of names, types, and code excerpts before any localStorage mutation. Users can **Apply import** or **Cancel import**; name conflicts disable Apply until **Skip conflicting names and keep saved versions** is explicitly selected. Existing snippets are never silently overwritten, identical entries remain idempotent, and Python snippets are never executed on import.
- A preview is invalidated if the local library changes before confirmation. File/schema/40-entry validation, atomic storage failure rollback, and existing export behavior remain in place.
- Added mandatory Chromium `tests/smoke_data_snippet_preview.py` and updated the existing interchange regression for confirmation semantics. Released via [PR #67](https://github.com/saeedsai/ProMathStudio/pull/67). Exact-head [dev Quality 40741172865](https://github.com/saeedsai/ProMathStudio/actions/runs/40741172865), [PR Quality 40741901937](https://github.com/saeedsai/ProMathStudio/actions/runs/40741901937) and [main Quality 40742516492](https://github.com/saeedsai/ProMathStudio/actions/runs/40742516492) all passed (81 steps); [Pages 40742515657](https://github.com/saeedsai/ProMathStudio/actions/runs/40742515657) succeeded. Independent interactive verification of the published URL was unavailable.

## Released — Graph Symbols caret-aware insertion (2026-10-28, PR #66)

- Unified the Symbols palette insertion path across Equation, Calculator and Graphs, removing duplicated graph/calculator insertion logic. 2D/3D graph function templates such as `sin(x)`, `cos(x)` and `sqrt(x)` select the editable `x` placeholder; replacing a selection inserts at the caret and restores editor focus.
- Graph symbol edits remain drafts until **Plot** is clicked and no longer trigger an unrelated Equation preview refresh. Existing 2D/3D draft isolation, math library, symbolic solver and calculator features are preserved.
- Added focused structural `tests/test_graph_symbol_caret.py` and mandatory Chromium `tests/smoke_graph_symbol_caret.py` for selection, focus, 2D/3D drafts, no auto-plot and 390/768/1280px layouts. Released via [PR #66](https://github.com/saeedsai/ProMathStudio/pull/66). Exact-head [dev Quality 40730918150](https://github.com/saeedsai/ProMathStudio/actions/runs/40730918150), [PR Quality 40731721171](https://github.com/saeedsai/ProMathStudio/actions/runs/40731721171) and [main Quality 40732325880](https://github.com/saeedsai/ProMathStudio/actions/runs/40732325880) all passed (79 steps); [Pages deployment 40732326236](https://github.com/saeedsai/ProMathStudio/actions/runs/40732326236) succeeded.

## Released — Equation CAS accessible result announcements and keyboard focus (2026-10-28, PR #65)

- Added one concise, screen-reader-accessible live summary for symbolic success, errors and worker progress, including the first result. The full MathML solution region remains navigable without duplicating live announcements.
- Kept the **Execute** button keyboard-focusable while a SymPy job is running using `aria-disabled` and the existing guarded busy state; no duplicate submissions or solver capability changes.
- Added mandatory Chromium `tests/smoke_equation_accessibility.py` for offline answers, invalid input, delayed worker reentry/focus, task picker focus and 390/768/1280px layouts. Released via [PR #65](https://github.com/saeedsai/ProMathStudio/pull/65): [dev Quality 40721833455](https://github.com/saeedsai/ProMathStudio/actions/runs/40721833455), [PR Quality 40722710824](https://github.com/saeedsai/ProMathStudio/actions/runs/40722710824), [main Quality 40723301997](https://github.com/saeedsai/ProMathStudio/actions/runs/40723301997) and [Pages deployment 40723299988](https://github.com/saeedsai/ProMathStudio/actions/runs/40723299988) all passed.

## Released — Nested spreadsheet aggregates (2026-10-28, PR #64)

- Fixed Data Tables formulas that combine aggregate functions, such as `=SUM(MEDIAN(A1:A5),COUNT(A1:A5))`. Aggregations now resolve innermost-first with a bounded 40-pass nesting limit, preserving existing `IF` lazy evaluation, range/reference checks, cycle detection, and the no-`eval` token grammar.
- Added a searchable **Nested aggregates** example to the Functions & Code Library; no existing formulas or actions were removed.
- Added mandatory Chromium regression `tests/smoke_sheet_nested_aggregates.py` covering numeric reference values, nested `SUM/MEDIAN/COUNT/AVERAGE/MIN/MAX`, nested `IF`, cross-sheet ranges, blank/text exclusion, cycles, invalid references, nesting limit, library insertion and responsive controls. Released via [PR #64](https://github.com/saeedsai/ProMathStudio/pull/64): [dev Quality 40712426644](https://github.com/saeedsai/ProMathStudio/actions/runs/40712426644), [PR Quality 40713240766](https://github.com/saeedsai/ProMathStudio/actions/runs/40713240766), [main Quality 40713839887](https://github.com/saeedsai/ProMathStudio/actions/runs/40713839887) and [Pages 40713838707](https://github.com/saeedsai/ProMathStudio/actions/runs/40713838707) all succeeded (78 QA steps per candidate).

## Released — Reliable TSV round-trip and CSV fixture repair (2026-10-28, PR #63)

- Corrected Data Tables **Export TSV** to quote commas and semicolons in addition to tabs, newlines and quotation marks. The shared CSV/TSV importer sniffs separators from the header; unquoted commas in otherwise valid TSV headers could previously cause the wrong delimiter to be selected on reimport. The export remains value-only and offline.
- Added an explanatory tooltip, preserved the existing Data Tables export actions, and synchronized standalone `index.html` with `src/data-tables.js`.
- Added mandatory Chromium regression `tests/smoke_data_tsv_delimiter.py` covering Unicode, ambiguous headers, tabs, multiline fields, quotes, reimport, malformed-file rollback and responsive controls.
- Diagnosed the previous dev Quality failure in `tests/smoke_data_formula_source_csv.py`: the test fixture itself contained an unquoted `IF(...,...,...)` CSV field. Rebuilt the fixture with Python's `csv.writer` while preserving all round-trip assertions. Verified exact-dev-head Quality [40702968005](https://github.com/saeedsai/ProMathStudio/actions/runs/40702968005), PR Quality [40703576622](https://github.com/saeedsai/ProMathStudio/actions/runs/40703576622), main Quality [40704132299](https://github.com/saeedsai/ProMathStudio/actions/runs/40704132299) and GitHub Pages [40704131521](https://github.com/saeedsai/ProMathStudio/actions/runs/40704131521).

## Released — Editable formula-source CSV export (2026-10-28, PR #63)

- Added **Export formulas CSV** to Data Tables, alongside the existing evaluated **Export CSV**. The new export preserves original editable cell strings, including formulas, quoted commas, embedded line breaks and Unicode; reimport restores formula text rather than flattening it into calculated values.
- Kept the existing evaluated CSV and JSON export behavior unchanged. The new button explicitly warns that external spreadsheet programs may evaluate formulas on opening the exported CSV.
- Added mandatory Chromium round-trip regression `tests/smoke_data_formula_source_csv.py`, registered in `.github/workflows/quality.yml`. Released through [PR #63](https://github.com/saeedsai/ProMathStudio/pull/63) with full Chromium regression and verified GitHub Pages deployment.

## Released — Data Tables saved-snippet JSON interchange (2026-10-28, PR #62)

- Added versioned `promathstudio-snippets` JSON export/import for saved Formula and Python snippets, with a data-only schema and browser download/file picker. Existing localStorage format is unchanged.
- Import merges nonconflicting snippets without overwriting existing names, treats exact repeats as idempotent, and rejects unsupported versions, duplicate names, malformed/oversized files, invalid formulas, name conflicts and more than 40 saved snippets. Validation occurs before an atomic storage write; quota failures leave the catalog unchanged. Import never executes Python.
- Added focused static test `tests/test_data_snippet_interchange.py` and mandatory Chromium regression `tests/smoke_data_snippet_interchange.py` covering JSON round trip, Unicode, rollback, reload and responsive controls. Source/standalone parity synchronized. Verified on exact dev [Quality 40685392257](https://github.com/saeedsai/ProMathStudio/actions/runs/40685392257) and [PR Quality 40686077662](https://github.com/saeedsai/ProMathStudio/actions/runs/40686077662), merged through [PR #62](https://github.com/saeedsai/ProMathStudio/pull/62) to main `5cab0ca1a8539d981618c5647470fc87d4ceec72`. Exact-main [Quality 40686644777](https://github.com/saeedsai/ProMathStudio/actions/runs/40686644777), [Pages 40686645258](https://github.com/saeedsai/ProMathStudio/actions/runs/40686645258) and [cleanup 40686644691](https://github.com/saeedsai/ProMathStudio/actions/runs/40686644691) all passed; post-merge dev Quality 40686662154 passed. Hosted interactive browsing remains unverified.

## Released — Equation task-family organization (2026-10-28, PR #61)

- Organized the combined Equation workstation's existing task selector into four accessible native groups: **Write & solve**, **Notebook & examples**, **Numerical & differential**, and **Solver configuration**. No solver, notebook, CAS or export buttons were duplicated, removed or hidden by this grouping; task values and drafts are preserved.
- Added `tests/smoke_equation_task_groups.py` with Chromium coverage for grouping, offline CAS, notebook, numerical/ODE, assumptions, draft preservation, other workspace isolation and 390/768/1280px layout. Registered it as a mandatory Quality workflow step. Source/standalone parity synchronized.
- Verified on exact dev and PR heads, merged through PR #61, passed main Quality, and published through GitHub Pages. Interactive public-site browsing remains unverified.

## Released — Unified Equation workstation (2026-10-28, PR #60)

- Combined the Equation Editor and Symbolic Solver into one **Equation** navigation tab. Retained live preview, math input, notebook, examples, CAS engine and symbolic operations, numerical methods, ODE initial values, assumptions, Python/SymPy code and exports. Legacy `mode('solver')` routes now activate Equation without creating a duplicate workspace.
- Unified the progressive workspace task selector so numerical/ODE/assumptions tools remain discoverable; CAS operation controls remain available under the basic Equation task. Preserved task selection across workspace changes and mobile layout.
- Added mandatory Chromium `tests/smoke_equation_combined.py` with CAS computation, task picker, notebook, responsive layout and legacy-route assertions; adapted existing navigation, task and Symbols browser regressions to the four-tab UI, preserving their functionality assertions.
- CI initially failed because existing browser smoke expected the removed Solver tab ([run 40673846827](https://github.com/saeedsai/ProMathStudio/actions/runs/40673846827)); subsequent CI identified the modular/standalone workspace task source parity failure ([run 40677384808](https://github.com/saeedsai/ProMathStudio/actions/runs/40677384808)). Updated `src/workspace-tasks.js` to match the standalone `index.html` without weakening the source-consistency test. **Released:** [PR #60](https://github.com/saeedsai/ProMathStudio/pull/60) merged to `main=88cb73225fa564806225ae8a549ace8c7de7a33d`. [Exact candidate dev Quality 40678121140](https://github.com/saeedsai/ProMathStudio/actions/runs/40678121140), [PR Quality 40678640721](https://github.com/saeedsai/ProMathStudio/actions/runs/40678640721), [main Quality 40679248178](https://github.com/saeedsai/ProMathStudio/actions/runs/40679248178) (73/73 steps each) and [GitHub Pages 40679248370](https://github.com/saeedsai/ProMathStudio/actions/runs/40679248370) all succeeded on their corresponding candidate/merge SHAs. Independent live UI browsing unavailable.

## Released — Data Tables MEDIAN and bounded formula references (2026-10-28, PR #59)

- Added `MEDIAN` to the searchable Functions & Code Library and offline spreadsheet evaluator: odd/even counts, multiple arguments, numeric ranges and quoted cross-table ranges. Ignores text/blank/whitespace cells; no numeric values returns `#NUM!`.
- Range aggregation now treats unpopulated in-grid rows and columns as blanks rather than zero-valued observations, fixing MEDIAN/AVERAGE/COUNT on short tables. Existing explicit numeric zeros are still counted.
- Aggregation ranges reject invalid workbook coordinates (row 0, rows above 6000, columns beyond AF) with `#REF!` instead of treating them as zero. Unpopulated in-grid cells remain blank.
- Added focused unit and mandatory Playwright tests for MEDIAN, existing SUM/AVERAGE/COUNT/MIN/MAX/IF, cross-table, cycle, invalid ranges, insertion and persistence. **Released:** [PR #59](https://github.com/saeedsai/ProMathStudio/pull/59) merged to `main=49ce54e82ce4ffb7ef440f325c5ec726601b2e9a`; [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/40669918914), [PR Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/40670408512), [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/40670931938) and [Pages deployment](https://github.com/saeedsai/ProMathStudio/actions/runs/40670930496) passed. Independent live UI browsing unavailable.

## Released — Shared Symbols palette navigation and keyboard accessibility (2026-10-28, PR #58)

- Fixed the **∑ Symbols** quick-menu visibility in Symbolic Solver and 2D/3D Graphs: workspace-specific body classes are now synchronized by the central workspace switcher, including session restore and programmatic navigation, rather than only Editor/Calculator click handlers. Existing palette insertion targets the working equation in Solver and the current 2D/3D graph expression in Graphs; drafts remain separate.
- The Symbols button now exposes `aria-expanded`/`aria-controls` state. Escape closes the drawer and restores focus to its trigger; clicking an open Symbols trigger closes it without focusing a hidden search field.
- Added Playwright regression `tests/smoke_shared_symbols.py` covering Solver, 2D and 3D insertion, draft isolation, keyboard focus, session/API mode restore, 390/768/1280 px visibility and Data Tables isolation. Registered as a mandatory Quality step. Updated user guide.
- **Released:** [PR #58](https://github.com/saeedsai/ProMathStudio/pull/58) merged via ordinary PR to `main=4cb8d38319e7d3bc62a31b871818ad609311f93b`. Exact dev Quality [40660701904](https://github.com/saeedsai/ProMathStudio/actions/runs/40660701904), PR Quality [40661179270](https://github.com/saeedsai/ProMathStudio/actions/runs/40661179270), main Quality [40661759085](https://github.com/saeedsai/ProMathStudio/actions/runs/40661759085), post-merge dev Quality [40661779124](https://github.com/saeedsai/ProMathStudio/actions/runs/40661779124), Pages [40661757481](https://github.com/saeedsai/ProMathStudio/actions/runs/40661757481), and branch cleanup [40661757692](https://github.com/saeedsai/ProMathStudio/actions/runs/40661757692) all passed. Initial [Quality 40660474297](https://github.com/saeedsai/ProMathStudio/actions/runs/40660474297) caught an actual missing `aria-expanded=false` update after insertion; fixed on dev and retained browser assertion. Hosted page was not independently interactively verified because external browsing was inaccessible; Pages deployment and CI browser tests were verified.

## Released — Data Tables saved snippet management and safe persistence (2026-10-28, PR #57)

- Added explicit **Edit**, rename and confirmation-based **Delete** controls for user-created Formula/Python snippets; built-in catalog entries remain read-only. Prevents silent overwrite of an existing name unless the user selected Edit. Storage writes are transactional: quota/security errors do not mutate the in-memory snippet catalog, and a cancelled deletion does nothing. The standalone `index.html` and `src/data-tables.js` remain synchronized. Added dedicated Playwright regression `tests/smoke_data_saved_snippets.py` for creation, rename, duplicate prevention, Python no-auto-run, cancelled/accepted deletion, storage failure, reload persistence and mobile viewports, registered in mandatory Quality. **Released via [PR #57](https://github.com/saeedsai/ProMathStudio/pull/57) to main `92e4860303396700ebe94e2f116cc3086fe80b66`.** Exact dev Quality [40654625640](https://github.com/saeedsai/ProMathStudio/actions/runs/40654625640), PR Quality [40654631674](https://github.com/saeedsai/ProMathStudio/actions/runs/40654631674), main Quality [40655146895](https://github.com/saeedsai/ProMathStudio/actions/runs/40655146895), Pages [40655146396](https://github.com/saeedsai/ProMathStudio/actions/runs/40655146396), and branch cleanup [40655146814](https://github.com/saeedsai/ProMathStudio/actions/runs/40655146814) succeeded. The initial test harness failure [40654438754](https://github.com/saeedsai/ProMathStudio/actions/runs/40654438754) was fixed without weakening checks. Hosted interactive QA was unavailable; deployment status verified through Pages Actions.

## Released — Data Tables Functions & Code Library and reliable insertion (2026-10-28, PR #56)

- Added searchable Formula, Python and Table Operation categories, including INNER/LEFT JOIN, UNION ALL, INTERSECT and EXCEPT chooser entries. Fixed a real focus/blur race: the table grid re-renders on cell blur, so library insertion now uses stable sheet/row/column coordinates instead of a detached input element; formula selection replaces the whole cell and persists it. Python recipes insert without running code, reveal the Python editor, and operation recipes select the native Combine controls without executing the operation. Added structural unittest and dedicated Playwright regression to mandatory Quality, with responsive and no-auto-run assertions. Exact dev Quality [40648285412](https://github.com/saeedsai/ProMathStudio/actions/runs/40648285412), PR Quality [40648574352](https://github.com/saeedsai/ProMathStudio/actions/runs/40648574352), main Quality [40648944819](https://github.com/saeedsai/ProMathStudio/actions/runs/40648944819), Pages [40648944379](https://github.com/saeedsai/ProMathStudio/actions/runs/40648944379), synchronized dev Quality [40648967588](https://github.com/saeedsai/ProMathStudio/actions/runs/40648967588) all passed; released at main `8d9849c2cbece6d1d128f59098ffb455f6e1eab5` through ordinary [PR #56](https://github.com/saeedsai/ProMathStudio/pull/56). Hosted independent interactive QA unavailable; no full Excel parity claimed.

## In QA — Reject lossy JSON record schema drift on import (2026-10-28)

- The shared Graphs/Data Tables JSON parser now rejects object-record arrays whose later rows introduce or omit column names, rather than silently dropping values outside the first record's header set. Key order may vary and Unicode values are preserved. Added focused Playwright coverage for reordered keys, extra/missing/replaced keys, transactional table/graph import rollback and responsive layouts; registered in mandatory Quality. Awaiting exact dev-head CI, independent PR gate, main Quality and Pages verification; not yet released.

## In QA — Preserve explicit empty CSV/TSV records on import (2026-10-28)

- The shared graph and Data Tables delimited parser no longer discards intentional all-empty records (`,`, tab-delimited fields or quoted empty cells). Truly blank physical lines remain ignored. Added EOF row-limit enforcement and focused browser tests for multiline quoted data, CSV export/reimport, TSV, malformed-input rollback, boundaries and responsive viewports. Mandatory Quality, PR, main and Pages verification pending; not yet released.

## Released — Reject lossy Data Tables JSON export for duplicate headers (2026-10-28, PR #52)

- JSON export now rejects duplicate column labels before downloading, preventing silent overwrites when rows are converted to JSON objects. CSV still retains duplicate headers, and distinct case-sensitive labels and one empty header remain valid. Added focused browser regression covering rejection, workbook rollback, CSV preservation, formula values, case/empty-header edges and responsive viewports; registered in mandatory Quality. Exact dev Quality 40632849087, PR Quality 40633188532, main Quality 40633492145, Pages 40633491520 and synchronized dev Quality 40633506608 succeeded. Released via [PR #52](https://github.com/saeedsai/ProMathStudio/pull/52) into `main=f067cef5804eb8721ea621de6f67fd120c6798ef`. Public interactive Pages QA unavailable; branch protections remain absent.

## Released — Indexed Data Tables JOIN ordering and bounded output (2026-10-28, PR #50)

- Replaced quadratic nested-loop equality JOIN with indexed right-hand key lookup while retaining duplicate-key Cartesian matches, empty-key matching, original left/right row ordering, and INNER/LEFT/RIGHT/FULL semantics. Rejects invalid join keys and oversize outputs before creating any new table. Added dedicated Playwright reference/negative/2,500-row/browser/mobile regression to mandatory Quality. Source and standalone index synchronized. Exact dev Quality 40630778150, PR Quality 40631064272, main Quality 40631391132 and Pages 40631391048 passed; merged via [PR #50](https://github.com/saeedsai/ProMathStudio/pull/50) to `main=97cd999b969feef6cbc83043e48befbb9b05ae72`. Hosted interactive QA unavailable; broader Data Tables and inventory gaps remain open.

## Released — Data Tables quoted clipboard TSV round-trip (2026-10-28, PR #48)

- Fixed context-menu row/column copy/paste of cells containing tabs, embedded newlines and escaped double quotes. A bounded TSV parser now validates the entire clipboard payload before mutating the workbook, rejecting malformed quotes, excessive columns/rows/cell lengths and oversized text without partial writes. Quote-only cells are escaped on row/column copy. Corrected context-action status routing so clipboard success/errors appear in the Data Tables status region rather than the generic hub. Added focused Playwright regression for context menus, formulas, invalid-input rollback and responsive viewports to mandatory Quality. Exact dev Quality 40627309037, PR Quality 40627630580, main Quality 40627969367, Pages 40627969011 and cleanup 40627969329 passed; merged via [PR #48](https://github.com/saeedsai/ProMathStudio/pull/48) into `main=621720b85ab8f82f76c97a226439f1c17f29ead4`. Hosted interactive Pages QA remains unavailable; broader spreadsheet QA remains open.

## Released — Data Tables advanced column filter row alignment (2026-10-28, PR #46)

- Corrected an off-by-one error in advanced column filtering: visible spreadsheet row numbers start at 1, but the filter had evaluated the previous row and hidden the first. Filtered first/last rows, numeric conditions, text search intersections, sort re-render and reset are now covered by a new focused Playwright test registered in mandatory Quality. This preserves workbook source values and existing filter drafts. Implementation dev Quality 40623617625, final dev Quality 40624054180, PR Quality 40624058378, main Quality 40624474851, Pages 40624474428 and cleanup 40624474885 all passed; merged via [PR #46](https://github.com/saeedsai/ProMathStudio/pull/46) into `main=f08fbaafbe1879f35b1acacff06c6e08d44f93ec`. Independent hosted interactive smoke remains unavailable; broader Data Tables QA remains open.

## Released — Data Tables keyboard menu traversal and quick-action focus (2026-10-28, PR #44)

- ArrowLeft/ArrowRight/Home/End move keyboard focus among the five top-level Data Tables action summaries with wraparound, without opening menus or intercepting arrows in table filter inputs. Quick **Filter rows** and **Python** buttons now move focus to their opened menu summaries. Native Enter/Space, Escape, existing workbook state and unsaved filter drafts remain intact. New focused Playwright regression covers traversal, wrap, exclusive opening, input-arrow behavior, quick-action focus, drafts and 390/768/1280 px viewports. Exact dev [Quality 40620765091](https://github.com/saeedsai/ProMathStudio/actions/runs/40620765091) and [PR Quality 40621089629](https://github.com/saeedsai/ProMathStudio/actions/runs/40621089629) passed; [PR #44](https://github.com/saeedsai/ProMathStudio/pull/44) merged normally into `main=e0e4a43d058eb37b7e2d7abc0c2421321f117f77`; [main Quality 40621493874](https://github.com/saeedsai/ProMathStudio/actions/runs/40621493874), [Pages 40621493113](https://github.com/saeedsai/ProMathStudio/actions/runs/40621493113) and [branch cleanup 40621493871](https://github.com/saeedsai/ProMathStudio/actions/runs/40621493871) succeeded. Dev was fast-forwarded to the merge without force; hosted interactive QA remains unavailable and this is not full Data Tables/WCAG completion.

## Released — keyboard workspace navigation and live status (2026-10-28, PR #42)

- ArrowLeft/ArrowRight/Home/End move visible keyboard focus among all five workspace buttons, including Data Tables; Enter/Space still activate, with no accidental mode change from arrows. Added high-contrast focus outline and polite workspace subtitle announcement. Preserves graph drafts and native tab order. New Playwright regression tests focus wrap, active route, activation, responsive widths and runtime errors. Dev Quality 40617989352, PR Quality 40618289024, main Quality 40618678114, Pages 40618678231 and synchronized dev Quality 40618700413 all succeeded for merge `70e7fdedc120a817724c72ae0f0068663a428f41`. Hosted interactive Pages smoke unavailable; no full WCAG certification claimed.

## Released — Data Tables action-menu keyboard and dismissal QA (2026-10-28, PR #41)

- Improved the existing Table/Filter/Combine/Files/Python menus: visible keyboard focus, Escape dismissal with focus returned to the active summary, and outside-pointer dismissal. Preserved existing input drafts, menu quick buttons, action handlers and workbook data. Added dedicated Playwright regression for keyboard, menu exclusivity, draft retention, sort, CSV download, Python and mobile; wired it into mandatory Quality. Dev Quality 40612392877, PR Quality 40612788052, main Quality 40613229652, Pages 40613229183 and synchronized dev Quality 40613655403 succeeded for merge `62074700d407f99fa527f474c265e123024d81f7`. This is not a general accessibility certification.

## Released — Graphs action grouping and panel QA (2026-10-28, PR #39)

- Grouped secondary Graphs send-to-Editor/Solver actions in an accessible disclosure; kept Plot, Reset, PNG and 2D/3D mode switches visible. Preserved existing button IDs, event handlers, graph state and workspace drafts. Added dedicated Playwright graph-panel regression and mandatory CI step for axes, appearance, 2D/3D, PNG, keyboard transfer, table task and mobile. Exact dev Quality 40609332818, PR Quality 40609762689, main Quality 40610140241 and Pages 40610140252 succeeded for main `10a1e067ca7184e0315f88d29982e848b069e189`. Hosted interactive smoke unavailable; graph import discoverability remains a separate open gap.

## Unreleased — exclusive workspace task disclosures (2026-10-28)

- Selecting a workspace task now closes other registered optional task forms in that workspace, including when returning to Basic. The chosen tool opens as before; unrelated panels, input drafts and remembered workspace selections are retained. Expanded the mandatory compact-task Playwright regression to cover Calculator, Graphs and Data Tables transitions and unsaved graph input preservation. Preserves explicit ODE/numerical/table-to-graph handoffs by selecting the Graphs Table task; added a handoff-specific browser assertion after CI exposed a regression. Await exact-head Quality, PR and Pages gates.

## Unreleased — compact workspace UI (2026-10-27)

- Replaced redundant 4–6-button task shortcut bars in each workspace with one accessible, responsive **Workspace tools** selector. Original calculation, graph, solver, table, import/export and notebook functionality remains available. Added direct browser tests for selection, state restoration, zero duplicate task buttons and mobile overflow. Exact-head Quality and Pages required for release.

## Unreleased — FFT inverse regression field-name correction (2026-10-27)

- Repaired `smoke_fft.py` to read inverse FFT `{re,im}` objects rather than spectrum `{real,imag}` fields; added an explicit recovered-real/windowed-sample equality check at 1e-10. This addresses real CI failure after 47 successful checks, without changing production FFT math. Full exact-head QA remains mandatory.

## Unreleased — isolate precision UI smoke from task navigator (2026-10-27)

- Precision browser regressions open the actual native disclosure summary, assert expansion, and preserve numerical/invalid-input/mobile coverage; task-first workspace regression now separately asserts High precision task navigation. This responds to real CI selector timeouts while retaining UI coverage. Exact-head full CI remains required.

## Unreleased — bounded real 2×2 SVD (2026-10-27)

- Added scaled one-sided Jacobi SVD for real 2×2 matrices, nonnegative descending singular values, orthonormal U/V, numerical rank and reconstruction diagnostics, factor transfer to Equation Editor. Handles singular, zero and large-scale-separation matrices without an AᵀA eigenvalue cancellation. Added numerical/reference/negative/UI regression to mandatory Quality. Exact-source V8 reference checks passed; full CI and Pages pending.

## Unreleased — periodic Hann window for FFT (2026-10-27)

- Added an optional periodic Hann analysis window to the offline real FFT, coherent-gain-corrected one-sided amplitude, original/windowed sample metadata, UI selection and stale-export invalidation. Preserved rectangular default. Added numerical reference, negative and browser UI/table regression in mandatory Quality; source/standalone synchronization verified. Dev candidate only until exact-head CI/PR/main/Pages gates pass.

## Unreleased — bounded real symmetric matrix eigenanalysis (2026-10-27)

- Added offline 2×2/3×3 Jacobi eigenvalues and orthonormal eigenvectors in the Matrix calculator, sorted spectrum, editor handoff and residual diagnostics. Added dedicated positive/negative/reference browser regression to mandatory Quality, plus documentation. Isolated JavaScript numerical references passed; exact-head full CI and Pages still pending.

## Unreleased — FFT frequency metadata and graph regression repair (2026-10-27)

- Added binWidthHz and nyquistHz API/UI metrics with focused browser reference, invalid rate and stale UI checks. Repaired Hz graph regression to access point objects (`.x`, `.y`), matching the actual Graphs API, without weakening expected values. Quality and Pages release still pending.

## Unreleased — FFT sample-rate frequency in Hz (2026-10-27)

- Added validated FFT sample-rate control, frequency_Hz spectrum columns and physical-frequency graph axis. Added dedicated Playwright tests for Hz references, bad sample rates, UI state and table/graph handoff. Exact-head CI and Pages verification pending.

## Unreleased — offline real-signal FFT (2026-10-27)

- Added bounded offline 4–256-sample radix-2 FFT, one-sided amplitude spectrum, inverse round-trip check, Data Tables/Graphs handoff, dedicated browser/reference regression and structural CI checks. Local isolated Chromium harness passed; full repository Quality and Pages remain pending.

## Unreleased — symbolic first-order ODE initial conditions (2026-10-27)

- Added optional one/two first-order SymPy ODE initial values: `diff(y(t),t)=y(t)` with `y(0)=1` → `y(t)=exp(t)`. Reject invalid functions/points/values, duplicate times, and contradictory overdetermined conditions.
- Added worker payload, generated Python, project export/import validation, documentation and direct embedded-SymPy/browser regression. Dev only until CI/PR/main/Pages gates pass.

## Unreleased — graph pan CI regression: viewport-relative pointer targeting (2026-10-27)

- Corrected 3D navigation's Playwright regression to click Pan first, scroll the canvas into view, recompute its bounding box and verify pointer hit-testing before dragging. Earlier real CI failures at PR runs 40522983794 and 40526526435 had panning stuck at (0, 0), consistent with stale screen coordinates after scrolling. The assertion remains strict about actual pan X/Y and zoom; this is a test repair, not an assertion bypass.
- Added GitHub Actions concurrency grouping by event and branch/PR to cancel superseded checks without disabling required full QA. All current dev and PR head checks must still pass before promotion.

## Unreleased — high-precision scientific output display (2026-10-27)

- Added optional scientific-notation display for high-precision decimal and expression results, preserving full decimal output, exactness and offline BigInt calculations. Toggling refreshes previous results; numerical reference and browser UI tests extend the existing mandatory Quality suite. Full CI/Pages verification pending.

## Unreleased — correct exact-division check for long decimal outputs (2026-10-27)

- Fixed false input-limit rejection when two valid ≤300-digit operands yield an exact quotient longer than 300 digits (up to the 800-character output cap). Internal exactness validation now uses an 800-digit result limit; user input remains limited to 300 digits. Added focused browser/reference regression and mandatory CI step. Production release still pending verified checks.

## Unreleased — bounded high-precision integer powers (2026-10-27)

- Added exact integer `^` powers (0–20) to offline decimal expressions, right-associative chains, ordinary unary precedence and rejection of `0^0`/negative, fractional or out-of-range exponents. Browser regression covers positive and invalid cases; full CI, PR and Pages remain pending.

## Unreleased — strict decimal expression token boundaries (2026-10-27)

- Fixed high-precision expression parsing so whitespace cannot concatenate separate numeric literals (`1 2`, `1 .2`) into a different number. Legitimate spaces between operators and parentheses remain supported. Added focused browser regression cases; full CI and deployment pending.

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

## 2026-10-28 — Group secondary Calculator and Editor actions (released via PR #37)

- Group low-frequency Calculator copy/result-transfer and Editor copy/Word export buttons in keyboard-accessible native disclosures; primary actions remain visible and original event listeners are retained.
- Add Playwright browser coverage for actual Word download, answer routing, clipboard fallback, keyboard and mobile layout; dev Quality 40606508008, PR Quality 40606906734, main Quality 40607265984 and Pages 40607265308 passed; main `137b008c583ee9f938430f5dd02cee4bb7df585a`. Independent hosted interactive smoke remains unavailable.


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

- Corrected standalone Calculator task selector to expose the existing High precision form; added exact bundled/source static regression to prevent future task-menu drift. Requires exact CI and Pages verification before release.
