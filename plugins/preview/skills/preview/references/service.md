# Preview service

The plugin contains the preview service source, including the Markdown
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
the document root and the plugin directory. The helper supports IPv4 addresses
and hostnames. Keep the loopback bind for local viewing or SSH forwarding.
`0.0.0.0` exposes the service on all IPv4 interfaces and requires an explicit
request for network access. Set a browser base URL explicitly when the user's
forwarded address differs from the server's local endpoint. A listening port
alone does not establish a browser URL. The helper checks locally; for SSH
access, verify artifacts locally and make the tunnel prerequisite clear.

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
stop an externally started service. Use the same state directory across plugin
upgrades; stop uses the saved process record even if the plugin path changed.
To change a managed service's root, bind, or port, stop it with its original
configuration and start it with the new settings. Stop before removing the old
plugin version's files. This helper starts a detached process; it does not install
a system service or arrange startup after reboot.

## Existing control-machine service

These are mappings for the existing control machine only, not portable defaults:

| Setting | Existing value |
| --- | --- |
| Filesystem root | `/preview` |
| Server bind | `127.0.0.1:8000` |
| Browser base URL | `http://127.0.0.1:8000` through an SSH local forward |
| Local diagnostic URL | `http://127.0.0.1:8000` |
| Remote access | SSH only; no public HTTP listener |

Reuse the managed service for document publication. The active state directory
and deployed helper path are local deployment settings: obtain them from the
current machine instructions and ownership record. Pass the existing state
directory explicitly and preserve the deployed release when changing only
service settings. Do not use the retired public port-8000 URL or reopen public
access unless explicitly requested. On a different machine, use its explicit
settings or the portable defaults above.

Run this command on the user's computer and keep the terminal open:

```sh
ssh -NT \
  -L 127.0.0.1:8000:127.0.0.1:8000 \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  root@74.82.197.96
```

Use the user's usual SSH alias or login account if different. Then open
`http://127.0.0.1:8000/`; artifact paths remain relative to that base. If local
port 8000 is occupied, choose another client-side port and use that port in
browser links while keeping the server endpoint at `127.0.0.1:8000`.
The agent's local HTTP check verifies the server, not the tunnel on the user's
computer. Do not claim the client tunnel is connected without checking it there.

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

The plugin repository is the source of truth for the service. Edit the files
under `plugins/preview/skills/preview/server/` directly and release changes with
the plugin; no separate service checkout or import command is needed.

- `server.py`: HTTP routes, directory listing, sorting, and file handling.
- `renderer.cjs`: Markdown rendering through the existing Node executable.
- `assets/style.css` and `assets/theme.js`: styling and saved theme selection.
- `assets/diagrams.js`: browser rendering and theme updates for Mermaid fences.
- `tests/`: HTTP integration and theme behavior tests.

The third-party markdown-it renderer is pinned to 14.1.0 and Mermaid to 12.2.0.
Their source URLs and SHA-256 hashes are in `server/assets/sources.json`, with
their MIT licenses alongside the bundles. Update these records when updating those
third-party assets. They do not pin the plugin's own service code.

Restart a managed service with the helper after changing service code or the
renderer. Document and stylesheet edits appear on refresh. Keep launch scripts,
logs, PIDs, and run records outside the checkout.

Run the service and lifecycle suites from the plugin repository:

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
