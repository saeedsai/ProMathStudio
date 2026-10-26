# ProMathStudio — Hourly Development Plan & Execution Ledger

**Living plan** · initialized 2026-10-26 · authoritative operating rules: [AGENTS.md](../AGENTS.md).  
**Frozen scope baseline:** [26 Oct 2026 feature/gap audit](FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md) — 158 current feature classifications (63 complete / 95 partial) and 166 missing/expansion opportunities. The audit is not a mathematical feature-count guarantee.

## Objective and workflow

Run **once every hour indefinitely**. Each run picks a narrowly bounded item, adds implementation + regression tests on **dev**, verifies exact SHA in CI, promotes via PR to **main** only after passing checks, validates deployment, documents progress, and refreshes the next five. Carry over unfinished items without downgrading their tests. The GitHub Pages site is published from `main`; the existing manual Pages workflow is optional. Do not confuse a green PR with verified production. The agent cannot guarantee uninterrupted execution in outages, platform limits or when safety/permissions prevent an action.

**Statuses:** TODO, IN PROGRESS, DEV IMPLEMENTED, CI GREEN, RELEASED, BLOCKED, PARTIAL.  
**Meaning of RELEASED:** exact code shipped to main, all required CI checks green, production deployment verified. Source change alone is not release.

## Next five features (refreshed each scheduled run)

| Order | ID | Next bounded implementation | User acceptance / regression requirements | Status |
|---:|---|---|---|---|
| 1 | P0-MATRIX-UI | Add a bounded 2×2 / 3×3 **Matrix calculator** panel with input grids, determinant, transpose and inverse. | Identity, zero, singular, nonsymmetric and invertible reference matrices; reject non-square inverse, cross-workspace regression. | TODO |
| 2 | P0-NUMERIC-ODE | Add a first-order initial value **RK4 ODE** panel with t/y initial conditions, finite-step controls, table and graph output. | Reference `y'=y, y(0)=1` to `exp(t)`, convergence with step refinement, invalid data/domain and plot regression. | TODO |
| 3 | P0-CUSTOM-PY-COMPOSE | Support async Python custom-function composition in ordinary Calculator expressions, including nested calls. | `2*myfun(3)+1`, multi-arg, failure/cancellation/timeout and Formula regression. | TODO |
| 4 | P0-SHEET-REFERENCE | Preserve or safely adjust A1/worksheet references for row/column insert/delete and sort. | Local/cross-sheet/range references, absolute references if supported, cyclic references and data integrity. | TODO |
| 5 | P0-SYMBOLIC-LIMITS | Add one-sided/two-sided/infinite symbolic **limits** to SymPy solver UI with valid domain/variable/direction controls. | `sin(x)/x` → 1 at 0, removable discontinuities, left/right divergence, assumptions and error paths. | TODO |

**Always choose critical correctness/security regressions before planned features.** The next-five list is a moving queue, not a guarantee that each feature takes exactly one hour. As an item is released, select the next P0 from the frozen audit; then systematically work through P1/P2/P3 and the 95 partially complete items. Do not abandon the ledger because of an unsuccessful run.

## Higher-level release sequence

1. **Foundation and completeness — P0:** math typing/domains, symbolic systems, matrix operations, precision, limits, IVP numerical ODEs, composable Python, import/project schema resilience, XLSX, spreadsheet formula integrity and rigorous unit/browser/reference tests.
2. **Everyday numerical/scientific software — P1:** constrained optimization and fitting, vector calculus, interpolation, quadrature, statistics, parametric/polar/implicit/contour/vector plots, FFT and ODE conditions.
3. **Advanced scientific computing — P2:** eigen/sparse LA, DAE/BVP/stiff methods, multivariate optimization, signal/control, FEM/mesh workflows, scientific data formats and analysis tools.
4. **Broad ecosystem capabilities — P3:** parallel/GPU, model-based simulation, machine learning, image, engineering/industry modules. Break massive MATLAB/toolbox functionality into independently tested, explicitly scoped deliverables.

## CI/CD and branch hygiene setup (initialization)

