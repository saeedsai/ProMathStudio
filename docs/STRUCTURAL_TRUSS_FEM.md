# 2D Truss Studio — canonical structural-truss-fem-2d

**Section-helper behavior on dev:** The accessible section helper remains intentionally inside the initially collapsed “Per-member material breakdown” disclosure. Browser tests must open its summary and verify the helper is visible before interaction. Applying properties requires one unambiguous member ID and preflights both destination fields before writing area and I. Unsupported axes, duplicate IDs, invalid/overflow geometry and missing fields reject without partial member mutation. The selected-member regression verifies a 40 × 60 mm rectangle gives A=2,400 mm² and Ixx=720,000 mm⁴ while preserving E, density, K and all other members.

**Import integrity on dev:** The browser snapshots immutable File.size before awaiting arrayBuffer(), validates the actual returned byteLength against the same 1 MiB budget, then strictly decodes UTF-8. A short read and a longer-than-declared read now have distinct diagnostics with exact expected/received counts. Both mismatches are rejected before JSON parsing, even when the differing bytes are only legal trailing whitespace; the active node/member inputs and prior solved results remain unchanged and aria-busy returns to false. Browser regressions cover both directions with actual File objects at 1280px and 390px, plus malformed UTF-8, actual BOM bytes and exact/over-limit boundaries.

**Verification baseline:** The immediately preceding dev head d1c25300184851af0c52c9619571c2878af5c458 passed exact-head Push Quality [#45202567594](https://github.com/saeedsai/ProMathStudio/actions/runs/45202567594) and PR Quality [#45202584053](https://github.com/saeedsai/ProMathStudio/actions/runs/45202584053), each with 218/218 steps successful and zero failures/skips. This new read-direction candidate requires fresh exact-head CI; it is not released.


## How to use

Open `tools/truss-studio.html` in a browser (requires its adjacent `truss-fem.js` and `truss-fem-ui.js`). Select a reference model or edit **Joints**: unique ID, X/Y in metres, Fix X/ Fix Y, forces Fx/Fy in kN (positive right/up). In **Members**, enter start/end IDs, E in GPa, area in mm² and optional density in kg/m³. The **Section property helper** in the material breakdown calculates area, centroidal Ixx/Iyy, elastic section moduli Sx/Sy, extreme-fibre distances cX/cY and radii of gyration rx/ry for solid/hollow rectangles and circles, plus open channels, I-sections and L-angles. L-angles also report Ixy, principal I1/I2 and the major-principal-axis angle; the selected centroidal/principal moment is applied to one member. Sx = Ixx/cX and Sy = Iyy/cY; rx = sqrt(Ixx/A) and ry = sqrt(Iyy/A). Rectangle Ixx is about the horizontal centroidal axis parallel to width; circle I is about any centroidal diameter. These are geometric properties, not design resistances. Optional Euler estimate inputs are I (second moment of area, mm⁴) and K (dimensionless effective-length factor); provide both to calculate Pcr. Either property may be stored alone without producing an Euler estimate; the geometry/member preview remains available and the status explains when the pair is incomplete. Click Analyze truss. Results show member tension/compression force (kN), stress (MPa), joint displacements (mm), support reactions (kN), residual/energy verification and, when I/K are supplied, a compression-only ideal Euler comparison. Gray dotted members represent the original truss; colored amplified lines represent deformed geometry (green tension, orange compression). Change scale or label visibility, export the model as JSON, results as CSV, diagram as SVG; imported legacy SI JSON is converted explicitly. The import status identifies the file's units for optional density (kg/m³), second moment I (m⁴ in legacy SI or mm⁴ in Studio) and effective-length factor K (dimensionless), in addition to the core force, modulus and area units.


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
- Concentric hollow circle: subtract the inner circle from the outer circle for A and equal centroidal I.
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

The non-solving material preview can report the ideal elastic critical load `Pcr = π² E I / (K L)²` when both second moment of area `I` and effective-length factor `K` are supplied. Current Studio JSON/UI uses `I` in mm⁴; legacy SI JSON uses `I` in m⁴ and converts it on import. `K` is dimensionless. The reported `Pcr` is in kN. Missing I/K leaves the estimate blank; supplying only one, non-positive/non-finite values, or an unrepresentable result is rejected. After solving, only compressive axial force is compared with `Pcr`; the result reports utilization `Pcomp/Pcr` and load ratio `Pcr/Pcomp`. Tension is not applicable and zero force is reported as no compression demand without division. This remains an ideal elastic screen, not a geometric buckling solver or code-compliant resistance check; it does not include imperfections, residual stress, local/flexural-torsional modes, inelasticity, code resistance factors or post-buckling. It is an educational idealization, not a certified design check; consult a qualified structural engineer.

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
