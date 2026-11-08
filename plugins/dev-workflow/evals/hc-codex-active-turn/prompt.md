---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

My Codex leader in hc terminal t3 is still in its current turn waiting for worker
t42, an independent Codex CLI launched with --no-daemon. The worker has a result
to report, and both terminals are working. Previously, codex queue held a reply
until the leader ended its turn. What should the worker use now? Should it wait
for the leader to become idle, add --wait to the send, or switch launch modes?
Explain when the leader can handle the report and what still needs checking
before accepting the work. Explain only; do not send messages or run commands.