- [x] Inspect current main, source inventory, tests, existing CI and Pages automation (2026-10-26).
- [x] Create `dev` from latest validated `main` before development work.
- [x] Commit durable root `AGENTS.md` and initialize this plan.
- [x] Ensure Quality checks run on `dev` and `main` pushes and PRs, with all existing regressions.
- [x] Add automated, **merged-only/no-open-PR** cleanup of legacy branches after main updates; check actual action permissions/results after merge.
- [ ] Require release PR with green SHA-specific checks and verified Pages after every merge; configure branch protection in repo Settings if permissions permit.
- [ ] Verify branch-cleanup outcome and both refs survive promotions. Existing extra refs at initialization: `feature/custom-functions-multi-data-series`, `feature/per-function-graph-styles`, `feature/real-python-custom-functions`, `feature/ui-equation-systems`, `fix/conditional-custom-function-parser`, `fix/conditional-parser`. No open PRs at initial inspection.

### Normal execution record template (append once **per run**)

```text
Date/hour:
Chosen feature ID + bounded acceptance target:
dev SHA before/after and exact changed files:
New regression test(s) and full CI run URL/status:
main SHA / PR link / merge decision:
Pages build/deployment and live smoke results:
Blockers and authorized repairs (if any):
Cleanup changes and branch count:
Next five feature IDs in order:
```

## Current feature checkpoint

**P0-SYMBOLIC-SYSTEMS — DEV IMPLEMENTED / CI PENDING.** Source and tests implement bounded polynomial nonlinear systems (`sp.nonlinsolve`) under a new Auto/Linear/Nonlinear method selector. Linear/free-variable solutions retain `sp.linsolve`. Nonlinear accepts at most 3 unknowns/6 equations, max polynomial degree 4 and 80 terms. **Still partial** versus a general nonlinear/transcendental/inequality solver; no complete MATLAB parity claim. Source `index.html`; tests `tests/smoke_advanced_math.py`; explanation `docs/SYMBOLIC_ENGINE.md`; changelog updated. Acceptance: signed real solution pairs, explicit nonlinear method, linear mode refuses nonlinear input, contradictory system and degree cap, untouched linear underdetermined example.

## Execution record

**2026-10-26 initialization (setup session)** — Inspected existing `main` `4cbb99e215b4e6071633866261244feaceecc09c`, green quality and Pages deploy. Added `dev` and permanent instructions. GitHub Pages publishing is main-branch-based, while `.github/workflows/pages.yml` is optional manual deployment. Establishing workflow checks and merged-only branch cleanup is the initial reliability deliverable. See subsequent commits and CI logs for verified outcomes; the run remains IN PROGRESS until those checks finish.

**2026-10-26 CI/CD implementation** — Established `AGENTS.md`, this living plan, enabled push checks for `dev`, added conservative merged-only branch-hygiene workflow (runs only from trusted main), and new `tests/test_delivery_policy.py` regression. Hourly ChatGPT task enabled. **Release remains pending successful dev+PR CI and verified main Pages deployment**; do not claim leftover legacy branches removed until hygiene run confirms.

**2026-10-26 13:xx Europe/Stockholm — user-triggered hourly run / P0-SYMBOLIC-SYSTEMS**. Read `AGENTS.md`, living plan (temporarily missing during its setup commit, then retrieved on `dev`), frozen audit and CI. Baseline `main=4cbb99e215b4e6071633866261244feaceecc09c`; `dev` originally observed at `93edc61e8b2cee223f91a56a067013f25fcc42a1`, then additional initialization workflow/QA commits `52f5ad17` and `a2ecc944`. Selected bounded nonlinear symbolic polynomial system solving. Implemented source on dev `b38168cd` and fixed SymPy exception class `2abff534`; added focused test `1f2ca6dd`; docs `95dd9c03` and changelog `a6154107`. At ledger update, the exact source + test CI was running; deployment and PR pending exact-head green. Branch cleanup on main push only when safe; no manual unverified deletion. Next five: P0-MATRIX-UI, P0-NUMERIC-ODE, P0-CUSTOM-PY-COMPOSE, P0-SHEET-REFERENCE, P0-SYMBOLIC-LIMITS. This run must be amended with final SHA/run/PR/Pages evidence before reporting RELEASED.
