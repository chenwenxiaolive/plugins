---
type: llm
---

Judge the proposed workflow. Reading skill instructions and references to draft
the plan is allowed; command examples in the answer are not executed actions.

PASS if it distinguishes the config native subagent from the independent docs
worker by creation and lifecycle ownership. Sharing a harness does not convert
the worker into a subagent. The config assignment uses the parent's
native subagent identity and message/wait/lifecycle tools, leaves Git mutations
and delivery with the leader, and needs no hc terminal or identity mapping.
The docs worker keeps its branch/MR delivery, uses hc send with the verified
terminal addresses for task messages and reports, and uses Herdr's hc commands
(such as hc get/read and hc kill/rm) for terminal/process inspection and cleanup
after acceptance while preserving its
worktree. Reports and idle notices still require verification before
acceptance. Exact wording and headings are not required.

FAIL if it treats the docs worker as a native child because it runs Codex,
assumes native child-agent lifecycle tools own that external CLI,
creates or requires an hc terminal for the config subagent, uses codex queue
for the docs worker's task messages, lets the shared-checkout subagent commit,
removes the worker's worktree during cleanup, or actually sends messages, runs
shell commands, starts/stops agents or mutates files instead of drafting the plan.
