---
type: llm
---

PASS if the command uses `hc run --bg --name fix-docs --cwd /volume/worktree/plugins/issue-docs`, launches interactive claude through `env` with `PATH="$PATH"` and IS_SANDBOX=1 for --dangerously-skip-permissions, inherits `claude-opus-5-5` with `--effort xhigh`, names the Claude session and puts the whole task in the launch. The task carries no reply address: the worker reports in its own terminal.
FAIL if it omits PATH, leaves the model unset, plans to send the initial task in a later message, or gives the worker a reply address or asks it to report back to this session.
