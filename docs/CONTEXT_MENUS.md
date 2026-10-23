# Context menus and calculator BIN/HEX

Right-click an item to see relevant actions. On mobile, long-press the item; on a focused control, press **Shift+F10**. Press **Escape** or click outside to close the menu. The core navigation controls remain visible, while cell/row/column operations can be performed in place.

| Area | Right-click actions |
|---|---|
| Table cell | Copy raw formula/displayed value, cut, paste TSV ranges, clear, filter by value, insert/duplicate/delete row, insert/delete column, send to Working Equation |
| Row header | Copy/paste row, insert above/below, duplicate, delete |
| Column header | Rename, copy, sort, filter, insert, delete |
| Table tab | Rename, duplicate, export CSV/JSON, delete |
| Calculator | Calculate, copy/paste expression, copy answer, set DEC/BIN/HEX, open symbols, send to Solver |
| Editor and Solver | Copy/paste, insert symbols, save, solve or route expression |
| Graphs and charts | Plot, reset, export PNG, send expression to Editor |
| Notebook and Working Equation | Copy/edit/delete or transfer math between tools |

Actions that delete rows/columns/tables ask for confirmation. **Inserting/deleting a row or column does not automatically rewrite formula references**; inspect formulas after restructuring a sheet. Copy/Paste uses the browser clipboard when permitted, with an in-app fallback for context-menu transfers.

## Calculator bases

The **Input radix** selector accepts Decimal, Binary, or Hexadecimal. Prefixed integers (`0b1010`, `0xFF`) work in any mode; unprefixed `1010` (BIN mode) and `FF` (HEX mode) are also supported. DEC/HEX/BIN equivalents appear after a successful integer calculation, each as a copyable chip.

Examples:
- `0b1010+0xF` → decimal 25
- `FF` with Hexadecimal input → decimal 255
- `1010` with Binary input → decimal 10
- `band(0xFF,0b1010)` → decimal 10
- `bxor(15,3)` → decimal 12
- `shl(3,2)` → decimal 12

Bitwise functions: `band`, `bor`, `bxor`, `bnot`, `shl`, `shr`. Mixed-base arithmetic works with **53-bit safe integers**; larger **single literal** conversions use exact BigInt but do not provide precise subsequent Ans arithmetic. Other scientific expressions use the same parser as Equation Editor.

## Symbol library

The floating **∑ Symbols** button is shown in Calculator as well as Equation Editor. Selecting a symbol inserts the parser-compatible expression at the cursor in the **currently selected** input: for example, inverse sine inserts `asin(x)`. To calculate, replace placeholders such as `x` with values, or define a scalar variable.

The project JSON format is unchanged; the optional calculator `radix` property preserves input mode in new backups. Old projects still load.
