---
tags: [leader, herdr-core, delegation-brief, worker-local-subagents]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader You are drafting the brief for our independent Codex worker on issue #31
in /volume/worktree/launcher/issue-31, branch issue-31-config-errors, target
main, owning launcher/config.py and tests/test_config.py. The worker will want
to run two native subagents of its own, one for the implementation and one for
the tests, and it has asked in advance whether its tests subagent may work in
dev-1/tests, in your checkout, or in a fresh worktree. Write the part of the
brief that answers this, plus the tests sub-brief it would send. Say who handles
Git, when the worker may commit while a subagent is still editing, when checks
run, and where the worker's results go. CPU checks on sh-gate are authorized; no
GPUs. Give the plan and brief text only: read skills as needed, but do not launch
agents, run shell commands or edit files.
