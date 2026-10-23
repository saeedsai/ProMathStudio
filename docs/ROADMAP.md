# Roadmap and priorities

This roadmap lists **future work**, not functionality guaranteed in the current build.

## P0 — Reliability and product quality

- [ ] Broaden test corpus for operator precedence, transformations, high-degree roots, domain constraints and complex branches.
- [ ] Set up release tagging/version display and end-to-end GitHub Pages smoke checks after deployment.
- [ ] Improve error messages for unsupported AST/CAS/graph operations.
- [ ] Harden project import validation, version migration and resilient localStorage handling.
- [ ] Evaluate explicit-content CSP and dependency integrity for production hosting.

## P1 — Cross-workspace mathematics

- [ ] Preserve exact symbolic types (rather than only strings) across all tools.
- [ ] Add multi-variable substitutions, parameter controls, assumptions and variable dependencies.
- [ ] Show calculation steps where SymPy supplies trustworthy transformations.
- [ ] Unified history and undo/redo that spans editor, calculator, solver and graphs.
- [ ] Compare symbolic and numerical graph roots.

## P2 — Plotting and advanced algebra

- [ ] Implicit curves `F(x,y)=0`, parametric curves and polar plots.
- [ ] Plotting of functions with parameters/sliders and large arrays of points.
- [ ] Multiple 3D surfaces and improved touch navigation.
- [ ] Matrices: determinant, inverse, eigenvalues, linear systems and matrix algebra UI.
- [ ] Higher-order/multivariable derivatives, integrals, ODEs/PDEs where practical.

## P3 — Packaging and collaboration

- [ ] Modularize the single-file JavaScript while preserving a zero-build distributable HTML.
- [ ] Add installable PWA/offline-cached Pyodide package option (observe licensing/download size).
- [ ] Import/export more math formats and improve Word round-trip compatibility.
- [ ] Optional cloud synchronization only with explicit privacy/storage design.

## Definition of done for new features

A feature needs a user-facing implementation, documentation update, automated tests where feasible, checked desktop/mobile behavior, and a recorded changelog entry. Do not claim deployment until the published site has been verified.

## Future advanced mathematics

- [ ] Add initial/boundary conditions to ODE/PDE operations where supported by SymPy.
- [ ] Explicit 2D/3D PDE numerical solvers with discretization/boundary conditions and error diagnostics.
- [ ] Weighted and robust regression, confidence bands, residual charts, and outlier controls.
- [ ] Richer drag-and-drop contextual tool navigation with accessibility testing.
