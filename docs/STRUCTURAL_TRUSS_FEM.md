# 2D Truss Studio — canonical structural-truss-fem-2d

**Status:** locally tested on dev; CI, review and main Pages deployment unverified. Upgrade of the existing standalone `tools/truss-studio.html`, not a duplicate tool or an embedded main workspace control.

## How to use

Open `tools/truss-studio.html` in a browser (requires its adjacent `truss-fem.js` and `truss-fem-ui.js`). Select a reference model or edit **Joints**: unique ID, X/Y in metres, Fix X/ Fix Y, forces Fx/Fy in kN (positive right/up). In **Members**, enter start/end IDs, E in GPa and area in mm². Click Analyze truss. Results show member tension/compression force (kN), stress (MPa), joint displacements (mm), support reactions (kN), and residual/energy verification. Gray dotted members represent the original truss; colored amplified lines represent deformed geometry (green tension, orange compression). Change scale or label visibility, export the model as JSON, results as CSV, diagram as SVG; imported legacy SI JSON is converted explicitly.

## Numerical contract

This solver models 2D pin-connected, axial-only, linear-elastic, small-displacement trusses with static loads. Each bar stiffness is `EA/L * [-c,-s,c,s]^T [-c,-s,c,s]`; global K is assembled, fixed zero-displacement DOFs eliminated, free system diagonal-scaled and solved with pivoting. Member axial extension is projected relative endpoint displacement; positive axial stress is tension. Reactions are `K*u-F`. Force balance, free-DOF residual, and twice strain energy = external work are checked. Physical buckling, geometric nonlinearity, material yielding, thermal loads, connection design, code compliance and safety factors are OUT of scope. For real structures verify with a qualified engineer.

## Compatibility

Previous TrussStudio API still exposes `TrussStudio.solve(model)` and `TrussStudio.example` with SI N/Pa/m² units and legacy output shape. The UI now accepts kN/GPa/mm². JSON import recognizes legacy member field `A` (m²) and converts load forces in N, E in Pa, and A in m² to the new form; exported JSON uses explicit new-form keys and units. Existing `index.html` distribution and source/bundle hashes are unchanged, but the companion page requires its relative JS assets, including for offline use.

## References and tests

- Single 2 m bar: E=200 GPa, area=1000 mm², +1 kN, displacement 0.01 mm, axial stress 1 MPa, reaction -1 kN.
- Three-bar triangle: legacy 10 kN load, member forces +5 kN in bottom chord and -7.0710678 kN on each diagonal, support reactions +5 kN each; +20 kN form example with 4 m span has +10 kN reactions each.
- Node bounds 2–80, members 1–240, maximum 150 free DOFs. Reject missing/free restraints, invalid IDs/endpoints, zero lengths, nonfinite input and zero/negative E/A.
- `node --test tests/test_truss_fem.js`: analytical references, stiffness/load scaling, equilibrium, invalid geometry and mechanisms.
- `python tests/smoke_truss_fem.py`: reference solver, browser editing/recovery, SVG, generated export content, desktop/mobile layout and console errors.
- `python tests/smoke_truss_studio.py`: original 10 kN SI reference and legacy JSON import, old API compatibility, exports and responsive recovery. Browser CI tests inline the same JS files because sandboxed Chromium blocks `file://`; hosted deployment must separately confirm relative asset loading and actual downloads.
