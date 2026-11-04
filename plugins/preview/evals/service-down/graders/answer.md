---
type: llm
---

The run has no shell, so judge the advice.
PASS if it says to check the `preview` systemd service (`systemctl status preview` or `journalctl -u preview`), restart it with `systemctl restart preview`, and check a page again afterwards. Mentioning `scripts/preview.py` or a manual server only to rule it out is fine.
FAIL if it recommends starting a server by hand (such as `scripts/preview.py` or `python -m http.server`) or changing the service's address, port or token.
