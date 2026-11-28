## Hollow-circle cavity transition rounding

## Pre-solve Euler input readiness summary

Each member preview distinguishes four input states: `not-supplied` (neither I nor K was entered), `missing-I` (K only), `missing-K` (I only), and `ready` (both positive inputs are valid). The pure `summarizeEulerInputReadiness(memberMetrics)` API returns an immutable total and count for each state plus `complete`; it rejects unknown states rather than silently dropping a member. An empty list is not considered complete.

The pre-solve live status always reports the readiness counts. This includes the all-not-supplied case: it must not claim merely that the model is ready for analysis while omitting that no member can receive the optional Euler screen. A complete input set says that the inputs are ready, not that the structure is stable or safe; buckling assessment remains a separate post-solve ideal elastic compression-only screen with the limitations described above.

Direct Node tests cover all four states, all-missing, all-ready, empty input, immutable output and invalid status rejection. Registered Chromium tests verify all-missing, mixed, all-ready and reset summaries at 1280px and 390px. The companion Truss Studio browser smoke also verifies the 14-column preview schema: `Euler inputs` is column 13 and `Euler Pcr` is column 14 (zero-based indices 12 and 13).

For a concentric annulus, use direct dimensionless differences 1-r² and 1-r⁴ while the cavity area ratio r² is at most 0.5. In this range the remaining area and inertia factors are bounded below by 0.5 and 0.75, so subtraction is well-conditioned and avoids the extra multiplication rounding of complementary factors. When r² > 0.5, retain the factored radial-gap expression to protect near-unity thin walls.

The boundary fixture uses outer diameter 1 mm and inner diameter 0.5000000000000001 mm (the next binary64 value above 0.5 mm). The previous factored path returns area 0.589048622548086 mm² and inertia 0.046019423636569225 mm⁴; correctly rounded references from the exact binary64 input are 0.5890486225480861 mm² and 0.04601942363656923 mm⁴. Section modulus is 0.09203884727313846 mm³ and both radii of gyration are 0.2795084971874737 mm. Node and Chromium regressions verify these values, unchanged input dimensions, the former one-ulp loss, and preserve the existing near-unity thin-wall and sub-half-ulp cavity cases at 1280px and 390px. This is binary64 numerical-boundary coverage, not a physical design example.

## Legacy SI-to-current unit conversion underflow

Legacy Truss models express nodal forces in N and Young's modulus in Pa, while the current model uses kN and GPa. Conversion must not silently erase a nonzero binary64 source value when division by 1000 or 1e9 rounds it to zero. `fromLegacy()` now rejects those unrepresentable force/modulus inputs with a field-specific underflow error. Exact zero remains valid, and ordinary legacy values retain the original division operation and results. Other scaled properties retain their existing validation and property-specific diagnostics.

Node and Chromium regressions cover positive and negative `Number.MIN_VALUE` forces on both axes, a minimum-subnormal legacy modulus, exact zero, and ordinary `-10000 N → -10 kN` / `200 GPa → 200 GPa` normalization. This is a conversion-integrity guard, not arbitrary precision; the current model still uses binary64 kN/GPa values.
## Subnormal global stiffness products

Each global stiffness coefficient is assembled by first dividing member stiffnesses by the largest stiffness contributing to that coefficient, then multiplying the normalized values by their row/column direction cosines, summing with the existing compensated signed reducer, and restoring the stiffness scale once. This avoids double-rounding or losing individual subnormal products before their combined contribution is assembled. The resulting matrix and solver remain IEEE-754 binary64; this is not arbitrary-precision FEM.

A synthetic two-node model uses twenty identical diagonal members with length approximately 2.82842712474619e-12 m, E=1e-323 GPa and A=1e-15 mm². Each parsed member stiffness is the minimum positive binary64 value, 5e-324 N/m. For c=s=0.7071067811865475, the old left-to-right expression k*c*c rounds each member contribution up to 5e-324 N/m, while the single product k*(c*c) rounds to zero. The exact rational sum of the supplied binary64 stiffness and direction-cosine factors rounds to 10 minimum subnormals (5e-323 N/m); the old path assembles 20 (1e-322 N/m). With an applied load of 1000 minimum subnormals in N, the displacement reference is 100 m rather than the old 50 m. The Node and Chromium regressions also require zero force-balance residual, finite strain-energy verification, and all twenty member results at 1280px and 390px. These are numerical stress fixtures, not physical structural dimensions.

## Compensated global stiffness assembly

The FEM assembler collects every finite member contribution to each global stiffness-matrix coefficient before summing that coefficient with the existing `finiteSignedSum` helper. This avoids sequential `+=` losing several individually sub-ulp parallel-member stiffness terms that together change the rounded coefficient. Same-sign terms use Neumaier compensation in original units; mixed-sign terms use an exact sum of the supplied binary64 terms when BigInt is available and the existing scaled compensated fallback otherwise. The matrix and solve remain IEEE-754 binary64; this is not arbitrary-precision FEM.

A synthetic horizontal-bar boundary fixture uses one member with stiffness (10^{16}) N/m and twenty parallel members with stiffness 1 N/m each. Ordinary sequential addition returns (10^{16}) N/m, while the correctly rounded aggregate is (10^{16}+20) N/m. With a (10^{16}) N axial load, the displacement must agree within (2\times10^{-16}) m with (10^{16}/(10^{16}+20)), rather than the old naive-assembly result of exactly 1 m. The free-DOF residual and strain-energy checks must remain below the existing (10^{-6}) solver tolerance. These extreme stiffnesses are numerical stress fixtures, not physical structural design examples. Node and Chromium regressions exercise the same case at 1280px and 390px.

## Compensated Truss preview aggregate totals

The JSON preview reports total member centreline length and total SI material volume using the existing Neumaier compensated summation helper. This preserves low-order contributions from small members when they are added to a much larger running total, while still returning ordinary binary64 values and rejecting genuinely overflowing totals. Individual member lengths and volumes remain the already-computed binary64 quantities; this does not increase their precision.

A numerical-boundary regression uses one 1e16 m member plus twenty 1 m members, and 1 mm² area for every member. The preview must return a total length of 10000000000000020 m and total volume of 10000000000.00002 m³. Naive sequential reductions lose or distort those small same-sign contributions. These are synthetic floating-point fixtures, not physical structural dimensions. Node and Chromium checks run the case at desktop and 390px mobile widths.

## Numeric string input contract

The FEM model parser and section-property helper accept primitive finite JavaScript numbers or trimmed decimal/scientific strings such as `-12`, `.5`, `1.` and `2.5e-3`. String inputs must use decimal syntax. JavaScript radix forms such as `0x10`, `0b10` and `0o10` are rejected instead of being silently reinterpreted by `Number()`. This keeps JSON/API inputs aligned with the application's decimal numeric fields while preserving ordinary decimal and scientific-notation compatibility. Whitespace around a valid decimal string is ignored. Raw strings longer than 256 UTF-16 code units are rejected before trimming, regular-expression matching or numeric conversion, so whitespace padding is included in the bound. Inputs within the limit are trimmed before decimal validation; a 256-code-unit value with 255 leading spaces and `1` remains valid, while the corresponding 257-code-unit value is rejected. This bounds imported/pasted input work without sacrificing binary64 precision. Blank strings, separators and non-finite values remain invalid.

## Hollow-rectangle small-cavity rounding

When the cavity/outer-area ratio is at most 0.5, net area uses the direct dimensionless difference rather than adding separately rounded complementary wall gaps. Ixx and Iyy use finite outer-minus-inner rectangle contributions through the shared section-property accumulator; if the solid-envelope moment overflows, the existing split-factor path remains available. For larger cavity ratios, the factored wall-gap expressions are retained to preserve thin-wall sections. Small-cavity radii use the stable identity
`(1 - cavity inertia ratio)/(1 - cavity area ratio) = 1 + cavity area ratio × (1 - inner-axis ratio²)/(1 - cavity area ratio)`
instead of dividing independently rounded factors.

The regression fixture B=H=1 mm, bi=1.2e-16 mm and hi=0.5 mm must return A=0.9999999999999999 mm², Ixx=Iyy=0.08333333333333333 mm⁴, centroid (0.5, 0.5) mm and rx=ry=0.28867513459481287 mm. A second fixture (bi=1.1e-16 mm, hi=0.51 mm) verifies the Iyy rounding boundary. A cavity below half an area ulp still rounds to the solid-envelope area. These are binary64 stress fixtures, not physical design dimensions. Node and registered Chromium tests also exercise the compatibility fallback with BigInt disabled at 1280px and 390px.

# 2D Truss Studio — canonical structural-truss-fem-2d

## Visible energy verification summary

After a successful solve, the results panel displays the signed global energy-balance residual in an always-visible `role="status"` summary, while the detailed force/energy verification remains in its collapsible disclosure. The summary exposes `data-analysis-state` (`pending` before the first successful solve, `valid` only after a successful solve, and `stale` whenever the model is invalidated or a solve fails) so integrations can distinguish current results from cleared or not-yet-computed results. It also exposes the shortest-round-trip binary64 values in `data-energy-residual-j` (joules) and `data-energy-error` (dimensionless); negative zero is preserved as `-0`. Both attributes are cleared to empty strings together with the visible summary whenever the model is edited or invalidated, and are repopulated only after a successful solve, so stale diagnostics cannot be mistaken for the current model. The registered Chromium regression compares both attributes against the solver's own binary64 reference, expands the detailed disclosure before inspecting its contents, and verifies edit/reset invalidation at desktop and 390px mobile widths.

## BigInt-free section-property summation fallback

The exact binary64 accumulator is used when the browser provides BigInt. When BigInt is unavailable, same-sign finite terms now use Neumaier compensation in their original units instead of normalizing by the largest term and multiplying back. This avoids an unnecessary second rounding during scale restoration and retains small same-sign contributions that can combine to change the rounded section property. Mixed-sign terms keep the existing exact-when-available and normalized compensated-residual fallback. The no-BigInt path is compensated, not exact; all returned values remain binary64, and genuinely non-finite final results are still rejected.

Direct Node and registered Chromium regressions temporarily disable BigInt and verify two L-angle area/centroid/inertia boundary cases, both channel and I-section sub-ulp flange-area totals, and channel/I-section centroid and inertia values. Chromium exercises the fallback at 1280px and 390px. The Truss solver remains an adjacent script, so the standalone root bundle is unchanged.

## Composite-section centroid and inertia summation

