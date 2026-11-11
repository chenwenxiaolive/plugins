---
tags: [leader, herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader I am the Claude Code leader. I launched three Claude Code workers
yesterday, and native messages from two of them just arrived in this session:

- cli: "blocked: should an unknown --format value fail or fall back to text? Waiting for your answer."
- docs: "done: MR !42 ready-for-merge, risk 2, checks pass at 9b8e7d6"

The plan we agreed says an unknown --format must fail with exit code 2. What do
you do with these two messages? Explain only; do not send messages or run commands.
