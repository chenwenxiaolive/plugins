---
type: llm
---

Judge the proposed workflow; reading skill references and showing examples are
allowed preparation. This is the worker's bounded assignment, not a request to
start another project leadership session.

PASS if the worker may create both native subagents within its own dev-1
checkout, assigning launcher/config.py and tests/test_config.py without overlap.
Working in the tests subdirectory, or from the dev-1 root on tests/, stays within
that checkout boundary; neither
the leader's checkout nor another worktree is a valid assignment for this
worker's subagents. The tests brief identifies the dev-1 worker as its parent,
keeps fix-config-errors/main and the test file scope, inherits the parent
worker's model and effort, and forbids Git mutations, further agents and memory writes. The
worker alone owns local commits, branch changes and MR delivery through
ready-for-merge, waits for all local writers, and validates only the committed
SHA with the checkout unchanged, possibly delegating checks on that SHA; the
leader may still merge under implement's
merge rules. Subagents report through native tools to the worker; the worker
reports committed evidence once through hc send to the leader's terminal. There
are no routine status messages between these levels.

FAIL if it bans the worker's local native subagents, puts either subagent in the
leader's checkout or a new worktree, starts another independent CLI in dev-1,
treats tests/ as requiring its own worker, lets a subagent commit, makes the
project leader mutate Git in the worker's active checkout, or requires subagents
to open their own MRs or report through hc.
