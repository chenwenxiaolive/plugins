# Preview server

The preview service ships with the skill and is maintained here; there is no
separate service checkout. It needs Linux, Python 3.10+ and Node.js 18+ on PATH,
with no package installation, build or CDN.

## Helper

`scripts/preview.py start|status|stop` manages one detached server; it installs no
system service and arranges no restart after reboot. Flags override environment
variables:

| Flag | Environment variable | Default |
| --- | --- | --- |
| `--directory` | `PREVIEW_ROOT` | `/preview` (must exist) |
| `--bind` | `PREVIEW_BIND` | `127.0.0.1` |
| `--port` | `PREVIEW_PORT` | `8000` |
| `--base-url` | `PREVIEW_BASE_URL` | Local URL for the bind address and port |
| `--state-dir` | `PREVIEW_STATE_DIR` | `~/.local/state/preview/<hostname>/<port>` |
| `--token-file` | `PREVIEW_TOKEN_FILE` | none: no access control |

State and logs live outside the document root and the skill. `start` reuses a
running server only when a temporary Markdown probe shows it serves the selected
root, and never adopts another server's PID. `stop` checks the recorded host,
boot, PID and command before signaling through a pidfd, so it never stops a server
it didn't start; keep the same state directory across skill upgrades. Output is
JSON on success and an English message on stderr on failure.

## Features

- With a token file, every request needs HTTP Basic credentials whose password is the token (any username); the browser asks once. The file holds only the token, must be mode `0600` and outside the document root; commands pass its path, never the token. Plain HTTP sends the credentials unencrypted.
- HTML is served as is; `.md` and `.markdown` (UTF-8, up to 8 MiB) render as HTML at the same URL. `?raw=1` returns the source, `?download=1` the original bytes.
- Pages have persistent System, Light and Dark themes.
- `mermaid` fences render in the browser with the bundled Mermaid 12.2.0 in strict mode, with no external requests, following the theme and keeping a collapsible source view. An invalid diagram shows its error and source while the others still render. It needs Safari 17.4+, Chromium 121+ or Firefox 123+; without JavaScript the code blocks stay readable.
- Directory listings sort by Name, Size or Updated, directories first, without JavaScript; the order stays in the URL.

## Files

- `server.py`: routes, directory listing, sorting and file handling.
- `renderer.cjs`: Markdown rendering through Node.
- `assets/style.css`, `assets/theme.js`, `assets/diagrams.js`: styling, theme selection, Mermaid rendering.
- `assets/sources.json`: source URLs and SHA-256 of the pinned markdown-it 14.1.0 and Mermaid 12.2.0 bundles, whose MIT licenses sit beside them. Update it with those bundles.
- `tests/`: HTTP integration and theme tests.

## Deploying a change

A deployed service runs a release copy of the skill, so editing this checkout
changes nothing there. After merging a server change, create the copy:

```sh
release=~/.local/share/preview/releases/<commit>
mkdir -p "$release" && git archive <commit> plugins/preview/skills | tar -x -C "$release" --strip-components=2
```

Then point the running service at `$release/skills/preview/server/server.py` (on
the control machine, the `preview.service` unit; see
[service.md](../references/service.md)), restart it and check a page. Keep the old
release until the new one is verified.

## Tests

From the repository root, with fixtures and logs in an external directory
(`PREVIEW_TEST_TMPDIR`):

```sh
python3 -B -m unittest discover -s plugins/preview/skills/preview/server/tests -v
python3 -B -m unittest discover -s tests/preview -v
```

Browser coverage (SVG rendering, themes, syntax errors, strict mode, no external
requests) uses an existing Playwright and Chromium; set `PLAYWRIGHT_BROWSERS_PATH`
if the browser is outside its default cache:

```sh
PREVIEW_PLAYWRIGHT_MODULE=/path/to/node_modules/playwright \
  node plugins/preview/skills/preview/server/tests/diagrams.browser.cjs
```
