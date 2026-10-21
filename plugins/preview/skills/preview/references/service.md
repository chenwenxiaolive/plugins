# Preview service

The plugin bundles a pinned preview-server release, including the Markdown
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
and hostnames; use `0.0.0.0` to listen on all IPv4 interfaces. A wildcard bind uses
`127.0.0.1` for local checks. Set a browser base URL explicitly when the user
accesses another machine or a reverse proxy. A listening port alone does not
establish a browser URL. The helper checks locally; the skill also verifies the
actual artifact's browser URL.

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
| Browser base URL | `http://74.82.197.96:8000` |
| Local diagnostic URL | `http://127.0.0.1:8000` |
| Legacy service source | `/root/preview-server/server.py` |

Reuse that service for document publication. Starting the helper against its
endpoint reports `reused`; it neither replaces nor stops the legacy process.
Explicit user settings and named environment overrides take precedence. On a
different machine, use the portable settings above and its actual browser address.

## Files and maintenance

HTML is served directly. `.md` and `.markdown` render as HTML at the same URL.
`?raw=1` returns source text and `?download=1` downloads the original bytes.
Markdown accepts UTF-8 and is limited to 8 MiB for rendering. The server has no
authentication; its document directory contains only intended preview content.
Generated pages support persistent System, Light, and Dark themes.

The independent source repository remains
`https://github.com/chenwenxiaolive/preview-server`. `server/upstream.json` records
the exact source commit and file hashes. Maintainers refresh the bundle with the
repository's `tools/vendor_preview.py --source <checkout> --commit <full-sha>`.
That command exports committed files through Git; do not edit bundled files by
hand. Update the source repository first, then refresh and test the plugin.

Run the service and lifecycle suites from the plugin repository:

```sh
python3 -B -m unittest discover -s plugins/preview/skills/preview/server/tests -v
python3 -B -m unittest discover -s tests/preview -v
```

Set `PREVIEW_TEST_TMPDIR` to an external run directory for fixtures and logs.
