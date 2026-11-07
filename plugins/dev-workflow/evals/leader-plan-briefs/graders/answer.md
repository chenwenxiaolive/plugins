---
type: llm
---

PASS if the plan preserves two independent MRs touching different files, reuses the available dev-1 and dev-2 slots for delegated Herdr workers with their own branches and main as target, and defaults those workers to Opus 5.5 xhigh. Each brief tells the worker to use the implement skill, stop at ready-for-merge, start no other agents except implement's review, and write no memory notes. Keeping a small change for the leader itself is fine if its delivery stays independent. A leader-model mismatch caveat is fine if the requested draft is still supplied.
FAIL if two independent deliveries share a worktree, fresh worktrees are proposed without a reason despite the available slots, a brief omits the target branch, or the plan folds both issues into one MR.
