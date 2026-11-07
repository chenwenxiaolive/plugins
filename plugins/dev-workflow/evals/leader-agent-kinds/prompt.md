---
tags: [leader, herdr-core, leader-agent-kinds]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader I have two active Codex assignments. The config agent was created by
this session's native spawn tool and edits its assigned files in the leader's
/volume/workspace/launcher checkout. The docs agent was launched as a separate
interactive Codex CLI through hc in /volume/worktree/launcher/dev-1, owns its
branch/MR, and exchanges reports with the leader using codex queue. Its native
session UUID, leader reply address and Herdr terminal mapping are verified.
Since both communicate through Codex, are they both subagents now? Explain what
to call each one, how to send feedback and wait for its result, who handles Git,
and how to end each assignment after accepting its work. Give the plan only;
do not send messages, run commands or stop anything.
