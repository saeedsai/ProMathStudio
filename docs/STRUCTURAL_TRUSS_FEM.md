# 2D Truss Studio — canonical structural-truss-fem-2d

**Section-helper behavior on dev:** The accessible section helper remains intentionally inside the initially collapsed “Member materials and section properties” disclosure. The summary's `aria-controls="member-material-content"` references a wrapper containing both the member metrics table and section helper. Browser tests must verify the controlled region starts hidden, activate the summary, and verify the helper and target selector are visible before interaction; later scenarios must open the disclosure conditionally rather than blindly toggling a state left open by an earlier scenario. Applying properties requires one unambiguous member ID and preflights both destination fields before writing area and I. Unsupported axes, duplicate IDs, invalid/overflow geometry and missing fields reject without partial member mutation. The selected-member regression verifies a 40 × 60 mm rectangle gives A=2,400 mm² and Ixx=720,000 mm⁴ while preserving E, density, K and all other members. Any edit to section shape/dimensions, target member, selected axis, or a member's ID/area/I clears the previous application result; a stale “applied” message must never describe a different configuration. Loading a new model also clears the prior result.

**Import integrity on dev:** The browser snapshots immutable File.size before awaiting arrayBuffer(), validates the actual returned byteLength against the same 1 MiB budget, then strictly decodes UTF-8. A short read and a longer-than-declared read now have distinct diagnostics with exact expected/received counts. Both mismatches are rejected before JSON parsing, even when the differing bytes are only legal trailing whitespace; the active node/member inputs and prior solved results remain unchanged and aria-busy returns to false. Browser regressions cover both directions with actual File objects at 1280px and 390px, plus malformed UTF-8, actual BOM bytes and exact/over-limit boundaries.

**Verification baseline:** The immediately preceding dev head d1c25300184851af0c52c9619571c2878af5c458 passed exact-head Push Quality [#45202567594](https://github.com/saeedsai/ProMathStudio/actions/runs/45202567594) and PR Quality [#45202584053](https://github.com/saeedsai/ProMathStudio/actions/runs/45202584053), each with 218/218 steps successful and zero failures/skips. This new read-direction candidate requires fresh exact-head CI; it is not released.


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

The section-property helper is inside the native `<details id="member-material-details">` disclosure. It is intentionally collapsed on initial load; a user opens “Per-member material breakdown” to access the material schedule and helper. Browser regressions must activate that summary and assert `#section-helper` is visible before interacting with its controls.

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
