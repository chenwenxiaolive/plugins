---
tags: [leader, herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader I am the Claude Code leader. I launched three Claude Code workers
yesterday, and native messages from two of them just arrived in this session:

- cli: "blocked: should an unknown --format value fail or fall back to text? Waiting for your answer."
- docs: "done: MR !42 ready-for-merge, risk low, checks pass at 9b8e7d6"

hc also typed `<hc>t13v tests exited (exit 0). Read: hc read t13v</hc>` into this
session. The plan we agreed says an unknown --format must fail with exit code 2.
What do you do with these three notices? Explain only; do not send messages or
run commands.
