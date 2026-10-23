# ProMathStudio

A browser-based mathematics workspace that brings four connected tools into one HTML app.

## Open the app

Open [index.html](index.html) in a modern browser, or enable GitHub Pages (Settings → Pages → Deploy from a branch → `main` → `/ (root)`) to host it.

When Pages is enabled, the expected website address is:
https://saeedsai.github.io/ProMathStudio/

> A live Pages deployment is not guaranteed until GitHub Pages has been enabled and published.

## Features

- **Advanced calculator:** standard and complex arithmetic, factorials, powers, roots, inverse trig functions, angle modes, constants `e`, `pi`, `i`, and history.
- **Equation editor:** live mathematical formatting, extensive symbol palette, LaTeX and Python/SymPy representation, editable Word equation export.
- **Symbolic solver:** expand, simplify, factor, solve, differentiate and integrate. Supports a built-in offline engine plus browser-executed SymPy for more advanced problems.
- **2D/3D graphing:** plot functions `y=f(x)` and surfaces `z=f(x,y)`, including multiple 2D curves, graph interaction, and image export.
- **Connected workspaces:** move working expressions and results between the editor, calculator, solver and graphs. Save and restore a notebook/project.

## Usage

1. Open `index.html` or the published GitHub Pages site.
2. Enter an expression in any workspace, e.g. `(x-1)^2` or `x^2=-1`.
3. Select **Symbolic Solver** and execute to transform or solve it.
4. Use the working-equation controls to send it to another workspace.
5. Save the notebook or export equations, plots, LaTeX, Python code, or Word documents.

## Requirements

- Modern Chrome, Edge, Firefox, or another browser supporting the app's web APIs.
- The basic app runs locally. Full **SymPy** execution needs an internet connection for its initial Pyodide/Python package download. Calculations run in the browser after loading.

## Source

The complete current application is in `index.html`. No build step or web server is required for the basic features.
