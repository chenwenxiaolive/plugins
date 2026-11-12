---
type: llm
---

Judge the proposed workflow; reading instructions and showing example commands
are allowed preparation.

PASS if the whole change goes to one independent Codex Herdr worker, inheriting
GPT-6-Astra at xhigh, in its own new worktree for issue #31 (such as
/volume/worktree/launcher/issue-31) on its own branch targeting main, responsible for the complete behavior, tests and documentation
including README.md. The leader keeps no part of the implementation
in /volume/workspace/launcher: it plans, writes the brief, launches and ends
its turn. The worker owns Git, the MR, review and the
merge its risk rating allows under implement, reports to the user in its own
terminal, and preserves the offending-key behavior, CPU-only checks on committed
code and no memory writes.

FAIL if the leader edits README.md or any file itself, keeps the MR, Git ownership or integration,
splits the issue across independent deliveries, routes the worker's questions or
results to the leader instead of the user, has it stop at ready-for-merge for the
leader to finish, puts the worker in the leader's checkout, or launches anything. A one-line delivery-state report to the leader is fine.
