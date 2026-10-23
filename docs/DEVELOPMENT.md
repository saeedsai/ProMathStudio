# Developer guide

## Repository organization

```text
index.html                 # Entire working app (entry point; no build required)
README.md                  # Overview and navigation
docs/                     # User, developer, syntax, graph, SymPy and deployment guides
tests/test_static.py       # Dependency-free Python unittest source assertions
tests/smoke_browser.py     # Playwright Chromium end-to-end smoke coverage
requirements-dev.txt       # Browser test dependency
.github/workflows/         # Test workflow and Pages deployment workflow
.nojekyll                  # Prevent Jekyll processing on GitHub Pages
CONTRIBUTING.md            # Contribution workflow
SECURITY.md                # Security disclosure instructions
CHANGELOG.md               # Release notes
```

No JavaScript packages are required at runtime. The single HTML file contains multiple inline script modules and a Python source block embedded for Pyodide.

## Local development

```sh
git clone https://github.com/saeedsai/ProMathStudio.git
cd ProMathStudio
python -m http.server 8000
# visit http://localhost:8000
```

Opening `index.html` directly is also possible. A local server makes clipboard/security-origin behavior and refresh tests more predictable.

## Validation before pushing

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/smoke_browser.py
```

Smoke tests use Playwright's DOM content initialization and avoid network-dependent SymPy loading. The first SymPy CDN load must additionally be tested manually with network access; test mathematical outputs independently.

## Working on the single-file source

- Keep routing and notebook compatibility, especially the `mathstudio-project` JSON format v1.
- Edit markup, CSS and scripts in `index.html`; avoid breaking script IDs used by the Web Worker.
- Add at least one regression check for changes to parsing, root calculations, graphing, Word export or transfer behavior.
- Test unambiguous operator precedence, complex principal roots, domain exclusions and different browser viewport sizes.
- Preserve error reporting when clipboard, localStorage or CDN access is unavailable.

## Pull requests

Make changes on a feature branch, run checks, include before/after screenshots if UI changed, update relevant docs and `CHANGELOG.md`. Do not force-push shared branches. No open-source reuse license has been chosen; see `CONTRIBUTING.md`.

[Architecture](ARCHITECTURE.md) · [Testing](TESTING.md)
