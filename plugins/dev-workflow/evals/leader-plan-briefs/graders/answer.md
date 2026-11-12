---
type: llm
---

PASS if the plan gives each issue its own Codex Herdr worker, inheriting
GPT-6-Astra xhigh, each in its own new worktree for that issue under
/volume/worktree/launcher/ on its own branch with main as target, producing two
independent MRs with separate task goals. Each brief names the target branch,
tells the worker to carry its single issue through implement including the merge
its risk rating allows, to report to the user in its own terminal, and to write no
memory notes. Workers retain delivery responsibility and cannot start more
independent workers. The leader keeps neither issue for itself and ends
its turn after launching.

FAIL if two independent deliveries share a worktree, a worktree is reused for
both issues, a brief omits the target branch, the plan folds both issues into one
MR, the leader keeps part of the implementation, a brief routes the worker's
questions or results to the leader instead of the user or has it stop at
ready-for-merge for the leader to finish, or an owned-file list restricts either
worker's implementation. A one-line delivery-state report to the leader is fine.
