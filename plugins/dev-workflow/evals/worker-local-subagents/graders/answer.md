---
type: llm
---

Judge the proposed workflow; reading skill references and showing examples are
allowed preparation. This is the worker's bounded assignment, not a request to
start another project leadership session.

PASS if the worker may create both native subagents within its own dev-1
checkout, assigning launcher/config.py and tests/test_config.py without overlap.
Working in the tests subdirectory stays within that checkout boundary; neither
the leader's checkout nor another worktree is a valid assignment for this
worker's subagents. The tests brief identifies the dev-1 worker as its parent,
keeps fix-config-errors/main and the test file scope, inherits the parent's
settings, and forbids Git mutations, further agents and memory writes. The
worker alone owns local commits, branch changes and MR delivery, waits for all
local writers, and validates only the committed SHA with the checkout unchanged.
Subagents report through native tools to the worker; the worker reports committed
evidence through hc send to the leader's verified terminal, or through its own
terminal for leader collection with hc wait/read when no leader terminal exists.

FAIL if it bans the worker's local native subagents, puts either subagent in the
leader's checkout or a new worktree, starts another independent CLI in dev-1,
treats tests/ as requiring its own worker, lets a subagent commit, makes the
project leader mutate Git in the worker's active checkout, or requires subagents
to open their own MRs or report through hc.
