# Changelog

Changes are documented in functional groups; historical version numbers are not reconstructed where no tagged release is available.

## 2026-10-23 — Initial GitHub publication and documentation

- Published the connected single-page HTML mathematical application as `index.html`.
- Four interactive workspaces: calculator, equation editor, symbolic solver, 2D/3D graphs.
- Shared working equation, source dropdown, cross-workspace transfer, notebook and project JSON backup.
- Browser-executed SymPy with Pyodide CDN download for advanced operations.
- Mathematical input library, live math notation, Python snippets, LaTeX and Word export, PNG graph export.
- Added full user/developer documentation, static and browser smoke tests, CI and Pages deployment workflow.

## Known limitations

See `docs/FEATURES_AND_LIMITATIONS.md`. In particular, the built-in offline solver is not a complete CAS; SymPy download and hosted deployment must be validated in the target browser/environment.
