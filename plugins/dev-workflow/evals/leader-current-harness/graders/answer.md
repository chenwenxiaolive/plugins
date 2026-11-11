---
type: llm
---

Judge the selected harness, model, delivery and reporting behavior, not exact
wording. A full launch command is not required for this draft; unknown bug
details and test commands may be marked for verification before launch.

PASS if it keeps the current Claude Code leader, selects a Claude Code worker with
sonnet at high matching the leader's verified settings, and places it in its own
interactive Herdr terminal in a new worktree for issue #19 with main as the MR
target. Both files are assigned, the worker carries the issue through implement
including the merge its risk score allows, validation runs on committed code with
CPU-only checks, and the worker reports to the user in its own terminal, which the
user watches in Herdr. The brief forbids memory writes and additional independent
workers, while allowing native subagents only within its own checkout and
retaining Git and delivery ownership.

FAIL if it requires switching the leader to another harness, defaults the worker
to Opus despite the stated inherited model, chooses a Codex worker, gives the
worker a reply address or asks it to report to the leader, leaves the leader to
integrate or merge the work, or launches anything.
