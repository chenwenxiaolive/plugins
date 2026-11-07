---
type: llm
---

Judge the proposed workflow. Reading skill instructions and references to draft
the plan is allowed; command examples in the answer are not executed actions.

PASS if it distinguishes the config native subagent from the independent docs
worker by creation and lifecycle ownership. Native cross-session messaging does
not convert the worker into a subagent. The config assignment uses the parent's
native subagent identity and message/wait/lifecycle tools, leaves Git mutations
and delivery with the leader, and needs no hc terminal or identity mapping.
The docs worker keeps its branch/MR delivery, uses codex queue with verified
native session identities for task messages and reports, and uses Herdr for
terminal/process inspection and cleanup after acceptance while preserving its
worktree. Native reports and idle notices still require verification before
acceptance. Exact wording and headings are not required.

FAIL if it treats the docs worker as a native child because it uses Codex
messaging, assumes native child-agent lifecycle tools own that external CLI,
creates or requires an hc terminal for the config subagent, substitutes hc send
for ordinary same-harness task messages, lets the shared-checkout subagent commit,
removes the worker's worktree during cleanup, or actually sends messages, runs
shell commands, starts/stops agents or mutates files instead of drafting the plan.
