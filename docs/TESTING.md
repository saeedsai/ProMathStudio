# Test and quality assurance plan

## Automated checks

Run the dependency-free unit suite:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

It inspects the HTML structure, all four workspaces, shared routing controls, embedded SymPy Python syntax and export controls.

Browser smoke tests:

```sh
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/smoke_browser.py
```

The Playwright smoke suite exercises the equation editor, notebook, offline Expand, a numeric calculator result, routing to 2D/3D canvas, and JSON export without connecting to the Pyodide CDN. It is not a full mathematical correctness proof.

## Manual regression checklist

- [ ] Desktop and mobile layouts do not overlap; palette/navigation can be used.
- [ ] `5! + sin(pi/2)` gives 121 in radians; `sqrt(-1)` gives `i`; inverse trig degree/radian toggles behave correctly.
- [ ] `(x-1)^2` expands to `x^2-2x+1`.
- [ ] `x^2=1` gives ±1; `x^2=-1` gives ±i.
- [ ] Rational simplification does not falsely accept a denominator-zero solution.
- [ ] SymPy loads online and solves a degree-9 polynomial or returns all root objects/approximations.
- [ ] Editor updates live MathML; palette symbols, matrices and Greek input work.
- [ ] Word .docx opens with editable equations and LaTeX is parseable.
- [ ] 2D supports multiple curves; 3D drag/zoom and PNG export work.
- [ ] Notebook rows can be sent to calculator, solver, editor and graph.
- [ ] Project save/import round trip restores working equation, notebook, calculator state and graph parameters.
- [ ] Invalid project JSON is rejected without deleting existing work.
- [ ] No serious console errors; inaccessible CDN/clipboard/storage fail gracefully.

## Release criteria

Static checks and browser smoke must pass for a code update; verify high-risk math operations separately. GitHub Actions is a signal, not proof of all correctness. Document any known failure in `docs/FEATURES_AND_LIMITATIONS.md` or `CHANGELOG.md` rather than claiming an unsupported capability.

[Development](DEVELOPMENT.md)