Channel and I-section calculations now sum their already-rounded finite binary64 rectangle contributions exactly when BigInt is available, rounding once after the complete sum. This applies to net area, both first moments, and each local-plus-parallel-axis inertia total. The existing scaled compensated sum remains the compatibility fallback when BigInt is unavailable. This avoids both lost sub-ulp contributions and order-dependent one-ulp overestimates; it does not make the underlying rectangle products arbitrary precision.

A synthetic boundary fixture uses B=2 mm, H=1 mm, tw=1 mm and tf=2e-17 mm. For the channel, naive first-moment reduction gives centroid x=0.5 mm instead of the correctly rounded 0.5000000000000001 mm; naive Ixx gives 0.08333333333333333 mm⁴ instead of 0.08333333333333334 mm⁴; naive Iyy gives 0.08333333333333336 mm⁴ instead of 0.08333333333333337 mm⁴. For the symmetric I-section, adding flange terms around the web can overestimate Ixx by one ulp (0.08333333333333336 instead of 0.08333333333333334 mm⁴). Direct Node and Chromium regressions compare against exact sums of the supplied binary64 terms at desktop and 390px viewports. These dimensions are numerical-boundary fixtures, not physical design examples.


## Composite-section area summation

Channel and I-section area totals use the shared scaled compensated accumulator instead of a left-to-right floating-point reduction. This matters when the web area is dominant and each flange area is individually smaller than half an ulp of that web area, but the two flange contributions together cross a rounding boundary. The regression uses a synthetic 1 mm² web and two approximately 6.66e-17 mm² flanges: ordinary sequential addition returns 1.0 mm², while the correctly rounded total is 1.0000000000000002 mm². The same behavior is checked for channels and symmetric I-sections. This is a binary64 summation-boundary test, not a physical design example.


**Section-helper behavior on dev:** The accessible section helper remains intentionally inside the initially collapsed “Member materials, section properties and Euler readiness” disclosure. The summary's `aria-controls="member-material-content"` references a wrapper containing both the member metrics table and section helper. Browser tests must verify the controlled region starts hidden, activate the summary, and verify the helper and target selector are visible before interaction; later scenarios must open the disclosure conditionally rather than blindly toggling a state left open by an earlier scenario. Applying properties requires one unambiguous member ID and preflights both destination fields before writing area and I. Unsupported axes, duplicate IDs, invalid/overflow geometry and missing fields reject without partial member mutation. The selected-member regression verifies a 40 × 60 mm rectangle gives A=2,400 mm² and Ixx=720,000 mm⁴ while preserving E, density, K and all other members. Any edit to section shape/dimensions, target member, selected axis, or a member's ID/area/I clears the previous application result; a stale “applied” message must never describe a different configuration. Loading a new model also clears the prior result.

**Import integrity on dev:** The browser snapshots immutable File.size before awaiting arrayBuffer(), validates the actual returned byteLength against the same 1 MiB budget, then strictly decodes UTF-8. A short read and a longer-than-declared read now have distinct diagnostics with exact expected/received counts. Both mismatches are rejected before JSON parsing, even when the differing bytes are only legal trailing whitespace; the active node/member inputs and prior solved results remain unchanged and aria-busy returns to false. Browser regressions cover both directions with actual File objects at 1280px and 390px, plus malformed UTF-8, actual BOM bytes and exact/over-limit boundaries.

