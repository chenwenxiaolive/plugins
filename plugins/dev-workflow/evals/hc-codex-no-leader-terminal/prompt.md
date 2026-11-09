---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

I am using a Codex leader outside Herdr. It has a CODEX_THREAD_ID but no hc
terminal. I want it to launch an independent Codex worker through hc, with
--no-daemon, for an hour-long task and receive its questions and results,
including a long validation log. Can it coordinate from here, with the worker
reporting in its own terminal for the leader to collect? If not, what should
happen instead, what becomes the worker's reply address, and how often should
the leader check on the worker? Explain only; do not launch, send or change
anything.
