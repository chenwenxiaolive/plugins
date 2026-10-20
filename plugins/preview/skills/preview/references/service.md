# Personal preview service

These defaults describe the existing control machine. On another machine,
resolve its service mapping before publishing.

| Setting | Current value |
| --- | --- |
| Filesystem root | `/preview` |
| Browser base URL | `http://74.82.197.96:8000` |
| Local diagnostic base URL | `http://127.0.0.1:8000` |
| Service source | `/root/preview-server/server.py` |

An explicit user-provided root or URL takes precedence. When set,
`PREVIEW_ROOT` and `PREVIEW_BASE_URL` override the corresponding defaults.
Read only these named variables; do not dump the environment. The plugin does
not set them, and the server's actual document root must match the chosen root.

The service serves HTML directly and renders `.md` and `.markdown` files into
HTML at the same URL. Append `?raw=1` for the original text or `?download=1`
for an attachment. Markdown rendering accepts UTF-8 and is limited to 8 MiB;
larger files need a download link or a deliberately smaller preview.

For example, `/preview/reports/result.md` maps to
`http://74.82.197.96:8000/reports/result.md`.
The loopback address is for local diagnosis, not a browser link for the user.

If the browser URL cannot be checked but the loopback URL works, report that
distinction. Reuse the current service without changing its process or network
configuration.
