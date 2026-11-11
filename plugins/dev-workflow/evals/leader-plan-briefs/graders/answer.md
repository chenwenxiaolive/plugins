---
type: llm
---

PASS if the plan gives each issue its own Codex Herdr worker, inheriting
GPT-6-Astra xhigh, each in its own new worktree for that issue under
/volume/worktree/launcher/ on its own branch with main as target, producing two
independent MRs that touch different files. Each brief names the target branch,
tells the worker to carry its single issue through implement including the merge
its risk score allows, to report to the user in its own terminal, and to write no
memory notes. Workers may create native subagents only in their own checkout,
retaining Git and delivery ownership, and cannot start independent workers or
assign subagents elsewhere. The leader keeps neither issue for itself and ends
its turn after launching.

FAIL if two independent deliveries share a worktree, a worktree is reused for
both issues, a brief omits the target branch, the plan folds both issues into one
MR, the leader keeps part of the implementation, or a brief gives a reply address
or asks the worker to report to the leader or to stop at ready-for-merge for the
leader to finish.
