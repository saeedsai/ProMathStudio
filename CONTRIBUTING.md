# Contributing

Thanks for improving ProMathStudio.

## Before changing code

Read [Development](docs/DEVELOPMENT.md), [Architecture](docs/ARCHITECTURE.md), [Testing](docs/TESTING.md), and [Security](SECURITY.md). File a clear issue describing the feature/bug and mathematical input/output.

## Proposed workflow

1. Work from the latest `main` commit on a feature branch.
2. Keep current user-visible behavior and version-1 project backups compatible.
3. Add reproducible tests for algebra, calculator, graph or editor changes.
4. Update documentation and `CHANGELOG.md`.
5. Run structural and Chromium smoke tests; run advanced SymPy tests manually online when affected.
6. Open a pull request with summary, tests, screenshots for UI work and limitations.

Do not push secrets, private math notebooks, generated binary exports or screenshots containing sensitive data.

## Licensing note

The repository does not currently include an open-source license. Public visibility is not permission to redistribute or sublicense its code. The repository owner should choose and publish a license before accepting outside contributions intended for redistribution.
