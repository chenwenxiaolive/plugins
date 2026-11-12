---
type: llm
---

Judge the proposed workflow; reading instructions and showing example commands
are allowed preparation.

PASS if the leader stays in /volume/workspace/launcher and launches one
independent Codex Herdr worker per issue, each in its own new worktree for that
issue (such as /volume/worktree/launcher/issue-44 and issue-45) on its own branch
targeting main. A directory has one independent session, which may create native
subagents only within its own checkout: the leader cannot assign its native
subagents to those worktrees, and native worktree isolation does not make that
valid. Each worker owns one issue with its Git mutations, MR, review and the
merge its risk rating allows, and reports to the user in its own terminal, which
the user watches in Herdr. The leader inherits the current harness, model and
effort, reports what runs where and ends its turn.

FAIL if native children of the leader work in those worktrees, native worktree
isolation bypasses the directory boundary, independent sessions share a checkout,
the two tasks share one worktree or one slot is reused for both, subagents are
forbidden within a worker's own checkout, the leader keeps the MR or integrates
the workers' commits, or the workers are given a reply address or asked to report
to the leader.
