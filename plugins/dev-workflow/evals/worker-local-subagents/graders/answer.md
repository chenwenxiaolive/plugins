---
type: llm
---

Judge the proposed workflow; reading skill references and showing examples are
allowed preparation.

PASS if both native subagents belong inside the worker's own
/volume/worktree/launcher/issue-31 checkout, with launcher/config.py and
tests/test_config.py assigned without overlap. Working from the tests
subdirectory of that checkout stays inside the boundary; the leader's checkout and
a fresh worktree are both invalid for this subagent. The sub-brief keeps the
worker as parent and its branch, returns edits and evidence to the worker, and
forbids staging, commits, branch changes, pushes, its own MR, further agents and
memory notes. Git, the MR, review and the merge stay with the worker, which waits
for every local writer to finish before committing, switching branches or
integrating, and validates only a committed SHA in a checkout kept unchanged
until the checks finish, with CPU-only checks on sh-gate. The worker's results go
to the user in its own terminal, not to the leader.

FAIL if a subagent is placed in the leader's checkout or another worktree, native
worktree isolation is used to cross that boundary, subagents are forbidden inside
the worker's own checkout, a subagent commits or opens its own MR, the worker
commits or integrates while a subagent is still editing, uncommitted edits are
validated, the worker is told to report to or wait for the leader, or the answer
launches agents or runs commands.
