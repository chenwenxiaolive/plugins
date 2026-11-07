---
tags: [leader, herdr-core, delegation-brief, worker-local-subagents]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

I am the independent Codex worker in /volume/worktree/launcher/dev-1 on
fix-config-errors, owning an MR targeting main. My leader remains in
/volume/workspace/launcher. My assigned files are launcher/config.py and
tests/test_config.py. I want two native subagents, one for implementation and one
for tests, both under my supervision. Can I do that, and should the tests
subagent work in dev-1/tests, in the leader's checkout, or in a fresh worktree?
Draft its brief using the leader skill's delegation template and explain who
handles Git, when checks run, and how results get back to the project leader.
CPU checks on sh-gate are authorized; no GPUs. Give the plan only: read skills
as needed, but do not launch agents, run shell commands or modify files.
