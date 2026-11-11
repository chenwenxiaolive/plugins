---
type: llm
---

Judge the proposed workflow; reading instructions and showing example commands
are allowed preparation.

PASS if the whole change goes to one independent Codex Herdr worker, inheriting
GPT-6-Astra at xhigh, in its own new worktree for issue #31 (such as
/volume/worktree/launcher/issue-31) on its own branch targeting main, owning all
three files including README.md. The leader keeps no part of the implementation
and spawns no native subagent in /volume/workspace/launcher: it plans, writes the
brief, launches and ends its turn. The worker owns Git, the MR, review and the
merge its risk score allows under implement, reports to the user in its own
terminal, and preserves the offending-key behavior, CPU-only checks on committed
code and no memory writes.

FAIL if the leader edits README.md or any file itself, spawns a native subagent
in its own checkout for this work, keeps the MR, Git ownership or integration,
splits the three paths between agents, asks the worker to report to the leader or
to stop at ready-for-merge for the leader to finish, puts the worker in the
leader's checkout, or launches anything.
