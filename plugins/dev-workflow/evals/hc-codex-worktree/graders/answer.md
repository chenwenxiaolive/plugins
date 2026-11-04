---
type: llm
---

PASS if it advises against Codex's --worktree option (it leaves stray checkouts and ignores the configured root), creates the worktree first (for example with `git worktree add`) and passes it as hc's --cwd, and launches codex with --no-daemon.
FAIL if it recommends codex --worktree.
