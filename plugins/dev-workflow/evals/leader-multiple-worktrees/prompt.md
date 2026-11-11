---
tags: [leader, herdr-core, leader-multiple-worktrees]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader Plan two parallel code tasks for my Codex session in
/volume/workspace/launcher: issue #44 fixes the config errors and issue #45
improves the CLI help. The files do not overlap and both target main. Can I spawn
two native subagents from this session and assign one to each task's worktree,
perhaps using native worktree isolation? If that does not fit our rules, give the
appropriate arrangement: which agent runs where, which checkout and branch each
one gets, who owns Git and the MR in each, and where each task's result goes.
Keep the current harness, model and effort. Explain the plan only; do not launch
agents, run shell commands or edit files. Reading skill references is fine.
