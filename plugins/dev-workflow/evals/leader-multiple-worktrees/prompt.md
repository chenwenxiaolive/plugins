---
tags: [leader, herdr-core, leader-multiple-worktrees]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader Plan two parallel code tasks for my Codex session in
/volume/workspace/launcher: issue #44 fixes the config errors and issue #45
improves the CLI help. The outcomes are independent and both target main. Can
both independent Herdr workers use this checkout on different branches? Give the
appropriate arrangement: which worker runs where, which checkout and branch each
one gets, who owns Git and the MR in each, and where each task's result goes.
Keep the current harness, model and effort. Explain the plan only; do not launch
agents, run shell commands or edit files. Reading skill references is fine.
