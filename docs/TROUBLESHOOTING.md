# Troubleshooting

## Equation does not mean what I typed

Use parentheses for precedence: `x/(x-1)` rather than `x/x-1`. For negative fractional exponents use `x^(-1/2)`. Some palette expressions only create notation; use the solver for execution.

## Calculator says it cannot calculate

Calculator is numeric. Use the symbolic solver for unknowns and move a specific numeric root back into calculator. Ensure angle mode is correct: degrees vs radians.

## Complex square roots and logarithms

Principal complex branches are used. `sqrt(-1)` is `i`; square roots in equations typically have both positive and negative roots and require **Solve**, not evaluation of one principal square root.

## SymPy is unavailable or slow

Check connectivity and content blockers that may interfere with the CDN Pyodide loader. Use the Built-in (offline) engine temporarily. RootOf is an exact root representation, not an error. Reduce large expressions when browser resource limits are reached.

## Graph is blank or discontinuous

Use explicit `y=f(x)` or `z=f(x,y)` form, valid finite bounds, and supported math functions. Inspect graph status. Discontinuities and poles can be clipped; zoom or change the range.

## Cannot copy to Word

Some browsers block clipboard APIs outside secure contexts. Download an editable Word `.docx` instead or export as an image for visual fidelity. Clipboard paste may not preserve editable Office Math.

## Work disappeared after closing

Browser localStorage is not guaranteed to persist (especially private browsing). Export a `MathStudio_Project.json` backup and later choose **Open project**. Import overwrites the currently saved notebook/history.

## GitHub Pages not live

Check repository Settings → Pages for enabled deployment source. Check the Actions workflow run, the published URL and recent deployment logs. A pushed `index.html` alone does not guarantee an accessible Pages site.

## Reporting problems

Attach the input, operation and engine, expected/actual outputs, browser/version, and whether offline/CDN-backed functions were used. Avoid publishing private equations or personal project JSON files in public issues.
