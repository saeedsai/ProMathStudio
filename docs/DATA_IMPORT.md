# Import CSV and JSON data into graphs

ProMathStudio lets you plot measured data alongside equations, entirely in your browser.

## How to use

1. Open **2D & 3D Graphs** and choose 2D or 3D.
2. Expand **Import CSV / JSON data to graph**. Choose a `.csv`, `.tsv` or `.json` file.
3. Select the coordinate columns: X and Y for 2D, X/Y/Z for 3D. Auto-detected names include `x`, `y`, `z`, `time`, `value`, and `height`.
4. Choose **Scatter points**, **Connected line + points** (connects in row order) or **3D grid mesh + points**.
5. Click **Fit axes to data** to adjust the graph bounds.
6. Use **Export PNG** for a picture and **Save project** to preserve your imported table, column selections and equations. The **Connected Workspaces** panel stays below the graph.

Imported data overlays any equation plots. Clear the equation text if you want only imported points. Use **Remove data** to return to equations alone.

## CSV examples

```csv
x,y
0,0
1,1
2,4
```

Files need a header row. Comma, semicolon and tab-separated files are supported, including quoted cells. Explicit all-empty records such as `,` or `"",""` are preserved when importing tables, while completely blank physical lines are ignored. Numeric data can use decimal and scientific notation. See [2D CSV sample](../examples/graph_2d.csv).

## JSON examples

Records:
```json
[{"x":0,"y":0,"z":0},{"x":1,"y":1,"z":2}]
```

Coordinate arrays:
```json
[[0,1],[1,3],[2,5]]
```

Objects can wrap records in `data` or `points`, specify `{"columns":["x","y"],"rows":[[0,1]]}`, or provide equal-length numeric arrays such as `{"x":[0,1],"y":[1,2]}`. See [3D JSON grid sample](../examples/graph_3d_grid.json).

## Three-dimensional data

For 3D, select distinct numeric X, Y, and Z columns. Scatter plots draw colored points; connected paths follow the file's row order. **3D grid mesh** draws quadrilateral cells only if every unique X/Y combination occurs exactly once; otherwise it displays points only. It does not triangulate irregular point clouds.

## Validation, privacy and project backups

- Maximum file size **1 MB**, **6,000 data rows**, **32 columns**.
- The first five rows appear in a read-only table preview. Invalid numeric coordinate rows are skipped.
- Data and filenames are treated as plain text; no CSV/JSON code is executed.
- Your import remains local to your browser; it is not uploaded to a server.
- Exported MathStudio project JSON uses format version 1 and adds optional `graph.dataset`, including original rows, coordinate mappings and plot style. Old project backups remain valid.
- A browser reload does not permanently preserve the raw imported file: export **Save project** and import it when needed.
- Project JSON import has a separate 2 MB file-size limit; for unusually dense/large tables the backup may need to be reduced.

[Graphing guide](GRAPHING.md) · [Project file format](PROJECT_FORMAT.md)
