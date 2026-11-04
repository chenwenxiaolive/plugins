# Preview service on this machine

| Setting | Value |
| --- | --- |
| Runs as | `preview.service` (systemd system unit, enabled at boot, `Restart=always`) |
| Document root | `/preview` |
| Browser base URL | `http://74.82.197.96:8000` (direct; no SSH tunnel) |
| Local check URL | `http://127.0.0.1:8000` |
| Server bind | `0.0.0.0:8000` |
| Access token file | `/volume/tmp/preview-ssh-20261101-q6t3azd2/token` (mode `0600`) |
| Headless browser | Playwright with headless Chromium in `sh-gate`'s system `python3` (none on this machine) |

The disabled `preview-local-only.service` is retired; leave it off.

## Check and restart

The unit runs the deployed server release in the foreground, outside any agent
session; a server started from an agent's terminal dies with that terminal. Don't
start one with `scripts/preview.py` here.

```sh
systemctl status preview          # running? recent log lines
systemctl restart preview         # restart with the unit's settings
journalctl -u preview -n 50       # request log and errors
systemctl cat preview             # the settings: release path, root, bind, port, token file
```

To change a setting or deploy a new release ([server/README.md](../server/README.md#deploying-a-change)),
edit `ExecStart` in `/etc/systemd/system/preview.service`, then
`systemctl daemon-reload && systemctl restart preview`, and check a page.

Pages need the token: a browser asks for it as the password (any username).
To check a page, let `curl` read the credentials from stdin, which keeps the token
out of command arguments:

```sh
printf 'user = "preview:%s"\n' "$(cat <token_file>)" | curl -K - --fail -sS --max-time 10 <url>
```

To screenshot a page, run Playwright on `sh-gate` against the browser URL, which it
reaches directly: give the browser context the token as HTTP credentials read from
ssh stdin, and keep the script and images in a new `/volume/tmp` run directory there.

The server serves HTML as is and renders `.md` as HTML at the same URL; `?raw=1`
returns the source and `?download=1` the original bytes. Credentials travel over
plain HTTP, so the root still holds only content meant for viewing. The server's
source, features and tests are described in [server/README.md](../server/README.md).
