# Security policy

## Scope

The project is a static, browser-based math editor. It uses localStorage and user-imported JSON projects. Optional advanced SymPy runs in a browser Web Worker after downloading Pyodide/SymPy from a third-party CDN.

## Responsible disclosure

For security issues, contact the repository owner privately using GitHub's repository security/advisory options where enabled. **Do not publish exploitable payloads or private project files in a public issue.** Normal bug reports can use GitHub Issues.

## Security expectations

- Do not introduce arbitrary JavaScript `eval` or unrestricted Python code execution.
- Validate project file size/structure before modifying persistent local state.
- Restrict AST node types and budget for complex symbolic expressions.
- Treat third-party CDN resources as a supply-chain trust boundary.
- Escape/sanitize any user-controlled output into DOM, clipboard HTML and document XML.
- Do not store secrets or personal mathematical projects in a public GitHub repository.

## Supported versions

The default branch is the maintained version; no separately maintained released version series has been declared.

## Privacy

No backend accounts or project sync are implemented. Browser storage persists on the user device. Exported project files contain your mathematical work; handle them as potentially sensitive.