**Verification baseline:** The immediately preceding dev head d1c25300184851af0c52c9619571c2878af5c458 passed exact-head Push Quality [#45202567594](https://github.com/saeedsai/ProMathStudio/actions/runs/45202567594) and PR Quality [#45202584053](https://github.com/saeedsai/ProMathStudio/actions/runs/45202584053), each with 218/218 steps successful and zero failures/skips. This new read-direction candidate requires fresh exact-head CI; it is not released.


## Material schedule CSV numeric round-trip

Finite numeric cells in the material schedule use JavaScript's shortest round-trippable decimal representation. Before quoting, the exporter reparses each numeric cell and verifies `Object.is(Number(text), value)`; it refuses non-finite numeric cells rather than emitting `Infinity` or `NaN`. This avoids fixed-significant-digit truncation: density `0.10000000000000002` and its derived mass `0.00020000000000000004` survive export and numeric re-import unchanged. For the 2 m, 0.001 m² bar at 7850 kg/m³, the UI intentionally displays mass rounded to `15.7` kg while the CSV preserves the computed binary64 value `15.700000000000001`. Euler critical load is converted from N to kN before serialization; a positive load that underflows to zero during this unit conversion is rejected rather than exported as a misleading zero. For the standard 2 m bar with I=1e6 mm⁴ and K=1, the kN cell is `493.48022005446785`, the shortest decimal that round-trips to the computed binary64 value. Negative zero is emitted explicitly as `-0`. This guarantees serialization fidelity, not additional physical accuracy beyond the stored inputs.

## Hollow-rectangle inertia range safety

Hollow-rectangle centroidal inertias use the existing dimensionless wall-gap factors without first constructing the outer and inner solid-rectangle fourth-power moments. For the Ixx path, the dimensionless factor is split evenly across the two depth factors:

\[
I_{xx}=A_o\left(\frac{h\sqrt{f_x}}{12}\right)(h\sqrt{f_x}),
\qquad A_o=bh
\]

Iyy uses the corresponding width factor. This is algebraically equivalent to the factored outer-minus-inner expression, but it avoids overflowing the full solid-envelope inertia before a very small wall factor is applied. Composite-section and L-angle rectangle pieces continue to use the same helper with factor 1.

A synthetic exact-binary64 boundary regression uses B=1e-10 mm, H=1e110 mm, bi=9.999999999999998e-11 mm and hi=9.999999999999999e109 mm. Both the old outer and inner Ixx fourth-power intermediates overflow, while area, Ixx/Iyy, section moduli and radii of gyration remain finite and match 100-digit Decimal references. These dimensions are a floating-point range test only, not a physically meaningful design example.

## Composite-section inertia range safety

The local centroidal moments of each non-overlapping rectangle are evaluated in an overflow-aware order:

- Ixx = (b*h)*(h/12)*h
- Iyy = (b*h)*(b/12)*b

These are algebraically identical to b*h^3/12 and h*b^3/12, but divide by 12 before the final multiplication. This prevents an intermediate b*h^3 or h*b^3 overflow when the final local moment is still representable. The same helper is used for the L-angle and channel/I-section rectangle decompositions; the parallel-axis terms, centroid calculation, validation and ordinary-size results are unchanged.

A synthetic floating-range regression uses 120-digit Decimal references for channel, I-section and L-angle properties. Its dimensions are intentionally far outside physical design practice and are solely a binary64 numerical-boundary test, not an engineering sizing example.

## Solid-circle inertia range safety

For a solid circle, the centroidal inertia is evaluated as `(π/64)·Do²·Do²`, applying the coefficient before the final multiplication. This avoids requiring the unscaled fourth-power intermediate `Do⁴` to be representable when the physical inertia is still finite. The final inertia still passes the existing finite-value guard; genuinely overflowing moments and underflowing small sections remain rejected.

A synthetic exact-binary64 regression uses `Do=2.45e77 mm`. The old `Do²·Do²` intermediate overflows, while area, Ixx/Iyy, section moduli and radii of gyration remain finite and match 120-digit Decimal references. A 40 mm reference remains unchanged, and the existing tiny-diameter underflow case remains rejected. These extreme dimensions are floating-point boundary tests only, not physically meaningful design examples.

## Rectangular radius-of-gyration precision

Solid and concentric hollow rectangles now calculate their radii directly from the section geometry instead of taking the square root of a rounded binary64 inertia/area quotient:

\[
r_x=h\sqrt{\frac{f_x}{12f_A}},\qquad
r_y=b\sqrt{\frac{f_y}{12f_A}}
\]

For a solid rectangle, all three factors are 1. For a hollow rectangle, with \(r_b=b_i/b\), \(r_h=h_i/h\), \(g_b=(b-b_i)/b\), and \(g_h=(h-h_i)/h\):

\[
f_A=g_b+r_b g_h,\quad
f_x=g_b+r_b g_h(1+r_h+r_h^2),\quad
f_y=g_h+r_h g_b(1+r_b+r_b^2)
\]

This avoids propagating severe relative error from a subnormal inertia. A synthetic binary64 case with \(b=10^{-6}\) mm and \(h=3.5\times10^{-106}\) mm produces a representable \(I_{xx}=5\times10^{-324}\) mm⁴, but the rounded \(\sqrt{I_{xx}/A}\) is about 17.6% above the geometric radius. The hollow-rectangle counterpart has the same issue. The direct geometric radii retain the analytical reference while the reported inertia remains the correctly rounded binary64 value. These dimensions are floating-point stress tests only, not physical design examples.

## Rectangular section-modulus precision

Solid and concentric hollow rectangles evaluate elastic section moduli directly from their dimensionless geometry factors when the corresponding dimensional inertia is subnormal:

\[
S_x=\frac{b h^2 f_x}{6},\qquad S_y=\frac{h b^2 f_y}{6}.
\]

This avoids dividing a coarsely quantized binary64 inertia by an extreme-fibre distance when the resulting section modulus is still normally representable. The reported Ixx/Iyy remain the correctly rounded binary64 values; Sx/Sy retain the precision of the original rectangle geometry. Ordinary, normal-inertia sections keep the existing I/c path. A synthetic exact-binary64 case with B=4.5e-81 mm and H=6e-81 mm, plus its concentric half-width/half-height hollow counterpart, previously produced 2–4% section-modulus errors from I/c. The direct formulas agree with 120-digit Decimal references within 5e-13 relative error. These dimensions are floating-point stress tests only, not physical design examples.

## Circular radius-of-gyration precision

For a solid circle, both centroidal radii are analytically (r_x=r_y=D_o/4). For a concentric hollow circle, with (q=D_i/D_o), cancellation of the common annulus factor gives

\[
r_x=r_y=\frac{D_o}{4}\sqrt{1+q^2}.
\]

The helper evaluates these equivalent geometric formulas directly instead of deriving the radius from a rounded binary64 (I/A) quotient. This matters when the reported inertia is a nonzero subnormal: its relative quantization can be large even while the area and exact radius remain representable.

A synthetic solid-circle boundary uses (D_o=3\times10^{-81}) mm. Its area is approximately (7.06858\times10^{-162}) mm² and its reported inertia rounds to the smallest positive binary64 value, but (sqrt{I/A}) overstates the geometric radius (7.5\times10^{-82}) mm by about 11.5%. The hollow counterpart with (D_i=1.5\times10^{-81}) mm has the same subnormal inertia and about 15.1% quotient error; the direct formula gives approximately (8.38525\times10^{-82}) mm. These dimensions are numerical representation tests only, not physical design examples.

## Small-cavity hollow-circle rounding

For a concentric hollow circle, let \(q=D_i/D_o\). When \(q\leq0.5\), the area and inertia factors are evaluated directly as \(1-q^2\) and \(1-q^4\). These factors remain at least 0.75 and 0.9375 respectively, so direct subtraction is well-conditioned. For \(q>0.5\), the helper retains the factored radial-gap expressions; this is the thin-wall regime where subtracting nearly equal squares would lose precision.

This split avoids multiplying separately rounded complementary factors for a very small cavity. If the cavity contribution is below half an ulp of the outer-envelope property, the correctly rounded binary64 result is the corresponding solid-circle value.

The regression uses the exact binary64 inputs \(D_o=1\) mm and \(D_i=9.313225746154786\times10^{-14}\) mm. The previous factored area and inertia factors both rounded to \(0.9999999999999999\), lowering area from \(0.7853981633974483\) to \(0.7853981633974482\) mm² and inertia from \(0.04908738521234052\) to \(0.04908738521234051\) mm⁴. The corrected factors round to 1, matching the solid-circle results. Existing thin-wall and extreme-scale annulus regressions remain in place. These are binary64 stress fixtures, not physical design dimensions.

## L-angle mixed-axis subnormal precision

A high-aspect-ratio L-angle can have one normal centroidal inertia and one subnormal inertia. A single maximum-dimension normalization may preserve the major axis but underflow the independently scaled minor axis. For a subnormal axis, the helper now normalizes width and depth separately and evaluates that axis's section modulus and radius directly from the two-rectangle geometry. The reported dimensional inertia and principal moments retain their binary64 values; only the affected `S` and `r` outputs use the higher-precision normalized geometry.

A synthetic exact-binary64 fixture (`B=1e-60 mm`, `H=1e60 mm`, `t=1e-140 mm`) has normal `Ixx` and subnormal `Iyy` (about `3.335e-321 mm⁴`). Its geometric `Sy` is about `3.333333333333333e-261 mm³` and `ry` about `5.773502691896258e-121 mm`; deriving them from the quantized `Iyy` produces relative errors above `1e-4`. Node and Chromium regressions use 160-digit Decimal references and run at desktop and 390px. These dimensions are floating-point stress fixtures only, not engineering design dimensions.

### Negligible underflowed channel web

A channel web is off the section's vertical centroidal axis, so its area cannot be discarded merely because tw times H rounds to zero: its first moments and parallel-axis terms may still be representable. The helper now accepts an underflowed channel web only when exponent-scaled upper bounds show that its area, both first moments, local and offset Ixx/Iyy, and Ixy all round below binary64 significance. Its area must also vanish in both the common-length and axis-separated normalized geometry paths. The flange-only aggregate area, first moments and both centroidal inertias must remain in the normal binary64 range; otherwise the section is still rejected. The existing centered I-section-web exception remains separate.

A synthetic exact-binary64 fixture (B=1e40 mm, H=1e-100 mm, tw=Number.MIN_VALUE, tf=2e-101 mm) has a positive web area that rounds to zero, while the complete section properties remain representable: A=4e-61 mm², Ixx=6.533333333333334e-262 mm⁴, Iyy approximately 3.333333333333334e18 mm⁴, Sx approximately 1.306666666666667e-161 mm³, Sy approximately 6.666666666666666e-22 mm³, rx approximately 4.041451884327381e-101 mm and ry approximately 2.8867513459481285e39 mm. A second off-axis-web fixture retains a representable first moment and is still rejected. Node and Chromium regressions use 200-digit Decimal references at 1280px and 390px. These dimensions are floating-point stress tests only, not engineering design dimensions.

## How to use

Open `tools/truss-studio.html` in a browser (requires its adjacent `truss-fem.js` and `truss-fem-ui.js`). Select a reference model or edit **Joints**: unique ID, X/Y in metres, Fix X/ Fix Y, forces Fx/Fy in kN (positive right/up). In **Members**, enter start/end IDs, E in GPa, area in mm² and optional density in kg/m³. The **Section property helper** in the material breakdown calculates area, centroidal Ixx/Iyy, elastic section moduli Sx/Sy, extreme-fibre distances cX/cY and radii of gyration rx/ry for solid/hollow rectangles and circles, plus open channels, I-sections and L-angles. L-angles also report Ixy, principal I1/I2 and the major-principal-axis angle; the selected centroidal/principal moment is applied to one member. Sx = Ixx/cX and Sy = Iyy/cY; rx and ry are the geometric equivalents of sqrt(Ixx/A) and sqrt(Iyy/A), evaluated from shape-specific formulas where a rounded subnormal quotient would lose precision. Rectangle Ixx is about the horizontal centroidal axis parallel to width; circle I is about any centroidal diameter. These are geometric properties, not design resistances. Optional Euler estimate inputs are I (second moment of area, mm⁴) and K (dimensionless effective-length factor); provide both to calculate Pcr. Either property may be stored alone without producing an Euler estimate; the geometry/member preview remains available and the status explains when the pair is incomplete. Click Analyze truss. Results show member tension/compression force (kN), stress (MPa), joint displacements (mm), support reactions (kN), residual/energy verification and, when I/K are supplied, a compression-only ideal Euler comparison. Gray dotted members represent the original truss; colored amplified lines represent deformed geometry (green tension, orange compression). Change scale or label visibility, export the model as JSON, results as CSV, diagram as SVG; imported legacy SI JSON is converted explicitly. The import status identifies the file's units for optional density (kg/m³), second moment I (m⁴ in legacy SI or mm⁴ in Studio) and effective-length factor K (dimensionless), in addition to the core force, modulus and area units.


## Preview metadata contract

Every valid section preview exposes one outer outline with the same canonical millimetre metadata:

- `data-section-width-mm` and `data-section-height-mm` describe the section bounding dimensions (for circles, both equal the outer diameter).
- `data-section-area-mm2`, `data-section-centroid-x-mm` and `data-section-centroid-y-mm` come directly from the canonical `sectionProperties` result.
- The centroid marker exposes `data-centroid-x-mm` and `data-centroid-y-mm`; each centroidal axis (or each L-angle principal axis) exposes the same coordinates.
- Circular outlines additionally expose `data-section-diameter-mm` and, for a hollow circle, `data-section-inner-diameter-mm`. Hollow rectangles expose inner width/height on the outer and inner outlines. Channels and I-sections retain web/flange thickness metadata; L-angles retain leg thickness.
- Every dimension annotation (B, H, D/Do/Di, bi/hi, tw/tf and L-angle t) has a stable `data-dimension-label`, SVG text role and an accessible name that includes its formatted millimetre value. The browser regression checks the complete expected dimension-label set and exact visible/accessibility value parity for all seven shapes.
- Horizontal/vertical `Ixx`/`Iyy` labels have explicit accessible names and text roles. The SVG title, description and visible caption remain synchronized through the root `aria-label`.
- When any required dimension is invalid or a computed property overflows/underflows, the preview removes all stale outlines, centroid/axis markers and dimension metadata. Because `aria-labelledby` references the SVG title and description, the `<desc>` is updated to the same unavailable message as the live caption and root `aria-label`; correcting the input restores the shape-specific description and canonical geometry. The browser regression exercises zero, negative, NaN/empty-number and arithmetic-overflow states plus recovery for all seven shapes.

This is presentation metadata, not a second calculation API. The FEM helper remains the sole source of area and centroid values. The Chromium regression checks all seven shapes at a 390px viewport against independent reference values and verifies the outline, centroid marker, axis metadata, title/description/caption and accessible axis labels.

## Exported deformation SVG geometry metadata

The solved SVG export preserves semantic attributes on every geometry line so downstream viewers and tooling do not need to infer meaning from color or coordinates:

- `data-geometry-role="original-member"` identifies the dotted undeformed member and includes its `data-member-id`.
- `data-geometry-role="deformed-member"` identifies the solved member and includes its member ID, `data-force-state` (`tension`, `compression` or `neutral`) and axial force in newtons.
- `data-geometry-role="applied-load"` identifies the load-vector shaft and includes the node ID and applied Fx/Fy in kN.
- `data-geometry-role="load-arrowhead"` identifies each arrowhead segment and includes its node ID and stable segment index.

The browser regression parses the actual exported SVG after importing a one-member AB bar with a load at B. It requires exactly one original member, one deformed member, one load shaft, two arrowhead segments and no unclassified line elements, while retaining the existing XML, MIME, viewBox, aspect-ratio, title, description, ARIA and background checks. These attributes are descriptive metadata only; they do not change FEM calculations or visual geometry.

## Numerical contract

The FEM solver models 2D pin-connected, axial-only, linear-elastic, small-displacement trusses with static loads. Each bar stiffness is `EA/L * [-c,-s,c,s]^T [-c,-s,c,s]`; global K is assembled, fixed zero-displacement DOFs eliminated, free system diagonal-scaled and solved with pivoting. Member axial extension is projected relative endpoint displacement; positive axial stress is tension. Reactions are `K*u-F`. Force balance, free-DOF residual, and twice strain energy = external work are checked. The solver itself does not model geometric buckling, post-buckling, yielding, thermal loads or connection behavior.

## Section-property helper

The standalone helper uses dimensions in mm and returns area in mm², centroidal second moments in mm⁴, elastic section moduli in mm³, extreme-fibre distances in mm and radii of gyration in mm:
- Solid rectangle: A = b·h, Ixx = b·h³/12, Iyy = h·b³/12.
- Concentric hollow rectangle: subtract the centered inner rectangle from the outer rectangle for A, Ixx and Iyy.
- Solid circle: A = π·d²/4, Ixx = Iyy = π·d⁴/64.
- Concentric hollow circle: with r = Di/Do and g = (Do−Di)/Do, compute A = (πDo²/4)·g·(1+r) and Ixx = Iyy = (πDo⁴/64)·g·(1+r)·(1+r²). The factored annulus expressions avoid subtracting nearly equal squared/fourth-power diameters for thin walls.
- Open channel: the web is on the left and both flanges extend right. It is assembled from a full-height web and two non-overlapping flange rectangles.
- I-section: two full-width flanges and a centered non-overlapping web rectangle.
- L-angle: one full-height left leg and one bottom leg extending right, decomposed into two non-overlapping rectangles so the shared corner is counted once.
The L-angle SVG outline publishes canonical `data-section-width-mm`, `data-section-height-mm`, `data-section-thickness-mm`, `data-section-area-mm2` and centroid coordinates in millimetres. Its two principal-axis lines and labels publish their angles; both axes must remain perpendicular and intersect at the same centroid. Browser coverage includes an asymmetric 120 × 70 × 12 mm reference and a near-limit valid 120 × 70 × 69.9 mm leg, with the exact 70 mm boundary rejected.

For channel and I-section, the helper computes the composite area centroid and both centroidal moments with the parallel-axis theorem. Both idealized open profiles are symmetric about the horizontal centroidal axis, so the horizontal/vertical centroidal axes are principal for these geometries. The channel centroid is reported from the outside web face and bottom edge; the I-section centroid is centered for symmetric inputs. Select Ixx (horizontal centroidal axis) or Iyy (vertical centroidal axis) before applying the selected value to the member. For bending about X, cX is the larger distance from the centroid to the top/bottom extreme fibres; for bending about Y, cY is the larger distance to the left/right extreme fibres. The channel's offset centroid therefore uses the farther outside edge when calculating cY.

For the L-angle, Ixy is the centroidal product of inertia Σ[Aᵢ(xᵢ−x̄)(yᵢ−ȳ)] because each aligned rectangle has zero local product of inertia. The principal moments are I1/I2 = (Ixx+Iyy)/2 ± sqrt(((Ixx−Iyy)/2)² + Ixy²); the I1-axis angle is 0.5·atan2(−2Ixy, Ixx−Iyy), counter-clockwise from +x; the perpendicular I2 minor-principal axis is at the I1 angle +90°. The reported angle uses Ixy = ∫(x−x̄)(y−ȳ)dA and the I1 major-moment convention. When an open channel is selected, the helper renders a live, accessible web-left/flanges-right SVG with B/H/tw/tf dimensions, the offset canonical centroid and horizontal Ixx/vertical Iyy axes. When an I-section is selected, it renders a live, accessible symmetric I-shaped SVG with a centered web, equal full-width flanges, B/H/tw/tf dimensions, the canonical centroid and horizontal Ixx/vertical Iyy axes. When a solid or concentric hollow rectangle, solid or concentric hollow circle is selected, the helper renders a live, accessible SVG with its outer dimensions, centroid and centroidal axes. The hollow-rectangle sketch shows the visibly cut-out centered void, B/H/bi/hi dimensions and inner dimension guide lines; the solid-circle sketch shows D; the hollow-circle sketch shows concentric outer/inner outlines with Do/Di dimensions and two perpendicular diameter axes. When an I-section is selected, it renders the centered-web/equal-flange outline with live tw/tf dimensions and invalid-thickness recovery. When an L-angle is selected, it renders B/H/t dimensions, centroid and both perpendicular major (I1) and minor (I2) principal axes. The visible caption reports both principal-axis angles to a consistent 0.001° precision. Each principal-axis SVG line exposes the canonical centroid coordinates in millimetres through data-centroid-x-mm and data-centroid-y-mm; its matching text label exposes the same angle in degrees through data-axis-angle-deg, keeping the visible labels and machine-readable geometry aligned with the FEM helper. These previews update as dimensions are edited, clear stale outlines when dimensions are invalid, and keep the SVG accessible name synchronized with the visible caption. These are geometry previews, not stress contours or FEM results.

The section-property helper returns an immutable centroid for solid and concentric hollow rectangles, solid and concentric hollow circles, and the open channel, I-section and L-angle. Rectangle centroid coordinates are measured from the lower-left outer corner; for a concentric void they remain at (B/2,H/2). Circular centroid coordinates are measured from the lower-left outer corner of the diameter-sized bounding square and remain at (D/2,D/2) for a concentric void. The live solid/hollow rectangle, solid/hollow circle and open-channel sketches consume this canonical result rather than recomputing the centroid in the UI. The helper also reports Sx = Ixx/cX and Sy = Iyy/cY, plus rx = sqrt(Ixx/A) and ry = sqrt(Iyy/A). These are elastic geometric section properties about the stated centroidal axes; they are not code resistance, allowable stress or a substitute for a complete member stability/design check. The section moduli and radii are displayed for reference and are not used by the axial-only FEM or the optional Euler estimate.

The open-section geometry assumes sharp corners, uniform web/flange thickness, no lips, no fillets and no eccentricity. The L-angle assumes two equal leg thicknesses meeting at a sharp right angle, with no fillet or toe radius. It does not calculate torsional constant, shear centre, shear area, warping, connection effects or code resistance. The formulas describe ideal prismatic cross-sections only.

All dimensions must be finite and strictly positive, with web thickness smaller than B and two flange thicknesses smaller than H. Area, moments, section moduli and radii that underflow or overflow are rejected before any member is changed. Applying a valid result updates only the selected member's area and I; E, density, K and other members are preserved. The browser preflights both destination fields before writing either, so a missing field or invalid/overflowing geometry cannot leave a partial section update.

## Optional ideal Euler member estimate

The non-solving material preview can report the ideal elastic critical load `Pcr = π² E I / (K L)²` when both second moment of area `I` and effective-length factor `K` are supplied. The numerical evaluation preserves the established direct operation order for ordinary inputs, then uses a binary mantissa/exponent product-quotient fallback if the numerator, `K·L`, or its square overflows or underflows; only a genuinely non-finite or zero final `Pcr` is rejected. Current Studio JSON/UI uses `I` in mm⁴; legacy SI JSON uses `I` in m⁴ and converts it on import. `K` is dimensionless. The reported `Pcr` is in kN. Missing I/K leaves the estimate blank; supplying only one, non-positive/non-finite values, or an unrepresentable final result is rejected. After solving, only compressive axial force is compared with `Pcr`; the result reports utilization `Pcomp/Pcr` and load ratio `Pcr/Pcomp`. Tension is not applicable and zero force is reported as no compression demand without division. This remains an ideal elastic screen, not a geometric buckling solver or code-compliant resistance check; it does not include imperfections, residual stress, local/flexural-torsional modes, inelasticity, code resistance factors or post-buckling. It is an educational idealization, not a certified design check; consult a qualified structural engineer.

## Compatibility

Previous TrussStudio API still exposes `TrussStudio.solve(model)` and `TrussStudio.example` with SI N/Pa/m² units and legacy output shape. The UI now accepts kN/GPa/mm². JSON import recognizes legacy member field `A` (m²) and converts load forces in N, E in Pa, and A in m² to the new form; exported JSON uses explicit new-form keys and units. The browser rejects invalid/non-safe or over-limit `File.size` values before reading, then rechecks the actual `ArrayBuffer.byteLength` against the same 1 MiB budget and requires exact equality with the immutable `File.size` before decoding. A mismatch reports the expected and received byte counts. A leading UTF-8 BOM is accepted only when it is part of the actual file bytes (and therefore contributes to `File.size`), then stripped by the canonical importer; malformed UTF-8 is rejected before any model controls are replaced. These checks prevent inconsistent file-size metadata and truncated/expanded reads from bypassing import integrity. Existing `index.html` distribution and source/bundle hashes are unchanged, but the companion page requires its relative JS assets, including for offline use.


### Pending JSON import cancellation on model edits

A file read is asynchronous, so a user may edit the active model before the selected file's bytes finish arriving. Bubbling `input` events are the authoritative edit signal for the node/member text, numeric and checkbox controls; the editor cancels a pending import when an actual input event invalidates the active model (and when the user explicitly analyzes it). Blur-only `change` events are not independently treated as edits: a delayed change notification from a field already edited before file selection can otherwise arrive after the newer import starts and incorrectly cancel that request. Member-ID edits synchronize the section-member selector on `input`. The late file result after a genuine edit is ignored, the edit remains in the editor, and the status reports cancellation. A newer file selection still supersedes an older read. The Chromium regression holds a legacy SI file read open, dispatches a blur-style change event after selection and verifies that the import remains pending and succeeds; it separately edits density through a real input event during another held read, verifies cancellation, releases the late bytes and confirms the edited value remains.

### Standalone SVG export sizing

The exported 1240×760 SVG explicitly sets `preserveAspectRatio="xMidYMid meet"` with the existing `viewBox="0 0 620 380"`. SVG viewers therefore fit the diagram proportionally inside the output viewport rather than stretching its geometry. The Chromium regression checks the serialized SVG root attribute together with its MIME type, namespace, title/description, accessible-name references, background and solved lines.

### Standalone SVG export accessibility

The solved deformation export preserves the plot's `viewBox` and SVG namespace, adds explicit 1240×760 output dimensions, and includes direct-child `<title>` and `<desc>` elements. The root uses `role="img"` and `aria-labelledby` references to both IDs; the description explains the dotted original members and tension/compression deformation coloring. The exported Blob is parsed as XML in Chromium regression tests, which verify the namespace, dimensions, viewBox, accessible-name references, title/description order, background and solved geometry.

### CSV download encoding and units

Both results and material-schedule downloads are UTF-8 CSV with exactly one leading UTF-8 BOM so spreadsheet applications such as Excel can identify Unicode unit symbols reliably. The shared download serializer removes any pre-existing leading BOM and canonicalizes CRLF, lone CR and lone LF record separators to CRLF before adding the single BOM. It appends one CRLF when non-empty normalized content lacks a terminal record separator; empty content remains BOM-only. Every field is quoted with embedded quotes doubled, and the final record also ends in CRLF. The results export labels force/stress/displacement/reaction units in kN, MPa and mm; the material schedule reports SI geometry/material quantities with explicit units (m, m², m³, GPa, kN/mm, kg/m³, mm⁴ and kN). The Chromium regression counts BOM sequences in the raw downloaded Blob bytes, checks CRLF-only records, parses the CSV columns and verifies that exports reflect the currently imported model.

## References and tests

- Single 2 m bar: E=200 GPa, area=1000 mm², +1 kN, displacement 0.01 mm, axial stress 1 MPa, reaction -1 kN. With I=1,000,000 mm⁴ and K=1, the ideal Euler Pcr reference is approximately 493.480220 kN.
- Three-bar triangle: legacy 10 kN load, member forces +5 kN in bottom chord and -7.0710678 kN on each diagonal, support reactions +5 kN each; +20 kN form example with 4 m span has +10 kN reactions each.
- Node bounds 2–80, members 1–240, maximum 150 free DOFs. Reject missing/free restraints, invalid IDs/endpoints, zero lengths, nonfinite input and zero/negative E/A.
- node --test tests/test_truss_fem.js: analytical references, stiffness/load scaling, equilibrium, invalid geometry and mechanisms; solid/hollow rectangle/circle and channel/I-section area, centroid, Ixx/Iyy, Sx/Sy, cX/cY, rx/ry and underflow/overflow references.
- `python tests/smoke_truss_fem.py`: reference solver, browser editing/recovery, SVG, generated export content, desktop/mobile layout and console errors.
- `python tests/smoke_truss_studio.py`: original 10 kN SI reference and legacy JSON import, old API compatibility, section-property display for all seven shapes, solid/hollow rectangle and solid/hollow circle dimensioned SVG/centroid/axis previews, L-angle principal-axis preview, hollow-wall invalid clearing/recovery, exports and 390px responsive recovery. Browser CI tests inline the same JS files because sandboxed Chromium blocks `file://`; hosted deployment must separately confirm relative asset loading and actual downloads.

### Import unit provenance feedback

After a valid JSON import, the status message identifies whether the file used legacy SI units (N, Pa, m² and m⁴) that were converted to the Studio editor units (kN, GPa, mm² and mm⁴), or whether Studio units were retained. This message is appended only after a successful solve; a structurally unstable model or rejected import keeps its error visible. The Chromium regression uses the actual file input to import a legacy bar with density, I and K, verifies the converted editor values and 0.01 mm reference displacement, exports the edited model as current Studio JSON, reimports it, and verifies the optional properties survive. A mixed-unit file must be rejected without changing the previously loaded model or solved result.

The optional import notice is a string-only argument to the analysis helper. The Analyze button's DOM event object is never treated as notice text; the browser regression asserts that ordinary manual analysis does not display an event-object string.


## Browser file-import byte integrity

The shared `ProMathTrussFEM.validateImportByteLength(declaredSize, actualByteLength?)` validator owns the 1 MiB file-import boundary. The UI calls it before the read with the immutable declared `File.size`, then after the read with `ArrayBuffer.byteLength`. Negative, fractional, non-finite and unsafe declared or actual lengths are rejected as invalid metadata; a safe declared or actual length above 1 MiB is reported as oversized. A safe but unequal read reports whether fewer or more bytes than declared were returned, with exact expected and received counts. All checks happen before UTF-8 decoding or JSON parsing. The Chromium regression creates a real File containing valid JSON, overrides only the File prototype read for that named file to return one byte fewer, and verifies the direction-specific diagnostic plus unchanged active model and solved results. The direct Node regression covers invalid declared/actual metadata, exact and over-limit sizes, and shorter/equal/longer counts. The import must fail without replacing the active model or its last solved result. The per-instance override avoids shared `File.prototype` state across the preceding delayed-import race test. The separate BOM regression places EF BB BF in the actual uploaded File buffer, so the browser's `File.size` includes those three bytes and the canonical importer can strip the decoded BOM without violating byte-count integrity.


## Latest-request-wins asynchronous JSON imports

Each selected file receives a monotonically increasing import request token. A request may continue after an asynchronous byte read or report an error only while its token is still the latest and its pending state has not been settled. Only that current request may clear the busy state or replace the active model/status. Selecting another file supersedes the previous request; editing the active model cancels the pending request. A stale earlier read that later succeeds or rejects is ignored and cannot replace the newer imported model, clear its pending indicator, or overwrite its success/error status. Clicking Analyze also cancels a pending import and solves only the currently displayed model; the resulting status explicitly reports that the pending import was cancelled.

The Chromium regression delays real File reads and covers: an older success after a newer successful import; an older rejection after a newer successful import; an older success after a newer selected file is rejected; and both late success and late rejection after Analyze cancels the pending import. The newest/current joint/member inputs, solved outputs, status and `aria-busy=false` remain unchanged after every stale completion. Analyze's cancellation notice remains visible alongside its successful analysis result. These are concurrency/rollback guarantees; they do not change FEM equations, import units or JSON schema.


## Legacy example copy semantics

The compatibility property `TrussStudio.example` retains the original SI-unit model shape (forces in N, modulus in Pa and member area in m²), but each property read returns a new editable deep copy. Mutating one retrieved model therefore cannot contaminate a later caller's reference example. Existing code that stores the property once and passes that object to `TrussStudio.solve(model)` remains supported. The Node regression checks independent object/array identity, editability, canonical SI values and successful solving of a fresh copy.


## Legacy SI compatibility reference and optional-property regression

The private canonical `TrussStudio.example` reference is recursively immutable. Each public getter read remains a fresh editable copy, preserving the legacy SI JSON contract (N, Pa, m² and m⁴). Legacy imports with optional density, second moment I and effective-length factor K must preserve physical equivalence after conversion to Studio units. The reference case uses density 7850 kg/m³, I=1e-6 m⁴ and K=1: the 2 m AB member mass is 15.7 kg and its Euler critical load is 493480.22005446785 N. Direct Node and Chromium regressions cover conversion and analysis; the browser fixture must restore native File prototype behavior after byte-boundary monkeypatches.


## Legacy optional-property normalization

When legacy SI JSON is converted by §fromLegacy§, optional member properties density, second moment §I§ and effective-length factor §K§ use one presence rule: §undefined§, §null§ and whitespace-only strings mean “not supplied” and are omitted from the normalized Studio member. Numeric zero remains present: density zero is valid and produces zero mass, while zero §I§ or §K§ remains invalid because each supplied buckling property must be strictly positive. §I§ and §K§ are independent; either may be retained alone, but the ideal Euler estimate is available only when both are supplied. The direct Node regression covers null/empty/whitespace values, zero density, legacy I-only and K-only conversions, and the absence of a false Euler estimate.


## Section-helper target identity and disclosure

The section-property helper is inside the native `<details id="member-material-details">` disclosure. It is intentionally collapsed on initial load; a user opens “Member materials, section properties and Euler readiness” to access the material schedule and helper. The summary contains a polite live `#member-material-count` label derived from the validated member snapshot: it displays the correct singular/plural count after model changes and `Unavailable` when preview validation fails. Browser regressions must verify the initial collapsed state, activate the summary once, and assert `#section-helper` is visible before interacting with its controls; later scenarios must reopen it conditionally rather than assuming it has re-collapsed.

Applying section properties requires the selected member ID to match exactly one current member row. No match reports that an existing member must be chosen; duplicate matches report an ambiguous ID and leave all member fields untouched. This prevents a pre-analysis edit that introduces duplicate IDs from silently applying section properties to whichever duplicate happens to appear first. The Chromium regression creates a duplicate ID, checks the exact diagnostic and full model snapshot, restores the unique ID, then verifies normal selected-member application and rollback cases.


## Section-axis selection validation

The section helper applies a centroidal or principal second moment only when the selected axis is valid for the current shape. Solid/hollow rectangles, channels and I-sections accept the width-parallel Ixx or depth-parallel Iyy axis. L-angles accept those two centroidal axes plus the major I1 and minor I2 principal axes. Circular sections do not use the axis selector. An invalid or stale selector value is rejected before either the selected member's area or I field is written; the browser regression injects an unsupported value and verifies the full member snapshot is unchanged before restoring Ixx and continuing the normal application test.


## Strict UTF-8 decoding of uploaded model bytes

The FEM kernel owns uploaded-byte decoding through `decodeImportBytes(bytes)`. It accepts an `ArrayBuffer` or typed-array view, enforces the shared 1 MiB byte budget, and uses a fatal UTF-8 decoder. Malformed, truncated or overlong byte sequences are rejected with the explicit `Model JSON must be valid UTF-8.` diagnostic rather than being replaced by U+FFFD and silently changing identifiers or numeric text. The decoder preserves a leading U+FEFF in its returned string so `importJSON` can strip the BOM only after the original bytes have already been counted by the File-size validator. The UI calls this canonical kernel helper only after the immutable declared File size and actual ArrayBuffer length have matched.

Node coverage exercises valid ArrayBuffer and typed-array input, actual UTF-8 BOM bytes, malformed two-, three- and four-byte sequences, invalid input types and the byte limit. The Chromium File-input regression uploads a real invalid byte sequence, verifies the exact error and `aria-busy=false`, and compares every node/member input plus the last solved displacement/stress/residual/verification text before and after rejection. It then imports a valid model and verifies analysis recovery. The browser scenario runs at the existing desktop and 390px viewports.


## Actual BOM and 1 MiB browser-file boundary

The UTF-8 BOM is part of the uploaded file's byte count: EF BB BF contributes three bytes to immutable File.size and the returned ArrayBuffer.byteLength. A real browser regression imports a BOM-prefixed Studio JSON document padded with legal trailing JSON whitespace to exactly 1 MiB, captures both lengths and the first three bytes, and verifies the same model and solved displacement are retained. A second real File one byte over the limit must be rejected from the declared size before arrayBuffer() is called, with the active model and prior solved results unchanged.

validateImportByteLength(declaredSize, actualByteLength) distinguishes invalid read metadata (undefined, null, negative, fractional, non-finite or unsafe actual length) with Model JSON read returned an invalid byte length. from a safe actual payload above 1 MiB (Model JSON exceeds 1 MiB.). Short/long but otherwise valid lengths retain the explicit expected/received mismatch diagnostic. Node tests cover each classification; Chromium verifies the invalid-metadata rollback, exact-limit BOM success and over-limit pre-read rejection at desktop and 390px.


## L-angle principal-moment numerical stability

The L-angle inertia tensor is diagonalized after scaling Ixx, Iyy and Ixy by their largest magnitude. The major principal moment is calculated from the normalized mean and radius; the minor moment is calculated as det(I)/I1 rather than subtracting two nearly equal large values. This preserves a representable minor moment for slender but valid sections and avoids avoidable overflow in the unscaled mean, radius and doubled product of inertia. A non-positive normalized determinant or an unrepresentable final moment is still rejected; the implementation does not clamp a negative or zero result into a plausible value.

The direct Node regression includes B=1,000,000 mm, H=1 mm and t=0.001 mm. Its minor principal moment is approximately 4.161659185863228e-4 mm⁴ (independent high-precision composite-rectangle reference); the former mean-minus-radius calculation rounded this positive value to zero and rejected the section.

## Thin-walled hollow-rectangle numerical stability

For outer width/depth \(b,h\) and centered inner width/depth \(b_i,h_i\), compute the hollow section by factoring the outer-minus-inner expressions. Define \(r_b=b_i/b\), \(r_h=h_i/h\), \(g_b=(b-b_i)/b\) and \(g_h=(h-h_i)/h\). Then

\[
A=bh(g_b+r_b g_h),\quad
I_{xx}=\frac{bh^3}{12}\left[g_b+r_b g_h(1+r_h+r_h^2)\right],
\]
\[
I_{yy}=\frac{hb^3}{12}\left[g_h+r_h g_b(1+r_b+r_b^2)\right].
\]

These are algebraically equivalent to subtracting the inner rectangle from the outer rectangle, but avoid catastrophic cancellation when valid walls are very thin. Existing finite/positive geometry checks remain in force; no invalid dimensions are clamped.

The direct Node and Chromium desktop/390px regressions use \(b=h=1{,}000{,}000\) mm and \(b_i=h_i=999{,}999.9999999\) mm. Independent 80-digit Decimal references evaluated from the exact binary64 inputs are \(A=0.20000152289866402\) mm² and \(I_{xx}=I_{yy}=33333587149.774002\) mm⁴. The prior subtractive calculation lost about \(2.52\times10^{-4}\) relative area and \(4.21\times10^{-4}\) relative inertia. The browser test also verifies only the selected member's area/I fields change; E, density, K and every other member remain unchanged.


## Extreme-aspect L-angle preview detail

The L-angle sketch preserves its measured outline at the same uniform scale used for the entered dimensions. When the displayed leg thickness would be below 2 SVG pixels, the preview adds a separate fixed-size leg-detail inset labelled **“Leg detail — not to scale”**. The live caption, SVG accessible name and SVG description announce that the inset is schematic; the original outline continues to expose the exact outer dimensions and leg thickness as metadata. The inset never participates in area, inertia, principal-axis or member-application calculations.

The Chromium regression checks a normal 100 × 80 × 10 mm L-angle has no inset, then checks B=1,000,000 mm, H=1 mm and t=0.001 mm at 1280px and 390px. It verifies the true-scale outline metadata, visible labelled inset, synchronized caption/ARIA description, principal-axis controls, and selected-member application against A=1000.000999 mm² and I1=83333583083083.333 mm⁴. E, density, K and every non-selected member must remain unchanged; the original section is restored before the remaining solver tests.


## Sub-pixel open-section preview detail

The channel and I-section sketches preserve their measured outlines at the same true scale as the entered dimensions. When either the displayed web or flange thickness would be below 2 SVG pixels, the preview adds a separate schematic inset labelled **“Web/flange detail — not to scale”**. The inset carries the actual entered web/flange thickness as metadata, while the original outline retains exact B/H/tw/tf metadata. The live caption, SVG accessible name and SVG description all announce that the detail is schematic. The inset is presentation-only and never changes area, centroid, Ixx/Iyy, section moduli, radii or member application.

The Chromium regression runs at 1280px and 390px. Normal 100 × 80 × 10 × 8 mm channel and I-section previews must not show an inset; the browser applies Iyy to member AC and checks independent references of 2,240 mm² area, 2,264,380.9523809524 mm⁴ for the channel and 1,338,666.6666666665 mm⁴ for the I-section. With B=H=1,000,000 mm and tw=tf=1 mm, the true-scale web/flanges are sub-pixel; the test verifies the measured outline remains dimensionally unchanged, the inset is labelled not to scale, both centroidal axes and the centroid remain present, and accessible caption/description stay synchronized. A solid-circle browser application additionally checks A=1,256.6370614359173 mm² and I=125,663.70614359172 mm⁴. Each application changes only its selected member's area/I and preserves E, density, K and every other member.


## Hollow-circle fourth-power overflow with a representable thin annulus

For a hollow circle, the factored area/inertia expressions must not eagerly form either outer or inner diameter to the fourth power. With a very thin annulus, both (D_o^4) and (D_i^4) can overflow binary64 even though the small dimensionless wall factor makes the final area and centroidal inertia representable. Compute the inertia in the order ((\pi/64)D_o^2 f_I D_o^2), keeping the annulus factor between the two finite squared-diameter terms. The solid-circle path still validates and uses its ordinary fourth power, because no small annulus factor exists to recover range.

The direct Node and Chromium regressions use (D_o=10^{78}) mm and (D_i=9.999999999999998\times10^{77}) mm. The former outer/inner fourth-power intermediates are Infinity, but 120-digit Decimal references evaluated from the exact binary64 inputs give (A=3.230940642955516\times10^{140}) mm² and (I_{xx}=I_{yy}=4.038675803694394\times10^{295}) mm⁴. The tests also verify finite section moduli/radii, unchanged input dimensions, selected-member-only application and preservation of E, density, K and the other members. These are synthetic floating-point range tests, not practical engineering dimensions.


### L-angle principal inertia at extreme aspect ratios

The L-angle inertia tensor is normalized before diagonalization, and its minor principal moment is normally recovered from the normalized determinant divided by the major eigenvalue. At extreme aspect ratios, that normalized determinant (or its subsequent division) can underflow to zero even though the physical minor moment is still a representable positive subnormal. In that case the engine now attempts the unscaled determinant only when it is finite and positive, then divides by the already-computed major principal moment. If the unscaled determinant is also non-finite or non-positive, the existing explicit underflow rejection remains; no value is fabricated.

The regression uses the synthetic floating-range geometry B=1e100 mm, H=1e-139 mm and t=1e-140 mm. A 100-digit Decimal reference from the exact binary64 inputs rounds to I2=8.35e-322 mm⁴. These dimensions exercise numerical representation limits and are not practical engineering design dimensions.


### Composite channel and I-section radii at subnormal inertias

A channel or I-section can have a positive representable area and positive subnormal centroidal inertias while the binary64 values of Ixx/A and Iyy/A are too coarsely quantized for accurate radii. The helper therefore recomputes the composite area, centroid and centroidal inertias in coordinates normalized by max(B,H), evaluates the dimensionless radii there, and multiplies by that length scale once. The reported dimensional area and inertias are not replaced by these normalized intermediates. If the normalized calculation itself cannot retain a positive value, the existing general radius path remains the fallback.

The direct Node and Chromium regressions use B=100s, H=80s, tw=10s and tf=8s with s=10^-82.2. Area remains 8.917600620398223×10^-162 mm²; Ixx rounds to 3.5×10^-323 mm⁴, while channel Iyy rounds to 4.4×10^-323 and I-section Iyy to 2×10^-323 mm⁴. Independent high-precision references from the exact binary64 dimensions give rx=2.0220658289055487×10^-81 mm for both shapes, channel ry=2.0060914979751612×10^-81 mm, and I-section ry=1.5424539802421713×10^-81 mm. The former sqrt(I/A) results differ by more than 1% on both axes. These synthetic dimensions exercise floating-point representation limits, not practical engineering design sizes; the physical subnormal inertias themselves remain quantized.

### L-angle subnormal inertia tensor and principal-property recovery

When the L-angle's dimensional centroidal inertias fall below the binary64 normal range, their quantization can corrupt derived properties even though area, principal moments, section moduli and radii remain representable. For example, B=1e-80 mm, H=8e-81 mm and t=1e-81 mm produced more than 1% error in both radii and more than 1 degree of principal-axis error when the engine used the rounded physical Ixx/Iyy/Ixy values directly.

For this subnormal case, the helper recomputes the same two non-overlapping rectangles after dividing all dimensions by max(B,H). It derives normalized area, centroid, Ixx/Iyy/Ixy, principal eigenvalues, extreme-fibre distances, section moduli and radii, then restores physical units in a scale-safe multiplication order. The reported dimensional inertias and product of inertia are rounded only when converted back to mm-based units. Ordinary-scale and extreme-aspect-ratio cases retain the existing calculation path when the normalized recovery cannot safely represent every required result.

The direct Node and Chromium regressions use exact binary64 input dimensions and independent 120-digit Decimal references. The case retains positive subnormal Ixx/Iyy/Ixy and principal moments, while normalized centroid, section moduli, radii and principal-axis angle match within 5e-13 relative error. Chromium exercises the same calculation at 1280px and 390px. These synthetic dimensions are numerical-range tests, not practical structural design dimensions.


## Subnormal circular section-modulus precision

For solid and concentric hollow circles, the helper retains the existing I/c section-modulus calculation at ordinary scales. When the dimensional circular inertia is subnormal, it instead evaluates the equivalent identity S = (π/32)·Do³ for a solid circle and S = (π/32)·Do³·(1 − (Di/Do)^4) for an annulus. The annulus multiplier is reused from the factored area/inertia calculation, avoiding direct fourth-power subtraction and division of a quantized subnormal inertia. This fallback applies only when I is below 2.2250738585072014e-308; it does not claim to recover a section modulus that is itself unrepresentable.

The regression uses Do = 3e-81 mm and, for the annulus, Di = 1.5e-81 mm. Both inertias round to the minimum positive binary64 value while exact section moduli remain normal. The former I/c result is over 20% high; direct Node and 1280px/390px browser checks compare corrected values with independent 120-digit Decimal references within 5e-13 relative error. Ordinary 40 mm circle calculations retain the original path.


## Subnormal composite section-modulus precision

Channel and I-section section moduli retain the ordinary dimensional I/c calculation while the corresponding physical inertia is normal. When Ixx or Iyy is subnormal, the helper reuses its normalized composite-rectangle inertia and normalized extreme-fibre distance: Sx = L³·IxxNorm/cYNorm and Sy = L³·IyyNorm/cXNorm, where L=max(B,H). The scale factor is multiplied from the normalized ratio outward so the implementation does not first form L³. Each axis switches independently; dimensional area and Ixx/Iyy outputs remain unchanged.

The Node and Chromium regressions use B=100·10^-82.2 mm, H=80·10^-82.2 mm, tw=10·10^-82.2 mm and tf=8·10^-82.2 mm. Both shapes have positive subnormal Ixx/Iyy while section moduli remain representable. Exact-binary64 120-digit Decimal references are Sx=1.444703108127935e-242 mm³ for both shapes; channel Sy=9.048880575086456e-243 mm³ and I-section Sy=6.725157272628184e-243 mm³. The former I/c path differs by 5–24%; corrected results are checked within 5e-13 relative error at desktop and 390px. These synthetic dimensions test floating-point range, not practical structural design.


## Axis-separated normalization for extreme composite aspect ratios

The channel and I-section property helper normally normalizes both coordinates by the larger of B and H. For an extreme aspect ratio, that can make the normalized thin-axis inertia underflow even though the dimensional Ixx remains a positive subnormal and the physical radius/section modulus are representable. The common-scale path is retained when its normalized area and both inertias remain in the normal binary64 range. Otherwise the same non-overlapping rectangles are normalized independently by B along x and H along y.

With dimensionless area A*, centroidal inertias Ixx* and Iyy*, and normalized extreme-fibre distances cX* and cY*, the dimensional relationships are A=B·H·A*, Ixx=B·H³·Ixx*, Iyy=B³·H·Iyy*, rx=H·sqrt(Ixx*/A*), ry=B·sqrt(Iyy*/A*), Sx=B·H²·Ixx*/cY*, and Sy=B²·H·Iyy*/cX*. The section-modulus scale products are restored with exponent-scaled multiplication so an intermediate product does not overflow or underflow before a representable result is formed. Reported dimensional area and Ixx/Iyy remain on the existing physical calculation path.

The direct Node and Chromium regressions use B=1e150 mm, H=1e-154 mm, tw=1e-154 mm and tf=4.9e-155 mm for both channel and I-section. Ixx is positive subnormal while Iyy is normal. Independent 120-digit Decimal references from the exact binary64 dimensions give rx=2.9160475533388224e-155 mm, ry=2.8867513459481288e149 mm, Sx=1.6666533333333332e-159 mm³ and Sy=1.6333333333333333e145 mm³. The previous max-dimension normalized path lost the thin-axis inertia and fell back to rounded physical I/A and I/c, producing relative errors above 1e-11. Corrected properties are checked within 5e-13 at desktop and 390px. These synthetic dimensions exercise floating-point limits, not practical structural design.


## Hollow-cavity area underflow versus net-property representability

Hollow-section validity depends on positive, strictly contained inner dimensions and representable net section properties. The helper does not need to materialize the cavity's own area or squared diameter merely to validate the geometry: either intermediate can underflow to zero even though the outer/net area, both centroidal inertias, section moduli and radii are finite. Hollow-rectangle and hollow-circle properties therefore continue through their factored dimensionless width/depth or inner/outer ratios. Genuinely unrepresentable net area or inertia is still rejected by the existing final property checks.

The regression uses synthetic binary64 boundary inputs only (not engineering design dimensions):

- Hollow rectangle: outer dimensions 1e100 × 1e-100 mm, inner dimensions 1e-162 × 1e-162 mm. The inner area rounds to zero, while net area is 1 mm², Ixx is approximately 8.333333333333334e-202 mm⁴, Iyy is approximately 8.333333333333332e198 mm⁴, and both section moduli/radii remain finite.
- Hollow circle: outer diameter 1e-50 mm, inner diameter 1e-200 mm. The inner-diameter square rounds to zero, while annulus area is approximately 7.853981633974483e-101 mm², inertia is approximately 4.908738521234052e-202 mm⁴, and section modulus/radius remain finite.

For both cases, all returned net properties match the corresponding solid envelope at binary64 precision because the cavity contribution is below the representable resolution. Direct Node and Chromium regressions also verify input immutability, frozen results and desktop/390px execution.


## Scale-safe axial member stiffness EA/L

The parser normally evaluates axial stiffness as the direct binary64 expression E*A/L. It keeps that path whenever the intermediate product is normal and the final quotient is finite and positive, preserving established ordinary-scale results. If E*A overflows or underflows (or the final quotient is not representable on that path), a positive-binary exponent decomposition evaluates the same product/quotient without materializing the dangerous intermediate. The final value is still required to be finite and strictly positive: genuinely overflowing or underflowing stiffness is rejected with the existing diagnostic.

Two synthetic exact-binary64 cases exercise both sides of the range. With E=1e299 GPa, A=1e308 mm² and L=1e308 m, the old E*A intermediate overflows although EA/L rounds to 9.999999999999999e301 N/m. With E=1e-16 GPa, A=5e-315 mm² and L=2e-12 m, the old intermediate rounds to zero although EA/L rounds to 2.49997217e-316 N/m. Node references use 120-digit Decimal arithmetic on the exact binary64 inputs; the Chromium smoke repeats both cases at 1280px and 390px. These are numerical-range fixtures, not physical design examples.

 
## Scale-safe optional member mass from L·A·ρ

When density is supplied, the parser calculates member mass directly from length, cross-sectional area and density. It preserves the ordinary left-to-right product when the intermediate volume and final mass are normal finite values; otherwise it combines binary exponents so an overflowing or underflowing intermediate volume does not discard a representable final mass. Zero density remains a valid zero mass, while a genuinely unrepresentable final mass is rejected.

The Node and desktop/390px Chromium regressions cover a 2e-12 m member with a minimum-subnormal area and 1e308 kg/m³ density (the old volume rounded to zero although mass is 9.88131291682493e-28 kg), and a 1e308 m member with 9.999999999999999e301 m² area and 1e-310 kg/m³ density (the old volume overflowed although mass is 9.999999999999968e299 kg). These are exact-binary64 numerical-range fixtures, not physical design examples.

## Preview and material-export volume range

A positive member can have a representable mass even when its SI geometric volume L·A is smaller than the binary64 range. The FEM parser retains the scale-safe mass calculation, but the pre-solve preview and material-schedule CSV require the volume itself to be representable. They now reject a positive L·A product that rounds to zero with an explicit member-specific underflow diagnostic, rather than displaying or exporting a false zero. Existing overflow rejection is unchanged. This does not alter parseModel, the stiffness calculation or the FEM solve path; it only prevents inspectJSON and exportMaterialCSV from publishing an unrepresentable volume.


## Final positive member-mass underflow

A positive density and positive member geometry whose final scale-safe product L·A·ρ rounds to zero is rejected with a member-specific mass-underflow diagnostic rather than being exposed as a valid zero mass. Explicit density zero remains valid and produces zero mass. This is distinct from an intermediate L·A underflow: when a positive final mass remains representable, the exponent-scaled product continues to accept it.

The direct Node and registered Chromium desktop/390px regressions use a 2e-12 m member, E=200 GPa, area=5e-318 mm² (which converts to Number.MIN_VALUE m²), and density=1e-300 kg/m³. Its axial stiffness remains positive (~4.940656458412466e-301 N/m), but its final mass is below binary64 range and must be rejected. The same member with zero density remains valid; with density 1e308 kg/m³ its mass remains 9.88131291682493e-28 kg despite the intermediate volume underflow. These are synthetic floating-point boundary fixtures, not physical design dimensions.


## Centered I-section web below the binary64 area range

A positive I-section web may have a web-area product that rounds to zero even though the two flange areas, total section area, both centroidal inertias, section moduli and radii remain representable. The central web is the only composite sub-piece permitted to take this path, and only when its two dimensions are each below 1 mm and its computed center exactly matches the section center. Under those conditions its local rectangle inertias are smaller than its already-underflowed area, and symmetry makes its parallel-axis offsets zero; omitting those unrepresentable contributions does not change any binary64 section property. The total section area and both final inertias still pass the ordinary positive/finite checks. Channel-web and all other composite-piece area underflow continue to be rejected.

The Node and registered Chromium desktop/390px regressions use B=1e100 mm, H=1e-100 mm, tw=Number.MIN_VALUE mm and tf=1e-101 mm. The central web area rounds to zero, while Decimal references from the exact binary64 dimensions give area 0.2 mm², Ixx approximately 4.066666666666667e-202 mm⁴, Iyy approximately 1.666666666666667e198 mm⁴, Sx approximately 8.133333333333334e-102 mm³, Sy approximately 3.333333333333334e98 mm³, rx approximately 4.509249752822894e-101 mm and ry approximately 2.8867513459481287e99 mm. The same geometry remains rejected as a channel because its underflowed web is not centered and must not be silently discarded. These are synthetic binary64 boundary fixtures, not engineering design dimensions.


## L-angle principal-axis recovery when dimensional Ixy underflows

A thin flange on an otherwise nearly square L-angle can make the dimensional product of inertia smaller than binary64's minimum subnormal even while area, both centroidal inertias, principal moments, section moduli and radii remain representable. Rejecting solely because the rounded Ixy is zero loses a valid section. When Ixy rounds to zero, the helper now re-evaluates the two-rectangle tensor at unit scale; it restores dimensional properties (allowing the physical Ixy to remain correctly rounded to zero) while calculating the principal-axis angle from the normalized product. Positive-definiteness, principal-moment, section-modulus and radius checks remain in force.

The synthetic exact-binary64 fixture uses B=H=1e-75 mm and t=B·(1−1e-14). Its exact-binary64 Decimal reference has Ixy≈−2.470544411709329e-329 mm⁴, which rounds to zero, while Ixx=Iyy≈8.333333333333331e-302 mm⁴, both principal moments round to the same positive value, and the principal-axis angle is 45°. The section moduli are approximately 1.6666666666666664e-226 mm³ and radii approximately 2.886751345948129e-76 mm. Node and registered Chromium regressions check these values at 1280px and 390px. This is a numerical-range fixture, not an engineering design dimension.



## L-angle dimensional Ixy signed-zero presentation

When the dimensional product of inertia is smaller than the binary64 range, its returned value is canonicalized to positive zero rather than exposing `-0`. The normalized two-rectangle tensor retains the signed Ixy value and remains authoritative for the principal-axis angle, so this presentation normalization does not discard the orientation information used by the calculation.


## Signed force and moment resultant range safety

The Truss JSON preview now evaluates signed applied-force resultants and the signed global-origin moment with scale-normalized Neumaier accumulation. This avoids rejecting a finite physical resultant merely because an early partial sum overflows before later nodal loads cancel it. Terms that underflow only after normalization are accumulated in a separate compensated residual, so a subnormal load is not silently discarded when it lies between two much larger cancelling loads.

For example, the SI sequence (1e308, 1e308, -1e308) has the finite resultant 1e308 even though ordinary left-to-right binary64 addition overflows at the second term. The same rule applies independently to x/y force totals and to the signed moment terms x·Fy and -y·Fx. Each individual moment product must still be representable, and a genuinely non-finite final resultant remains rejected with a finite-number diagnostic. This is compensated binary64 summation, not arbitrary-precision arithmetic.

The Node regression covers horizontal and vertical force cancellation, a minimum-subnormal force between cancelling large loads, moment cancellation, and true final force overflow. The registered Chromium regression repeats these cases at 1280px and 390px. This preview change does not alter the FEM stiffness matrix or displacement solver.


## Force-balance diagnostic cancellation safety

The solved-model force-balance diagnostic now combines all applied nodal loads and support reactions in one scale-normalized compensated sum per axis. It no longer reduces external loads and reactions independently before adding the two totals. This matters when both intermediate totals overflow but their combined equilibrium residual is finite.

The regression uses a fully triangulated reference model with one free, unloaded translation and three large restrained horizontal loads. The old separate reductions produce +Infinity and -Infinity, whose sum is NaN; the corrected diagnostic returns exactly zero in both axes. Node and Chromium tests exercise this at desktop and 390px viewports. This changes only the reported force-balance diagnostic; stiffness assembly, displacement solution, reactions and energy verification remain unchanged.

## Subnormal normalized summands in signed resultants

The compensated resultant helper treats every normalized quotient below the smallest normal binary64 value as a residual term, not only quotients that round all the way to zero. A nonzero subnormal quotient is too coarsely quantized to preserve its relative precision when multiplied back by a very large scale. Retaining the original finite term in the residual avoids that precision loss after large positive/negative cancellation.

The additional regression uses a 1e-10 N term between +1e308 N and -1e308 N. The naive normalized quotient is subnormal and the previous compensated-only path returned about 9.999987484955998e-11 N (approximately 1.25 ppm low); the revised residual path returns the expected binary64 1e-10 N. The existing minimum-subnormal residual, horizontal/vertical force, moment cancellation and genuine-overflow tests remain.


## Exact mixed-sign binary64 resultants

Mixed-sign applied-force, applied-moment and solved force-balance reductions now accumulate the exact integer representation of the supplied finite binary64 terms, then round once to the nearest binary64 result (ties to even). This avoids precision loss when a normalized Neumaier sum and its original-unit residual nearly cancel: a 79-node preview with +1e308 N, -1e308 N, 35 loads of 2.3 N, 40 loads of -2 N, -0.5 N and +1e-10 N previously returned about 9.99875737761613e-11 N instead of the correctly rounded 9.99937827510621e-11 N. The same reference is checked for the signed origin moment in Node and Chromium at 1280px and 390px. Same-sign reductions retain the scale-normalized compensated path, and browsers without BigInt retain the prior bounded fallback. Inputs and outputs remain binary64; this is exact accumulation of the supplied binary64 values, not arbitrary-precision engineering arithmetic.


## L-angle area and inertia summation precision

The L-angle is decomposed into two non-overlapping rectangles. Its positive area terms previously passed through the scaled compensated reducer, which can itself shift a two-term total by one ulp after normalization and rescaling. Its Ixx/Iyy paths also added each rectangle's local and parallel-axis terms left-to-right, making the result order-dependent. The helper now uses the existing exact binary64 accumulator to sum the already-rounded rectangle areas, first moments, local inertias and parallel-axis terms once (nearest/ties-to-even) when BigInt is available; the existing scaled compensated fallback remains for environments without BigInt. Ixy uses the same sum contract for consistency. This does not make the underlying rectangle products arbitrary precision.

Two synthetic binary64 regressions cover distinct failures. For B=8,605,413.972369973 mm, H=4.292204701476468 mm and t=2.136125318978258e-5 mm, the previous scaled area reduction returned 183.8225183531027 mm² instead of 183.82251835310274 mm², shifting the centroid; the previous Ixx reduction returned 0.0005630523010274838 mm⁴ instead of 0.0005630523010274837 mm⁴. For B=1.1143751945503119e-20 mm, H=4.305111224234166e-16 mm and t=2.015788401705846e-21 mm, the previous Iyy reduction returned 2.94557285397156e-79 mm⁴ instead of 2.9455728539715605e-79 mm⁴. Direct Node and Chromium regressions verify area, centroid and both inertias at 1280px and 390px. These extreme dimensions are floating-point stress fixtures only, not physically meaningful design examples.


## Compensated nodal reaction accumulation

Each nodal internal-force resultant is now accumulated from the already-rounded binary64 terms K_ij*u_j together with the negative applied load using the shared finiteSignedSum routine. This avoids order-dependent support reactions when a small term is bracketed by large opposite member-force contributions. Mixed-sign terms use the exact binary64 accumulator when BigInt is available; the compatibility path remains compensated. Returned reactions and the global force-balance diagnostic remain ordinary binary64 values; this is not arbitrary-precision FEM.

The regression uses three one-metre horizontal bars with axial stiffness 1e20 N/m and applied loads of 1 N, +1e16 N and -1e16 N. The support reaction is -1 N and the global horizontal force balance is zero. The former sequential row reduction evaluates the member terms -1, -1e16, +1e16 as zero and loses the support reaction. Node and Chromium tests assert the lost naive result, corrected reaction, zero force balance, free-DOF residual and energy check at 1280px and 390px. This is a synthetic floating-point stress fixture, not a physical structural design example.

## Compensated energy-balance diagnostics

The solver accumulates free-DOF external work and member elastic strain energy with the shared finite signed summation helper. It then evaluates the balance residual as one signed sum of the two elastic-energy totals and negative external work. This preserves low-order contributions when a small member is listed after a much larger member and avoids an overflowing intermediate (2U) when the final signed residual is representable. Values remain binary64; the check is a numerical consistency diagnostic, not an energy-accuracy certificate.

A regression fixture uses exact binary powers: each member has stiffness 65536 N/m; one bar carries 2^36 N over 2^20 m (2^55 J), and 32 independent bars each carry 256 N over 1/256 m (0.5 J). Ordinary member-order accumulation remains at 2^55 J because each small term is below half an ulp; the compensated result is exactly 2^55+16 J. External work is 2^56+32 J, so the signed energy residual and normalized error are zero. Node and Chromium tests run the same reference model at desktop and 390px viewports. These are floating-point stress fixtures, not physical structural dimensions.


The solve result exposes the signed `energyResidual` in joules, computed from the same rounded binary64 elastic-energy and external-work totals used by the identity check. The Truss Studio verification panel displays this absolute signed residual alongside the normalized error, so users can distinguish the energy scale from the relative consistency measure. Neither value certifies material strength, stability or code compliance.

## Aggregate member-mass preview

The pre-solve `inspectJSON` result reports `knownMemberMassSubtotal` in kg, `unknownDensityMemberCount`, and `totalMemberMass`. A total is present only when every member has an explicit density; an omitted or blank density remains unknown and never silently contributes zero. Explicit density zero is valid known data. When only some densities are known, the UI labels their sum as a subtotal and states how many members still lack density; when none are known it reports that a mass estimate is unavailable. The aggregate uses the shared finite signed accumulator and rejects a genuinely unrepresentable subtotal rather than displaying Infinity. This is a material estimate, not a structural-capacity or safety certification.


## Post-solve Euler ratio range handling

The optional compression-only Euler screen must not make an otherwise finite linear-elastic FEM solution fail merely because one displayed ratio is outside binary64 range. For positive compression demand and positive Euler critical load, the solver reports each representable ratio as a finite number. If `Pcomp/Pcr` or `Pcr/Pcomp` overflows or underflows, its numeric field is `null` and the corresponding `eulerUtilizationRange` or `eulerLoadRatioRange` is `overflow` or `underflow`. The other ratio remains available when representable. The assessment compares the original positive demand and critical-load operands directly, so the below/at-or-above classification does not depend on either rounded quotient. Truss Studio displays `> max` or `< min` for a ratio outside binary64 range and keeps the explanatory range detail in the assessment; result CSVs retain the assessment text when a numeric cell is unavailable.

Node and registered Chromium regressions use three synthetic, non-design fixtures. One has a representable utilization but an overflowing `Pcr/Pcomp`; another has a representable load ratio but an overflowing utilization; the third reaches the minimum positive Euler load and forces the reciprocal load ratio to underflow to zero. All must return finite displacements, equilibrium and energy diagnostics, preserve the correct Euler classification, and identify unrepresentable ratios without returning Infinity or rejecting the solve. These fixtures test floating-point reporting limits only; the Euler screen remains an ideal elastic comparison, not a code-compliant buckling resistance or design certification.


## Euler screening below the general zero-force threshold

The ordinary member-force classification suppresses forces within ±1e-8 N as numerical zero. That presentation threshold must not suppress a physically meaningful optional Euler comparison when both second moment I and effective-length factor K are supplied. For Euler-enabled members, every strictly negative solved axial force is retained as compression demand and classified as compression for the screen; the comparison uses the unrounded positive demand against Pcr. Members without I/K retain the existing ±1e-8 N display/noise threshold and remain unassessed. This distinction prevents small-scale or low-load models from incorrectly reporting “No compression demand” when a sub-threshold force exceeds a correspondingly small Euler critical load.

Node and registered desktop/390px Chromium regressions use a 2 m bar with E=1 GPa, area=1e-3 mm², I=4e-9 mm⁴ and K=1. A 5e-12 N compressive load is below Pcr≈9.869604401089358e-12 N; a 5e-9 N compressive load is above it. Both are below the general 1e-8 N force threshold. The regressions verify the compression demand, member type, utilization and assessment, plus finite equilibrium/energy diagnostics. A matching model without I/K confirms that the established near-zero classification is unchanged. These are numerical-scale tests, not physical design examples.


## Per-member Euler input readiness

The pre-solve member-material table labels the optional ideal Euler estimate inputs independently for every member: `Not supplied` when neither I nor K is present, `Missing I` when only K is supplied, `Missing K` when only I is supplied, and `Ready` when both are supplied and the critical load can be calculated. A missing input is not treated as zero and does not prevent the axial-only FEM solve.. The table is inside a collapsed native disclosure whose visible summary explicitly names Euler readiness and announces the current member count; users open that summary to inspect the per-member rows. The Chromium smoke verifies the initially collapsed state, opens the disclosure through its summary before reading cell contents, and verifies the live count changes from `3 members` to `1 member` and back when switching examples. The machine-readable `inspectJSON().memberMetrics[].eulerInputStatus` values are `not-supplied`, `missing-I`, `missing-K` and `ready`. The table's Euler Pcr remains blank unless both validated inputs produce a representable positive critical load.

Node and registered desktop/390px Chromium regressions cover all four readiness states, confirm incomplete pairs do not produce Pcr, and verify that editing and restoring the model refreshes the per-member labels.
