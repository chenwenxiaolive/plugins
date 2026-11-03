# Preview service

The skill contains the preview service source, including the Markdown
renderer and theme assets. It requires Linux, Python 3.10+ and Node.js 18+ on PATH;
no package installation, build, or browser CDN is required.

## Configuration and commands

Run `python3 -B scripts/preview.py` relative to this skill directory, or use the
script's absolute path. Commands are `start`, `status`, and `stop`. Options follow
the command. Explicit flags override the corresponding environment variables.

| Flag | Environment variable | Default |
| --- | --- | --- |
| `--directory` | `PREVIEW_ROOT` | `/preview` |
| `--bind` | `PREVIEW_BIND` | `127.0.0.1` |
| `--port` | `PREVIEW_PORT` | `8000` |
| `--base-url` | `PREVIEW_BASE_URL` | Local HTTP URL for the bind address and port |
| `--state-dir` | `PREVIEW_STATE_DIR` | `~/.local/state/preview/<hostname>/<port>` |

The document directory must already exist. State and logs must be outside both
the document root and the skill directory. The helper supports IPv4 addresses
and hostnames. Use loopback for local viewing or SSH forwarding; preserve an
existing deployment's explicitly authorized network access. `0.0.0.0` exposes the
service on all IPv4 interfaces. Set a browser base URL explicitly when the browser
address differs from the server's local endpoint. A listening port
alone does not establish a browser URL. The helper checks locally; for SSH
access, verify artifacts locally and make the tunnel prerequisite clear.

Portable loopback example; use the saved settings for an existing deployment:

```sh
python3 -B scripts/preview.py start --directory /preview
python3 -B scripts/preview.py status
python3 -B scripts/preview.py stop
```

`start` checks the configured endpoint before launching. It reuses a service only
when a temporary Markdown probe proves that the endpoint renders files from the
selected document root. The probe is removed afterwards. An occupied port with
a different root or incompatible service is an error. Reuse never adopts the
other service's PID. `status` reports `running`, `reused`, or `stopped`; stopped
and unhealthy services return a nonzero exit code. Output is JSON on success;
errors are English messages on stderr.

`stop` stops only the process recorded by this helper, verifying its host, boot,
PID identity, and command before signaling through a Linux pidfd. It does not
stop an externally started service. Use the same state directory across skill
upgrades; stop uses the saved process record even if the skill path changed.
To change a managed service's root, bind, or port, stop it with its original
configuration and start it with the new settings. Stop it before removing an old
copy of the skill. This helper starts a detached process; it does not install
a system service or arrange startup after reboot.

## Existing control-machine service

These are mappings for the existing control machine only, not portable defaults:

| Setting | Existing value |
| --- | --- |
| Filesystem root | `/preview` |
| Server bind | `0.0.0.0:8000` |
| Browser base URL | `http://74.82.197.96:8000` |
| Local diagnostic URL | `http://127.0.0.1:8000` |
| Remote access | Direct HTTP; no SSH tunnel required |

Reuse the managed service for document publication. The active state directory
and deployed helper path are local deployment settings: obtain them from the
current machine instructions and the state directory's `deployment.json`.
For every start, status check, or restart, use that saved helper and explicitly
pass its `directory`, `bind`, `port`, and `base_url` values as `--directory`,
`--bind`, `--port`, and `--base-url`, together with the existing `--state-dir`.
Preserve the deployed release when changing only service settings. If a running
process differs from the saved configuration, stop it with the actual settings
in `service.json`, then start with the intended settings from `deployment.json`.

Direct access is the owner's standing choice for this machine. Keep
`0.0.0.0:8000` across starts and restarts; do not replace it with the helper's
loopback default or re-enable the retired `preview-local-only.service` unless
the owner explicitly changes that choice. Open `http://74.82.197.96:8000/`
directly and construct artifact links relative to that base. A local diagnostic
check does not establish reachability from the user's computer. On a different
machine, use its explicit settings or the portable defaults above.

## Files and maintenance

HTML is served directly. `.md` and `.markdown` render as HTML at the same URL.
`?raw=1` returns source text and `?download=1` downloads the original bytes.
Markdown accepts UTF-8 and is limited to 8 MiB for rendering. The server has no
authentication; its document directory contains only intended preview content.
Generated pages support persistent System, Light, and Dark themes.
Markdown fences labeled `mermaid` render as diagrams in the browser using the
bundled Mermaid 12.2.0 library. Diagrams follow the page's theme and include a
collapsible source view. Invalid diagrams show an error and keep their source
visible; other diagrams still render. Without JavaScript, the original code
blocks remain readable. Mermaid uses its strict security mode and makes no
external rendering requests. The bundle requires a modern browser (Safari 17.4+,
Chromium 121+, or Firefox 123+); server-side Markdown still needs only Node.js 18+.
Directory headings sort by Name, Size, or Updated, toggling ascending and
descending order. Directories remain first; sizes use bytes and modification
times use their full precision. Sorting works without JavaScript and is retained
in the page URL when refreshed.

This repository is the source of truth for the service. Edit the files
under `plugins/preview/skills/preview/server/` directly and release changes with
the skill; no separate service checkout or import command is needed.

- `server.py`: HTTP routes, directory listing, sorting, and file handling.
- `renderer.cjs`: Markdown rendering through the existing Node executable.
- `assets/style.css` and `assets/theme.js`: styling and saved theme selection.
- `assets/diagrams.js`: browser rendering and theme updates for Mermaid fences.
- `tests/`: HTTP integration and theme behavior tests.

The third-party markdown-it renderer is pinned to 14.1.0 and Mermaid to 12.2.0.
Their source URLs and SHA-256 hashes are in `server/assets/sources.json`, with
their MIT licenses alongside the bundles. Update these records when updating those
third-party assets. They do not pin the skill's own service code.

Restart a managed service with the helper after changing service code or the
renderer. Document and stylesheet edits appear on refresh. Keep launch scripts,
logs, PIDs, and run records outside the checkout.

Run the service and lifecycle suites from the repository root:

```sh
python3 -B -m unittest discover -s plugins/preview/skills/preview/server/tests -v
python3 -B -m unittest discover -s tests/preview -v
```

Set `PREVIEW_TEST_TMPDIR` to an external run directory for fixtures and logs.
For browser coverage, use an existing Playwright installation and Chromium:

```sh
PREVIEW_PLAYWRIGHT_MODULE=/path/to/node_modules/playwright \
  node plugins/preview/skills/preview/server/tests/diagrams.browser.cjs
```

Set `PLAYWRIGHT_BROWSERS_PATH` when the browser is installed outside its default
cache. The browser check covers real SVG rendering, theme changes, syntax errors,
source/download preservation, strict-mode handling, and operation without external
requests. Screenshots and server logs stay in `PREVIEW_TEST_TMPDIR`.
