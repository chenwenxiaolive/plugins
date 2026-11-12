---
type: llm
---

Judge the proposed workflow; reading instructions and showing example commands
are allowed preparation.

PASS if the leader stays in /volume/workspace/launcher and launches one
independent Codex Herdr worker per issue, each in its own new worktree for that
issue (such as /volume/worktree/launcher/issue-44 and issue-45) on its own branch
targeting main. A directory has one independent session. Each worker owns one
issue with its MR, review and the
merge its risk rating allows, and reports to the user in its own terminal, which
the user watches in Herdr. The leader inherits the current harness, model and
effort, reports what runs where and ends its turn.

FAIL if independent sessions share a checkout,
the two tasks share one worktree or one slot is reused for both,
the leader keeps the MR or integrates
the workers' commits, or the workers' questions or results are routed to the
leader instead of the user. A one-line delivery-state report to the leader is fine.
