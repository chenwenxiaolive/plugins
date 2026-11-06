---
type: llm
---

PASS if it checks the real working directories of the running claude and codex processes (for example `readlink /proc/<pid>/cwd` for the PIDs from `pgrep -x claude` and `pgrep -x codex`) rather than trusting the cwd that `hc ls` or `hc get` shows.
FAIL if it relies only on the cwd that hc lists.
