# Features, scope and limits

This describes the **current single-file implementation**, not aspirational features.

| Feature | Present | Limitations |
|---|---|---|
| Scientific calculator | Yes | Numeric scalar computations; floating point, not arbitrary precision |
| Complex numbers | Yes | Principal branches apply to roots/logarithms; results may be approximate |
| Equation typesetting | Yes | Rendering is MathML; clipboard compatibility varies |
| Greek/advanced symbols | Yes | Some are display-only and cannot be numerically executed |
| One-variable built-in CAS | Yes | Polynomial/rational scope; higher-degree forms need SymPy |
| Browser SymPy | Yes | CDN download required for initial use; runtime/browser resources can limit complex problems |
| Exact/numeric roots | Yes via SymPy | No elementary radicals for every polynomial; RootOf may be shown |
| Matrix/array layout | Yes | Typesetting and SymPy coverage vary by operation |
| 2D function graphing | Yes | Explicit y=f(x), multiple curves; not a general implicit/parametric plotter |
| 3D function graphing | Yes | z=f(x,y) mesh; not a full 3D CAD or symbolic surface engine |
| Equation transfer | Yes | Transfers mathematical text and supported result forms; not all CAS objects map to calculator |
| Word editable equations | Yes | Native .docx; Word clipboard formatting is browser-dependent |
| Persistent project | Yes | JSON format v1 only; import **replaces** saved notebook/history |
| Offline operation | Partial | Basic app works offline; first full SymPy load requires network |
| Cross-device synchronization | No | Files remain in each browser until explicitly exported/imported |

**Not guaranteed:** full MATLAB Symbolic Math Toolbox equivalence; general PDE/ODE solution; arbitrary Python code execution; guaranteed real-time graphing for every mathematical expression; a hosted backend; automatic cloud sync; all possible LaTeX macros.

## Mathematics reliability

1. Exact vs floating-point: calculator uses JavaScript-style finite precision; SymPy can produce exact symbolic forms.
2. Principal values: complex logarithms and roots have branch conventions.
3. Root sets: beware extraneous roots caused by denominator cancellation or applying non-invertible transformations.
4. Trigonometric equations may have infinite families; exact sets and selected principal solutions differ.
5. Graph sampling can miss singularities/very narrow peaks.
6. Always verify consequential calculations independently.

See [Symbolic engine](SYMBOLIC_ENGINE.md) and [Graphing](GRAPHING.md).
