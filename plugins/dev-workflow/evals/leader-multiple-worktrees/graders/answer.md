---
type: llm
---

Judge the proposed workflow; reading instructions and showing example commands
are allowed preparation.

PASS if the leader remains in /volume/workspace/launcher and uses one independent
Codex Herdr worker in each existing dev-1/dev-2 worktree. A directory has one
independent session, which may create multiple native subagents only within its
own working directory/checkout. The leader cannot assign its native subagents to
those other worktrees or use native worktree isolation to do so. Each worker
retains its local Git ownership, waits for its local writers before committing
or integrating, and returns committed changes/evidence through hc send to the
leader's terminal t3 for its existing delivery. Separate MRs are not
required merely because separate workers are used. Inherit the current settings
and reuse the existing slots.

FAIL if native children of the leader work in dev-1/dev-2, native worktree
isolation bypasses the directory boundary, independent sessions share a checkout,
subagents are forbidden within a worker's own checkout, a worker's subagents
commit independently, or independent Codex worker reports use codex queue.
