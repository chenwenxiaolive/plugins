---
tags: [leader, herdr-core, delegation-brief, worker-local-subagents]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader You remain the project leader in /volume/workspace/launcher. Our
independent Codex worker in /volume/worktree/launcher/dev-1 on fix-config-errors
owns an MR targeting main and the files launcher/config.py and
tests/test_config.py. It asks to create two native subagents under its own
supervision: one for implementation, one for tests. Should we allow that, and
should its tests subagent work in dev-1/tests, in your checkout, or in a fresh
worktree? Draft your reply and the tests brief for the worker to send, using the
delegation template. Explain who handles Git, when checks run, and how results
get back to you. CPU checks on sh-gate are authorized; no GPUs. Give the plan
only: read skills as needed, but do not launch agents, run shell commands or
modify files.
