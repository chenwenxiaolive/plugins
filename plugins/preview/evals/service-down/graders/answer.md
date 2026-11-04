---
type: llm
---

PASS if the answer checks and restarts the `preview` systemd service (for example `systemctl status preview`, `systemctl restart preview`, `journalctl -u preview`) and checks a page again afterwards, without starting a server by hand or changing the service's address, port or token.
FAIL if it starts a server manually (such as `scripts/preview.py` or `python -m http.server`), or changes the service's settings.
