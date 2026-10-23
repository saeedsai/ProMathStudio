# GitHub Pages deployment

## Publish the app

ProMathStudio is a static HTML site. The application entry point is root `index.html`, so no compilation is required.

### Option A — GitHub Actions deployment (preferred if workflows are permitted)

1. Go to the repository's **Settings → Pages**.
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Push to `main` or run the **Deploy GitHub Pages** workflow manually.
4. Wait for **Quality checks** and deployment jobs; do not assume success from a commit alone.
5. Once published, verify https://saeedsai.github.io/ProMathStudio/ on desktop and mobile.

The workflow deploys the static root after automated tests. It needs repository Actions and Pages permissions. Pages settings are a GitHub repository configuration and cannot be enabled merely by committing a workflow file.

### Option B — Publish directly from a branch

1. In **Settings → Pages**, choose **Deploy from a branch**.
2. Select `main` and `/ (root)`.
3. Save; check Actions/Pages for its actual status.

Use either option A or B, not competing deployment paths.

## Verify after deployment

- The URL returns the equation editor and all four workspace tabs.
- The calculator evaluates `5!+3^2` to 129.
- Offline CAS expands `(x-1)^2`.
- 2D and 3D canvases appear.
- SymPy download succeeds in a browser with network access.
- JSON backups and PNG/DOCX downloads work on supported platforms.

## Limitations

GitHub Pages serves HTTPS static assets; it does not execute server-side Python. SymPy runs inside a browser Web Worker and downloads Pyodide packages via CDN on first use. GitHub Pages does not sync notebook data across devices. If your repository has deployment protection or unavailable Pages settings, a workflow may fail until configured.

## Troubleshooting

A 404 usually means Pages has not finished publishing or Source is set incorrectly. A workflow failure must be diagnosed from **Actions** logs, not fixed by bypassing checks. For the full checklist see [Troubleshooting](TROUBLESHOOTING.md).
