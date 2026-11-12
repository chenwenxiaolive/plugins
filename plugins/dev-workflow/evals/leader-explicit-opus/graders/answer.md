---
type: llm
---

PASS if the plan preserves the explicit Claude Opus 5.5 xhigh request and uses an
independent Claude Code worker through Herdr, in its own new worktree for issue
#27, outside the leader's checkout. It recognizes that Codex native subagents
cannot supply Opus. The worker owns the issue through implement and reports to the
user in its own terminal, which the user watches and steers in Herdr. Its
one-line delivery report reaches the Codex leader with hc send to the leader's hc
terminal, which works across harnesses, so no native message between Claude and
Codex is needed.

FAIL if it substitutes a native Codex subagent for Opus, claims the native Codex
spawn tool can launch Claude Opus, runs the independent Claude Code process in
the leader's checkout, routes the worker's questions or results to the leader
instead of the user or through native messaging, has the leader integrate the
worker's commits, or launches a worker despite the plan-only request.
