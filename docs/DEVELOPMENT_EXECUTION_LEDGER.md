# ProMathStudio — Living Development Execution Ledger

Baseline: 158 present (63 bounded complete, 95 partial), 166 gap/improvement opportunities (22 P0, 64 P1, 53 P2, 27 P3). Engineering catalog counts overlap; not a unique completed feature count.

| ID | Feature | Status | Evidence |
|---|---|---|---|
| MATH-MATRIX-WLS-UI-001 | Interactive weighted QR least-squares for 3×2 real matrices | Released via PR #95; dev/main Quality and Pages success at 352c1dd8549beb8cb0707012b7bd466d1fcd25c1; independent live-browser check unavailable | src/matrix-tools.js, index.html, tests/smoke_matrix_weighted_least_squares.py, .github/workflows/quality.yml |
| MATH-MATRIX-WLS-RHS-002 | Strict decimal RHS and positive weight input types for QR least-squares | Released via PR #96; dev/main Quality and Pages success at 5573801dfc87c2c0a093e7e81ebba7ebbc5e4028; live browser unverified | src/matrix-tools.js, index.html, tests/test_weighted_least_squares_rhs_validation.py; 51 V8 numerical assertions passed |
| MATH-ODE-RK45-DIAG-005 | Adaptive RK45 derivative stage/time/state diagnostics | Implemented on dev; full CI/PR/Pages pending | src/ode-tools.js, index.html, tests/test_ode_rk45_diagnostics.py, tests/smoke_ode_rk45_diagnostics.py, quality.yml |
| MATH-ODE-RK45-TIME-RESOLUTION-004 | Large-epoch representable-step and exact-endpoint RK45 integration | Implemented on dev; exact-head CI and PR/Pages pending | src/ode-tools.js, index.html, tests/test_ode_rk45_endpoint.py, tests/smoke_ode_rk45_endpoint.py |
| MATH-ODE-RK4-BACKWARD-001 | Backward scalar RK4 initial-value problems | Released via PR #91; main and Pages Quality green at f5ce020595ec0c0d8e6dcbae4a8301afaf505535 | src/ode-tools.js, index.html, tests/test_ode_backward.py, tests/smoke_ode_backward.py |
| MATH-ODE-RK45-BACKWARD-002 | Backward scalar adaptive RK45 initial-value problems | PR #92 merged at 04886109013b08cde9e312933a8b74ab842406be; dev/PR CI green, Pages workflow succeeded, main Quality pending at checkpoint | src/ode-tools.js, index.html, tests/test_ode_rk45_backward.py, tests/smoke_ode_rk45_backward.py |

| MATH-ODE-RK4-SYSTEM-BACKWARD-003 | Backward coupled RK4 two-state IVPs | Implemented on dev; exact-head CI/PR/Pages pending | src/ode-tools.js, index.html, tests/test_ode_system_backward.py, tests/smoke_ode_system_backward.py |

## 2026-10-29 — RK45 derivative stage diagnostics execution checkpoint

Read root AGENTS contract, current plan, frozen audit and exact-head GitHub Actions. Pre-change `dev=main=5573801dfc87c2c0a093e7e81ebba7ebbc5e4028`, two branches, no open PR, latest dev/main Quality and Pages green. Added stage-specific derivative errors in bounded scalar RK45, preserving accepted step calculation and stale-export invalidation; new direct numerical and browser regressions and mandatory Quality gate. Local V8 numerical reference/error tests passed. Full Python/Chromium and release gates to be verified at committed candidate SHA; GitHub branch protection remains unconfigured. No unrelated files deleted. Next-five acceptance queue is at top of hourly plan.

## 2026-10-29 — QR least-squares strict-input execution checkpoint

