---
type: llm
---

Judge the selected harness, model, delivery and reporting behavior, not exact
wording. A full launch command is not required for this draft; unknown bug
details and test commands may be marked for verification before launch.

PASS if it keeps the current Claude Code leader, selects a Claude Code worker with
sonnet at high matching the leader's verified settings, and places it in its own
interactive Herdr terminal in a new worktree for issue #19 with main as the MR
target. Both files are included as context, the worker carries the issue through implement
including the merge its risk rating allows, validation runs on committed code with
CPU-only checks, and the worker reports to the user in its own terminal, which the
user watches in Herdr. The brief forbids memory writes and additional independent
workers, while retaining delivery responsibility without prescribing native
subagent management.

FAIL if it requires switching the leader to another harness, defaults the worker
to Opus despite the stated inherited model, chooses a Codex worker, gives the
worker's questions or results to the leader instead of the user, leaves the
leader to integrate or merge the work, or launches anything. A one-line delivery-state report to the leader is fine.
