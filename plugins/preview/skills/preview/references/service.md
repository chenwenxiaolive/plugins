# Preview service on this machine

| Setting | Value |
| --- | --- |
| Document root | `/preview` |
| Browser base URL | `http://74.82.197.96:8000` (direct; no SSH tunnel) |
| Local check URL | `http://127.0.0.1:8000` |
| Server bind | `0.0.0.0:8000` |
| State directory | `/volume/tmp/preview-ssh-20261101-q6t3azd2` |
| Access token file | `token` in the state directory (mode `0600`) |

Direct access is the owner's standing choice. Keep `0.0.0.0:8000` across restarts,
and don't re-enable the retired `preview-local-only.service` unless the owner asks.

## Start, check, restart

Use the helper and settings saved in the state directory's `deployment.json`
(`helper`, `directory`, `bind`, `port`, `base_url`, `token_file`), so the deployed
release stays in place:

```sh
state=/volume/tmp/preview-ssh-20261101-q6t3azd2
python3 -B <helper> status|start|stop --state-dir "$state" \
  --directory <directory> --bind <bind> --port <port> --base-url <base_url> \
  --token-file <token_file>
```

Pages need the token: a browser asks for it as the password (any username).
Never print or repeat it; to check a page, let `curl` read the credentials from
stdin so they stay out of command arguments:

```sh
printf 'user = "preview:%s"\n' "$(cat <token_file>)" | curl -K - --fail -sS --max-time 10 <url>
```

- `status` reports `running`, `reused` or `stopped`, and exits nonzero when the service is stopped or unhealthy.
- `start` reuses a service only after a probe shows it serves this root, and refuses a port held by anything else.
- `stop` stops only the process this helper started.
- To change settings, stop the service with the settings in `service.json`, start it with the new ones, and record them in `deployment.json` so later restarts keep them.
- The service runs a release copy (`release` in `deployment.json`), not this checkout; [server/README.md](../server/README.md#deploying-a-change) says how to deploy a server change.

The server serves HTML as is and renders `.md` as HTML at the same URL; `?raw=1`
returns the source and `?download=1` the original bytes. Credentials travel over
plain HTTP, so the root still holds only content meant for viewing. The server's source, features
and tests are described in [server/README.md](../server/README.md).
