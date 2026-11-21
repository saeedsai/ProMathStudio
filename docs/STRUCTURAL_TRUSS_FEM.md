# 2D Truss Studio — canonical structural-truss-fem-2d

**Status:** solid, concentric hollow, open-channel and I-section property helpers implemented on dev; exact-head Quality pending; review and main Pages deployment unverified. Upgrade of the existing standalone `tools/truss-studio.html`, not a duplicate tool or an embedded main workspace control.

## How to use

Open `tools/truss-studio.html` in a browser (requires its adjacent `truss-fem.js` and `truss-fem-ui.js`). Select a reference model or edit **Joints**: unique ID, X/Y in metres, Fix X/ Fix Y, forces Fx/Fy in kN (positive right/up). In **Members**, enter start/end IDs, E in GPa, area in mm² and optional density in kg/m³. The **Section property helper** in the material breakdown calculates area and centroidal I for solid/hollow rectangles and circles, plus open channels and I-sections, then applies the selected centroidal moment to one member. Rectangle I is about the centroidal axis parallel to width; circle I is about a centroidal diameter. Optional Euler estimate inputs are I (second moment of area, mm⁴) and K (dimensionless effective-length factor); provide both to calculate Pcr. Either property may be stored alone without producing an Euler estimate; the geometry/member preview remains available and the status explains when the pair is incomplete. Click Analyze truss. Results show member tension/compression force (kN), stress (MPa), joint displacements (mm), support reactions (kN), residual/energy verification and, when I/K are supplied, a compression-only ideal Euler comparison. Gray dotted members represent the original truss; colored amplified lines represent deformed geometry (green tension, orange compression). Change scale or label visibility, export the model as JSON, results as CSV, diagram as SVG; imported legacy SI JSON is converted explicitly.

## Numerical contract

The FEM solver models 2D pin-connected, axial-only, linear-elastic, small-displacement trusses with static loads. Each bar stiffness is `EA/L * [-c,-s,c,s]^T [-c,-s,c,s]`; global K is assembled, fixed zero-displacement DOFs eliminated, free system diagonal-scaled and solved with pivoting. Member axial extension is projected relative endpoint displacement; positive axial stress is tension. Reactions are `K*u-F`. Force balance, free-DOF residual, and twice strain energy = external work are checked. The solver itself does not model geometric buckling, post-buckling, yielding, thermal loads or connection behavior.

## Section-property helper

The standalone helper uses dimensions in mm and returns area in mm² and centroidal second moments in mm⁴:
- Solid rectangle: A = b·h, Ixx = b·h³/12, Iyy = h·b³/12.
- Concentric hollow rectangle: subtract the centered inner rectangle from the outer rectangle for A, Ixx and Iyy.
- Solid circle: A = π·d²/4, Ixx = Iyy = π·d⁴/64.
- Concentric hollow circle: subtract the inner circle from the outer circle for A and equal centroidal I.
- Open channel: the web is on the left and both flanges extend right. It is assembled from a full-height web and two non-overlapping flange rectangles.
- I-section: two full-width flanges and a centered non-overlapping web rectangle.

For channel and I-section, the helper computes the composite area centroid and both centroidal principal moments with the parallel-axis theorem. The channel centroid is reported from the outside web face and bottom edge; the I-section centroid is centered for symmetric inputs. Select Ixx (horizontal centroidal axis) or Iyy (vertical centroidal axis) before applying the selected value to the member. The open-section geometry assumes sharp corners, uniform web/flange thickness, no lips, no fillets and no eccentricity. It does not calculate shear centre, torsional constant, shear area or local-axis orientation of the installed member.

All dimensions must be finite and strictly positive, with web thickness smaller than B and two flange thicknesses smaller than H. Area and moments that underflow or overflow are rejected before any member is changed. Applying a valid result updates only the selected member's area and I; E, density, K and other members are preserved. The formulas describe ideal prismatic cross-sections, not code-compliant resistance or buckling checks.

## Optional ideal Euler member estimate

The non-solving material preview can report the ideal elastic critical load `Pcr = π² E I / (K L)²` when both second moment of area `I` and effective-length factor `K` are supplied. Current Studio JSON/UI uses `I` in mm⁴; legacy SI JSON uses `I` in m⁴ and converts it on import. `K` is dimensionless. The reported `Pcr` is in kN. Missing I/K leaves the estimate blank; supplying only one, non-positive/non-finite values, or an unrepresentable result is rejected. After solving, only compressive axial force is compared with `Pcr`; the result reports utilization `Pcomp/Pcr` and load ratio `Pcr/Pcomp`. Tension is not applicable and zero force is reported as no compression demand without division. This remains an ideal elastic screen, not a geometric buckling solver or code-compliant resistance check; it does not include imperfections, residual stress, local/flexural-torsional modes, inelasticity, code resistance factors or post-buckling. It is an educational idealization, not a certified design check; consult a qualified structural engineer.

## Compatibility

Previous TrussStudio API still exposes `TrussStudio.solve(model)` and `TrussStudio.example` with SI N/Pa/m² units and legacy output shape. The UI now accepts kN/GPa/mm². JSON import recognizes legacy member field `A` (m²) and converts load forces in N, E in Pa, and A in m² to the new form; exported JSON uses explicit new-form keys and units. Existing `index.html` distribution and source/bundle hashes are unchanged, but the companion page requires its relative JS assets, including for offline use.

## References and tests

- Single 2 m bar: E=200 GPa, area=1000 mm², +1 kN, displacement 0.01 mm, axial stress 1 MPa, reaction -1 kN. With I=1,000,000 mm⁴ and K=1, the ideal Euler Pcr reference is approximately 493.480220 kN.
- Three-bar triangle: legacy 10 kN load, member forces +5 kN in bottom chord and -7.0710678 kN on each diagonal, support reactions +5 kN each; +20 kN form example with 4 m span has +10 kN reactions each.
- Node bounds 2–80, members 1–240, maximum 150 free DOFs. Reject missing/free restraints, invalid IDs/endpoints, zero lengths, nonfinite input and zero/negative E/A.
- node --test tests/test_truss_fem.js: analytical references, stiffness/load scaling, equilibrium, invalid geometry and mechanisms; solid/hollow rectangle/circle and channel/I-section area, centroid, principal-moment and underflow/overflow references.
- `python tests/smoke_truss_fem.py`: reference solver, browser editing/recovery, SVG, generated export content, desktop/mobile layout and console errors.
- `python tests/smoke_truss_studio.py`: original 10 kN SI reference and legacy JSON import, old API compatibility, exports and responsive recovery. Browser CI tests inline the same JS files because sandboxed Chromium blocks `file://`; hosted deployment must separately confirm relative asset loading and actual downloads.
