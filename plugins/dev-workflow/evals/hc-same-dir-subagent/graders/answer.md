---
type: llm
---

PASS if it gives the tests to a subagent (the Agent tool) rather than starting an hc worker in /volume/workspace/launcher, because an agent already runs in that checkout. Offering an hc worker in a separate worktree as an alternative is fine.
FAIL if it starts or proposes an hc worker whose `--cwd` is /volume/workspace/launcher.
