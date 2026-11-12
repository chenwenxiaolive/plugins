---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

I am using a Codex session outside Herdr to start work on issue #63. It has a
CODEX_THREAD_ID but no hc terminal of its own, and its shell has TERM=dumb and no
COLORTERM. I want it to launch an independent Codex worker through hc, with
--no-daemon, for an hour-long task that produces a long validation log. Can it
launch from here, or does it need its own Herdr terminal first? Show the launch
command. Where do the worker's questions and results go, and how often should
this session check on it? Explain only; do not launch, send or change anything.
