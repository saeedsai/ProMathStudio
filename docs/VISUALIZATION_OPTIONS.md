# Visualization appearance, table zoom and calculator output formats

## Graphs and charts

Open **Graphs → Appearance · colors and styles** to customize 2D mathematical curves, 3D surfaces and bar/pie charts. Choose Classic, Bright, Pastel, Monochrome or a custom color; select solid/dashed/dotted lines, thin/medium/thick strokes, and a background. The panel is collapsed by default to keep plotting uncluttered.

The appearance settings are saved as `graph.appearance` in the existing project JSON (optional, backward-compatible). For example:

```json
{"palette":"bright","color":"#536be8","line":"dashed","width":"5","points":"circle","background":"#ffffff"}
```

The point shape selector is available for future per-series styling; currently points in imported datasets retain their existing circular markers. Bar and pie charts honor palette selections. Data-series point colors are currently separate from mathematical equation curve colors.

## Data Tables zoom

Use the **Table zoom** minus/plus buttons or slider to scale the editable sheet from **50% to 200%**, in 10% steps. Use **100%** to reset. Zoom changes display only, not stored values or formula computations. The selection persists in this browser using `promath-table-zoom`; exporting a project does not transfer the zoom between devices.

## Calculator number display

Under Calculator, choose **Number display**:
- **Auto** — standard shortest reasonable representation.
- **Decimal** — fixed-decimal presentation to the chosen precision.
- **Scientific** — exponent notation, such as `1.23456789e+8`.
- **Engineering** — exponent multiple of three, such as `123.456789e+6`.

Calculation uses the same numeric engine; output formatting does not change the internal result. Significant-figure precision still controls rounding. Large standalone BIN/HEX integers remain exact conversion strings. Calculator number format is saved with the project as `calculator.format`.
## Multiple equations and per-series colors

**Primary color is always applied to the first graph**, regardless of the selected palette. For second and subsequent equations the selected palette supplies distinct colors. With **Custom color**, additional series receive distinct hues based on the primary color rather than all appearing identical.

The **Individual graph colors** row appears automatically when there are functions in the Graph input. Pick a color for any equation independently; graph-specific overrides are saved in `graph.appearance.series` in project JSON. To return a series to the palette, select another palette or restore default project appearance. Background, line weight and line styles apply across the graph.
