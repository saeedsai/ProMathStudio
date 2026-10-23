# Exports, code and Word interoperability

## Equation editor

| Control | Output |
|---|---|
| **Copy LaTeX** | LaTeX text for currently previewed expression |
| **Copy for Word** | Rich HTML/MathML clipboard when browser permits |
| **Copy image** | PNG image on clipboard when supported |
| **Word .docx** | Download with editable Word Office Math, when representable |
| **Export .tex** | LaTeX notebook document |
| **Notebook .docx** | Saved equations as Word objects |
| **Copy Python** | Python/SymPy code snippet from parsed equation |

## Symbolic solver

Results may be copied as LaTeX, saved to notebook, exported to Word or routed into another workspace. The corresponding Python/SymPy operation is shown in an expandable panel. Exact CAS results should be checked when transferred to a numeric-only calculator.

## Graph

**Export PNG** downloads the currently rendered 2D or 3D canvas. PNG is a static picture; it is not a vector plot and cannot be edited as equations.

## Word specifics

Browser clipboard APIs and native Word MathML support vary across Chrome/Edge/Firefox and Word versions. If pasting does not preserve editable math, use **Word .docx** instead. Editability applies to the Office Math equations in exported files, not to screenshots.

## Security

Equation exports can be opened in external programs. Generated Python is for review and execution in a trusted Python environment; the app does **not** run pasted arbitrary Python code. Clipboard operations may require HTTPS/secure context and a user gesture.

[User guide](USER_GUIDE.md)