Pre-change dev/main: `352c1dd8549beb8cb0707012b7bd466d1fcd25c1`, no open PR. Latest main [Quality 40938128712](https://github.com/saeedsai/ProMathStudio/actions/runs/40938128712), dev [Quality 40938172409](https://github.com/saeedsai/ProMathStudio/actions/runs/40938172409) and [Pages 40938128804](https://github.com/saeedsai/ProMathStudio/actions/runs/40938128804) succeeded. Found direct weighted API accepted `"0x10"`, `"0b10"` and `[2]` as RHS through JavaScript Number coercion. Fixed shared ordinary/weighted QR RHS parsing and weighted object/array coercion; preserved valid decimal and scientific notation, original QR method and 3×2 scope. Added `tests/test_weighted_least_squares_rhs_validation.py` and synchronized standalone `index.html`. Executed the exact new JavaScript test body against modified source in V8: 51 assertions passed (positive, invalid, large/small scales, near-singular). Full Python unittest/Chromium Quality, PR and Pages remain pending at this checkpoint; historical audit totals unchanged. No stale tracked files proven safe to remove. Current next-five acceptance gates are at top of hourly plan.

## 2026-10-29 — Weighted least-squares UI execution checkpoint

Read root contract, living plan, frozen inventory and GitHub Quality. Pre-change dev `581070060867f2e5302ce665e3ef6ee5dcbafc86`, main `5d7ddaae6a5ec3b6696afd84ecc5d660d63f271d`, no open PRs; prior exact dev Quality [40931054692](https://github.com/saeedsai/ProMathStudio/actions/runs/40931054692) passed full unit/browser gate. Implemented editable weighted 3×2 QR fitting in matrix UI and standalone bundle, added focused browser regression and CI step. GitHub CI for the final documentation commit, dev→main PR and Pages not yet verified at checkpoint. Existing baseline counts unchanged. Next five and acceptance in hourly plan.

## 2026-10-29 execution log

Read AGENTS.md, hourly plan, frozen inventory, latest CI and PR #91. Pre-change dev `1d750757621a94effb55428799154807cecc2cca`, main `2c286be5cefa164ffae6c27dad48db2eba74c465`. Existing [dev Quality 40902863476](https://github.com/saeedsai/ProMathStudio/actions/runs/40902863476) passed 105 steps. New candidate includes actual source, bundled HTML, regression tests, CI step, docs and changelog; exact-head CI and production deployment require post-commit verification.

Next five acceptance criteria: see top of docs/HOURLY_DEVELOPMENT_PLAN.md.

## 2026-10-29 — Reverse adaptive RK45 development checkpoint

Pre-change dev/main `f5ce020595ec0c0d8e6dcbae4a8301afaf505535`. Exact baseline [dev Quality 40909400149](https://github.com/saeedsai/ProMathStudio/actions/runs/40909400149), [main Quality 40909376915](https://github.com/saeedsai/ProMathStudio/actions/runs/40909376915), and [Pages 40909376443](https://github.com/saeedsai/ProMathStudio/actions/runs/40909376443) passed. Selected highest-feasible ODE correctness improvement, signed backward RK45; preserved forward path, updated source/standalone and focused static/browser regression. Candidate CI and release pending; no production claim. Next five and acceptance in hourly plan.

## 2026-10-29 — Reverse coupled RK4 checkpoint

Pre-change dev/main `04886109013b08cde9e312933a8b74ab842406be` after PR #92 merged. Dev and PR Quality at previous head `133e0d4a2561e31c58c49a56206b5620d13b40d2` passed; Pages workflow for `04886109013b08cde9e312933a8b74ab842406be` succeeded; main Quality was still running. Implemented reverse coupled RK4 with new static/Chromium regression, updated source and standalone, preserved forward checks, added CI step. Local V8 numerical source checks passed: oscillator errors 5.296e-7, 1.977e-9, 7.631e-12, reverse polynomial [0,-4.7610027899269713e-17,1.6108925530441487e-17]. Exact candidate CI and promotion still require verification.

## 2026-10-29 — RK45 time-resolution execution checkpoint

Read AGENTS.md, current plan, frozen 2026-10-26 audit, CI and open PRs. Pre-change dev/main `4dc28d966905431c91f8a242752a01a3755ee138`; [dev Quality 40920561431](https://github.com/saeedsai/ProMathStudio/actions/runs/40920561431), [main Quality 40920539776](https://github.com/saeedsai/ProMathStudio/actions/runs/40920539776) and [Pages 40920539516](https://github.com/saeedsai/ProMathStudio/actions/runs/40920539516) passed; open PR count zero. Fixed representable-step underflow and endpoint snapping in scalar RK45; added static and browser numerical/UI regression. Direct V8 source checks: 1-ULP and large-epoch forward/reverse constant-derivative errors below 3e-16, ordinary exponential errors below 1e-10, stiff 1-ULP underflow correctly diagnosed. Full unit/Chromium CI and release verification pending at checkpoint. See top of hourly plan for NEXT FIVE.
