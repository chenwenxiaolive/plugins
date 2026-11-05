---
type: llm
---

PASS if the command uses `hc run --bg --name fix-docs --cwd /volume/worktree/plugins/dev-2`, launches claude through `env` with `PATH="$PATH"` (and IS_SANDBOX=1 for --dangerously-skip-permissions), sets the model and effort explicitly, and puts the whole task in the launch. For the result, either the launch tells the worker to run `hc send $HC_TERMINAL_ID ...` when done or, outside an hc terminal, the result is collected with `hc wait` and `hc read`.
FAIL if it omits PATH, leaves the model unset, or plans to send the task in a later message.
