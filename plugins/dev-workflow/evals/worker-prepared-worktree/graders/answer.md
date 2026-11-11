---
type: llm
---

The run has no shell, so judge the plan.
PASS if it works in the checkout and branch it is already in, without creating either again, and starts from the issue, its discussions and its execution record.
FAIL if it runs `git worktree add`, creates or renames the branch, moves to another directory, or treats the prepared checkout as something to set up.
