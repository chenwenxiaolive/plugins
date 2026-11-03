# Preview service on this machine

| Setting | Value |
| --- | --- |
| Document root | `/preview` |
| Browser base URL | `http://74.82.197.96:8000` (direct; no SSH tunnel) |
| Local check URL | `http://127.0.0.1:8000` |
| Server bind | `0.0.0.0:8000` |
| State directory | `/volume/tmp/preview-ssh-20261101-q6t3azd2` |

Direct access is the owner's standing choice. Keep `0.0.0.0:8000` across restarts,
and don't re-enable the retired `preview-local-only.service` unless the owner asks.

## Start, check, restart

Use the helper and settings saved in the state directory's `deployment.json`
(`helper`, `directory`, `bind`, `port`, `base_url`), so the deployed release stays
in place:

```sh
state=/volume/tmp/preview-ssh-20261101-q6t3azd2
python3 -B <helper> status|start|stop --state-dir "$state" \
  --directory <directory> --bind <bind> --port <port> --base-url <base_url>
```

- `status` reports `running`, `reused` or `stopped`, and exits nonzero when the service is stopped or unhealthy.
- `start` reuses a service only after a probe shows it serves this root, and refuses a port held by anything else.
- `stop` stops only the process this helper started.
- To change settings, stop the service with the settings in `service.json`, then start it with the new ones.

The server serves HTML as is and renders `.md` as HTML at the same URL; `?raw=1`
returns the source and `?download=1` the original bytes. It has no authentication,
so the root holds only content meant for viewing. The server's source, features
and tests are described in [server/README.md](../server/README.md).
