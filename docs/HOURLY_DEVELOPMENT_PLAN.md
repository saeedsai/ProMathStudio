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
| 1 | P0-SYMBOLIC-SYSTEMS | Extend Symbolic Solver **Solve system** from linear `linsolve` to nonlinear symbolic systems via a safe SymPy operation selector or robust auto-detection. Preserve linear/free-parameter path. | Test `x^2+y^2=5; x-y=1` returns both signed real pairs (or complete equivalent set) and `x=2x+2z; y=x-z` still returns free-variable family; include inconsistent/invalid systems and safe AST limits. | TODO |
| 2 | P0-MATRIX-UI | Introduce first-class 2D matrix input and determinant/transpose/inverse with exact/approximate output in Calculator or Solver; keep matrix types distinct from existing display templates. | Verify identity, invertible/singular matrices, 2×2/3×3 determinant, transpose; do not claim generalized LA yet. | TODO |
| 3 | P0-NUMERIC-ODE | Add user-facing numerical ODE initial value solver for `y'=f(t,y)` with basic RK4 and explicit interval/initial condition controls, result table and graph handoff. | Reference `y'=y,y(0)=1` against `exp(t)`, step sensitivity and invalid inputs; do not misrepresent as stiff/general solver. | TODO |
| 4 | P0-CUSTOM-PY-COMPOSE | Permit nested/custom Python function calls within Calculator expressions (e.g., `2*myfun(3)+1`) with async worker bridge; keep worker isolation, time limits and formula behavior. | Conditional Python multi-line function returns and nested expression, errors/timeouts/cancellation, no regressions in Formula/Graph/Data Tables. | TODO |
| 5 | P0-SHEET-REFERENCE | Protect spreadsheet formulas during insert/delete/duplicate row/column and sort; implement explicit reference transformation or safe refusal, with cross-sheet rules documented. | Test A1-style references, sheet-qualified refs, ranges, edge shifts and cyclic/error cases. | TODO |

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
- [ ] Ensure Quality checks run on `dev` and `main` pushes and PRs, with all existing regressions.
- [ ] Add automated, **merged-only/no-open-PR** cleanup of legacy branches, if permitted; retain unique/unmerged commits and `dev`/`main`.
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

## Execution record

**2026-10-26 initialization (setup session)** — Inspected existing `main` `4cbb99e215b4e6071633866261244feaceecc09c`, green quality and Pages deploy. Added `dev` and permanent instructions. GitHub Pages publishing is main-branch-based, while `.github/workflows/pages.yml` is optional manual deployment. Establishing workflow checks and merged-only branch cleanup is the initial reliability deliverable. See subsequent commits and CI logs for verified outcomes; the run remains IN PROGRESS until those checks finish.
