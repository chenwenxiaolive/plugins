---
tags: [leader, herdr-core, leader-multiple-worktrees]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader Plan two parallel code tasks for my Codex session in
/volume/workspace/launcher: fix config errors in the idle, clean, fully pushed
/volume/worktree/launcher/dev-1 slot and improve CLI help in the equally ready
/volume/worktree/launcher/dev-2 slot. Each task needs its own branch, but both
return commits for my existing delivery targeting main, without separate MRs.
Can I spawn two native subagents from this session and assign one to each
worktree, perhaps using native worktree isolation? If that does not fit our
rules, give the appropriate arrangement, including where any subagents belong,
who owns Git in each checkout and how results reach the leader. Keep the current
harness/model/effort and prefer native messaging. Explain the plan only; do not
launch agents, run shell commands or edit files. Reading skill references is fine.
