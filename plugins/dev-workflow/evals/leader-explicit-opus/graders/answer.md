---
type: llm
---

PASS if the plan preserves the explicit Claude Opus 5.5 xhigh request, uses a Claude Code worker through Herdr and reuses /volume/worktree/launcher/dev-1 after the normal availability checks. It recognizes that Codex native subagents cannot supply Opus and keeps the external worker out of the leader's checkout. It does not require a new MR merely because Herdr is used; integration into the leader's existing delivery can be coordinated by the leader. A leader-model mismatch caveat is fine if the requested plan is supplied.
FAIL if it substitutes a native Codex subagent for Opus, claims the native Codex spawn tool can launch Claude Opus, runs the independent Claude Code process in the leader's checkout, creates a fresh worktree without a reason, or launches a worker despite the plan-only request.
