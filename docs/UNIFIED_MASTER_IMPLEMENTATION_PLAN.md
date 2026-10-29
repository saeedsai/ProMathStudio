# ProMathStudio — Unified Master Implementation Plan

**2026-10-29. Status: planning, not implementation.** Canonical repo: saeedsai/ProMathStudio, development on dev, validated release on main. Preserve the standalone offline index.html and scripts/build.py.

## Scope and truthful counting

The 2026-10-26 audit recorded 158 present capabilities (63 complete within stated scope, 95 partial) and 166 gaps/improvement opportunities (22 P0, 64 P1, 53 P2, 27 P3). New engineering catalogs have **1,368 overlapping entries/families**: original six engineering disciplines 148; Control Theory 181; GNSS 144; Signal Engineering 177; Cryptography 145; Electromagnetics 163; Statistics 80; Data Science 90; Materials & Alloys 80; Structural 80; AI/ML 80. An additional 19 electrical/electronics backlog items and 22 candidate disciplines are tracked separately. These figures are NOT additive unique features and cannot yield an accurate completion percentage. First audit and deduplicate by canonical computation, UI behavior and requirement granularity; preserve links to all original subfeatures.

## Product and toolbox structure

Preserve Calculator, Equation/Symbolic Solver, Graphs 2D/3D, Data Tables, saved projects and notebook. Reconcile current UI with source before consolidating the Equation workspace. Add one Engineering Toolbox workspace with searchable discipline/category navigation. The **15 documented disciplines** are Physics, Mechanical, Electrical, Electronics, Fluids, Aerospace, GNSS, Signals, Cryptography, Electromagnetics, Statistics, Data Science, Materials & Alloys, Structural and AI/ML. **Control Theory must also have its own visible toolbox selection**, sharing common algorithms: 16 selections total if cross-disciplinary Control is displayed independently. The 22 additional candidate domains are review-only, not approved implementations.

Tool UI: search, favorites, recent, examples, input validation and units, one contextual Run/Solve/Plot/Save/Export/Help bar, accessible mobile/desktop layouts, responsive forms, consistent light/dark design, keyboard and screen reader support. Planned tools must be visibly marked unavailable, not fake working buttons.

## Canonical shared engines

| Reusable package | Scope | Cross-toolbox reuse |
|---|---|---|
| expressions/CAS | AST, parser, symbols, equation transformations, assumptions, MathML/LaTeX/Python export | Equation, Calculator, all engineering |
| numerics | Real/complex arithmetic, differentiation, quadrature, interpolation, roots, tolerances | Math, physics, mechanical |
| linalg | Dense/sparse matrices, decompositions, eigenproblems, least squares | Structures, circuits, GNSS, AI, control |
| solvers | Nonlinear equations, ODE, BVP, PDE, FEM adapters, optimization | Fluids, EM, aerospace, structural |
| graphs | 2D/3D rendering, plot specs, axes, legends, cursor, scientific adapters | Every toolbox |
| data | Dataframes, joins, CSV/JSON/binary, streaming, provenance | Data Science, signals, GNSS, statistics |
| signals | FFT, transforms, filters, resampling, spectral estimates | Signals, GNSS, electronics, EM, control |
| estimation | Covariance, WLS, Kalman/UKF, sensor fusion | GNSS, robotics, control, AI |
| statistics | Distributions, tests, regression, DOE, uncertainty, reliability | Statistics, AI, materials, structures |
| optimization | Constrained/unconstrained solvers, sensitivities, parameter sweeps | Mechanical, aerospace, energy, AI |
| physics | Units, dimensional analysis, material properties, coordinates | All engineering |
| simulation | State-space, integration, events, model coupling, Monte Carlo | Control, flight, mechanical, thermal |
| IO/security | Versioned project formats, exports, validation, vetted cryptographic adapters | All |
| UI/registry | Stable IDs, schemas, tool shell, actions, navigation, status | All |

One canonical function with toolbox-specific adapters and presets. Examples: solveLinear(A,b) for circuits, GNSS and structural stiffness; solveODE for flight, control and thermal; FFT for signals, radar, GNSS and EMC; Kalman for GNSS/INS and tracking; plot(spec,data) for Bode, root locus, stress-strain and trajectories. Prefer pure functions, no DOM in solver code, explicit contracts, and classes only for necessary stateful engines. Preserve existing APIs and saved data with adapters. Benchmark bundle size, load time and memory; do not assume module splitting alone makes the application smaller.

## Feature ledger and hierarchy

Create machine-readable ledger with canonical ID, parent family, toolbox aliases, description, input/output schema, units, domain assumptions, dependency IDs, priority, effort, acceptance tests, status, source path, test path, release SHA and documentation. Statuses: planned, specified, in progress, partial, implemented, verified, released; blocked separately. Each high-level catalog item expands to bounded low-level capabilities with reference examples and test cases. Mark overlapping entries as references to the same solver. Do not mark a tool as implemented merely because it can be manually coded in Python.

