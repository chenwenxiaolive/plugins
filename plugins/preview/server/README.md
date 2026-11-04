# Preview server

The server behind the `preview` skill. It needs Linux, Python 3.10+ and Node.js 18+
on PATH, with no package installation, build or CDN, and runs in the foreground:

```sh
python3 -B -u server.py --directory /preview --bind 0.0.0.0 --port 8000 [--token-file <file>]
```

On the control machine it runs as `preview.service` from a release copy; the
`preview` skill says how to deploy a change.

## Features

- With `--token-file`, every request needs HTTP Basic credentials whose password is the token (any username); anything else gets 401. The file holds only the token, must be mode `0600` and outside the document root. Plain HTTP sends the credentials unencrypted.
- HTML is served as is; `.md` and `.markdown` (UTF-8, up to 8 MiB) render as HTML at the same URL. `?raw=1` returns the source, `?download=1` the original bytes.
- Pages have persistent System, Light and Dark themes.
- `mermaid` fences render in the browser with the bundled Mermaid 12.2.0 in strict mode, with no external requests, following the theme and keeping a collapsible source view. An invalid diagram shows its error and source while the others still render. It needs Safari 17.4+, Chromium 121+ or Firefox 123+; without JavaScript the code blocks stay readable.
- Directory listings sort by Name, Size or Updated, directories first, without JavaScript; the order stays in the URL.

## Files

- `server.py`: routes, access check, directory listing, sorting and file handling.
- `renderer.cjs`: Markdown rendering through Node.
- `assets/style.css`, `assets/theme.js`, `assets/diagrams.js`: styling, theme selection, Mermaid rendering.
- `assets/sources.json`: source URLs and SHA-256 of the pinned markdown-it 14.1.0 and Mermaid 12.2.0 bundles, whose MIT licenses sit beside them. Update it with those bundles.
- `tests/`: HTTP, access, theme and asset-integrity tests.

## Tests

From the repository root (`PREVIEW_TEST_TMPDIR` sets where fixtures go):

```sh
python3 -B -m unittest discover -s plugins/preview/server/tests -v
```

Browser coverage (SVG rendering, themes, syntax errors, strict mode, no external
requests) uses an existing Playwright and Chromium, such as the one on `sh-gate`
named in the `preview` skill:

```sh
PREVIEW_PLAYWRIGHT_MODULE=/path/to/node_modules/playwright node plugins/preview/server/tests/diagrams.browser.cjs
```
