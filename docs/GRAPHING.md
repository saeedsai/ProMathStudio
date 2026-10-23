# 2D and 3D graphs

## Plotting

Open the **2D & 3D graphs** tab. Pick the dimension at the top of the graph panel.

**2D:** write one function per line; examples:

```text
y=sin(x)
y=cos(x)
y=1/(x-1)
y=exp(-x^2)
y=if(x<0,-x,x)
```

Use just the functions you want; each gets its own curve. Graphing reads the selected x/y bounds from the control fields. Functions separated by newlines or semicolons are supported.

**3D:** enter one surface, for example:

```text
z=sin(sqrt(x^2+y^2))
```

Other examples: `z=x^2-y^2`, `z=exp(-(x^2+y^2)/5)`. Adjust x/y/z min/max before plotting.

## Interaction

- **Plot functions** renders the latest input.
- **Drag** pans 2D or rotates 3D.
- **Wheel** zooms when supported by the browser/device.
- **Reset view** restores viewing settings.
- **Export PNG** downloads the current canvas as an image.
- **Add to current graph** in Connected workspaces adds functions without replacing current 2D curves.

## Transfer rules

Typing an equation such as `x^2=1` and sending it to **Graph 2D** converts it to a residual function `y=(x^2)-(1)`; its zero crossings correspond to equation roots. Explicit `y=...`/`z=...` definitions are kept as functions.

## Supported notation and restrictions

The canvas evaluator supports conventional arithmetic, trig, logarithms, exponentials, abs and some piecewise forms; unsupported syntax produces a graph status/error instead of an arbitrary code execution. Trigonometric graph inputs use radians irrespective of calculator angle mode. Sampled plots cannot faithfully show every discontinuity, vertical asymptote or steep/narrow feature. There is no general implicit/parametric plotter.

[Syntax](SYNTAX_REFERENCE.md) · [Features and limitations](FEATURES_AND_LIMITATIONS.md)
