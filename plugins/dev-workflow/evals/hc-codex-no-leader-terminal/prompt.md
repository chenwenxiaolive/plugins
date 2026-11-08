---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

I am using a Codex leader outside Herdr. It has a CODEX_THREAD_ID but no hc
terminal. Its independent Codex worker runs in hc terminal t42 with --no-daemon;
inside that worker HC_TERMINAL_ID is t42. Prepare the communication part of the
worker brief and explain how the leader will send follow-ups and collect
questions and results, including a long validation log. Do we need to create a
terminal for the leader? Explain only; do not launch, send or change anything.
