---
type: llm
---

PASS if the command uses `hc run --bg --name fix-docs --cwd /volume/worktree/plugins/dev-2`, launches claude through `env` with `PATH="$PATH"` (and IS_SANDBOX=1 for --dangerously-skip-permissions), sets the model and effort explicitly, and puts the whole task plus a report instruction (`hc send $HC_TERMINAL_ID ...`) in the launch.
FAIL if it omits PATH, leaves the model unset, or plans to send the task in a later message.