## Mathematical backlog priorities

**P0:** correctness of existing parser/AST, numerical domain and residual handling, worker safety, source/bundle parity, CI and regressions. **P1:** matrix/vector/complex operations; symbolic algebra and equation systems; calculus and transforms; nonlinear roots and numerical integration; complex 2D/3D graphs; rich graph modes; data import and plots; initial/boundary conditions for ODE/PDE; optimization. **P2:** sparse linear algebra, advanced eigenproblems, stiff ODE, BVP, 2D/3D PDE/FEM, uncertainty and automatic differentiation, scientific Python interoperability, high-performance plotting. **P3:** advanced symbolic/physical modeling, large multiphysics solvers, high-end CFD/EM and specialist validated toolboxes. Map all 166 audited gaps and 95 partial capabilities individually to these tracks.

## Phases and rough single-engineer estimates

| Phase | Deliverable | Approximate dedicated full-time effort |
|---|---|---|
| 0 | Audit source, original detailed catalogs, CI and deduplicated ledger | 3–6 weeks |
| 1 | Fix P0 defects, baseline tests and offline build | 6–12 weeks |
| 2 | Tool registry, reusable core, UI shell, safe incremental refactor | 8–16 weeks |
| 3 | Complete P1 math, graphing, Equation and data capabilities | 16–32 weeks |
| 4 | Engineering Toolbox navigation and first validated shared vertical slices | 12–24 weeks |
| 5 | Broad practical functionality across all 16 toolbox selections | 24–52 weeks |
| 6 | Advanced PDE/FEM, simulation, AI, precise GNSS, advanced EM, optimization | 36–78+ weeks |
| 7 | Specialist depth, new candidate domains, standard-specific validation | Ongoing |

Phases can overlap; do not sum durations mechanically. Assumptions: one dedicated experienced full-time engineer, functional CI, mature libraries, approximately 30–40 productive hours/week. Estimated **9–18 months** for a usable modular platform with meaningful engineering tools, **24–48 months** for broad practical coverage of 16 toolbox selections, and **48–84+ months** for deep advanced catalog coverage plus candidate domains. These are scenario estimates, not promises. Hourly ChatGPT task runs are NOT equivalent to full-time engineering capacity; measure throughput and revise quarterly. A staffed specialist team could shorten some milestones but not proportionally.

## Priority order and first vertical slices

Always fix high-severity correctness/security failures first. Otherwise rank user value, cross-toolbox reuse, dependency unblocking and effort; do not choose based on catalog order. Recommended first shared slices: (1) registry plus existing tool migration; (2) shared matrix solver used by circuits and GNSS/structures; (3) common graph adapters for math, control and statistics; (4) FFT and filtering for signals/GNSS/EM; (5) regression/statistics for data science and materials; (6) ODE/state-space for control, aerospace and mechanical; (7) units/material property models for physics, mechanical and structures. Finish each vertical slice end to end before multiplying incomplete placeholders.

## Verification and validation

Every numerical kernel: analytical or independent reference result, tolerance, residual, domain assumptions, units, boundary/singular and invalid-input tests, deterministic seed and documented precision. Add property/metamorphic tests (linearity, conservation, transform inverses), regression tests, integration tests and cross-toolbox equivalence tests. Validate physical models against published benchmark problems or measurements when possible; do not claim certification for structural, biomedical, cryptographic, GNSS-integrity or power-safety results without domain-specific review.

Every release: source/bundle parity, offline boot, project save/reload, existing feature regression, browser/mobile keyboard/accessibility smoke, no duplicate action controls, no critical errors, performance/bundle budgets, green CI for exact dev SHA, authorized dev→main PR, then deployment and hosted QA verification. Never bypass branch protection or describe a dev commit as a live deployment.

## Next five implementation tasks

1. Create canonical deduplicated ledger and import/link the 158/166 audit, all catalog entries and original detailed six-discipline files.
2. Baseline current source structure, duplicated implementations, tests, build size, performance, CI and saved project compatibility.
3. Build registry for **existing implemented tools first**, validate unique IDs, cross-toolbox aliases, input/output schemas and statuses.
4. Build reusable tool shell and contextual action bar; remove duplicate buttons without removing any underlying functionality.
5. Extract one existing solver into a shared pure module; demonstrate reuse in two workspaces with numerical and UI regression tests.

## Development cadence and definition of done

Hourly scheduled runs: inspect latest dev/main, AGENTS.md, this plan, audited inventory and CI; select a bounded dependency-ready feature; search for existing implementation; implement source + tests + docs; commit to dev; attempt safe PR promotion after green checks; report exact status. Continue independent compatible dev work while a release is pending. Reprioritize weekly, reconcile catalogs monthly, revise estimates quarterly.

A feature is released only with validated behavior, canonical implementation, input/output and units, reference/negative tests, accessible UI, docs, saved-project regression, green CI, authorized merge and verified deployment. Documentation alone is **planned**.
