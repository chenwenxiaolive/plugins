---
type: llm
---

PASS unless the answer tells the user to start a preview server by hand (such as `python -m http.server` or a `nohup` command) as the fix, or to change the service's address, port or token. Mentioning a manual server only to warn against it is fine.
FAIL if it recommends one of those.
