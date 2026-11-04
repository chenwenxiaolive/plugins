---
name: preview
description: Create or update standalone HTML and Markdown artifacts in the local /preview service, verify them, and return links at its configured browser URL. Use for requested document previews, reports, existing /preview artifacts, or managing the bundled service. Keep tracked repository documentation in its established location.
---

# Preview

Write the page under `/preview` and return its link: `http://74.82.197.96:8000/` plus
the URL-encoded path below `/preview`. The server renders `.md` as HTML at the same
URL (`?raw=1` gives the source, `?download=1` the bytes), so don't make HTML copies.
Publish only content meant for the user, and leave tracked repository docs where
they are; copy one in as a snapshot to preview it.

- Every request needs the access token as the HTTP Basic password, with any username; the browser asks once. It's in `/volume/tmp/preview-ssh-20261101-q6t3azd2/token`. Never print or repeat it. To check a page, keep it out of command arguments: `printf 'user = "preview:%s"\n' "$(cat <token file>)" | curl -K - --fail -sS --max-time 10 <url>`.
- When layout matters (charts, wide tables, phone width, dark mode), screenshot the page at desktop and phone width, in light and dark, and fix what you see. Use the headless Chromium on `sh-gate` in `/volume/tmp/preview-browser-20261104-XrJSjB`: `source env.sh` there, and its `README.txt` says how to rebuild it.
- The server runs as `preview.service` (systemd, `Restart=always`, enabled at boot, bound to `0.0.0.0:8000` by the owner's choice). If it's down, `systemctl restart preview`; its settings are in `systemctl cat preview`, and its log is `journalctl -u preview`. Don't start a second server, and don't re-enable the retired `preview-local-only.service`.
- The service runs a release copy of the server (source in this repository's `plugins/preview/server/`) from `~/.local/share/preview/releases/<commit>/`. To deploy a merged change, `git archive <commit> plugins/preview/server | tar -x -C <release> --strip-components=3`, point the unit's `ExecStart` at the new `server.py`, then `systemctl daemon-reload && systemctl restart preview` and check a page.
