---
tags: [herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Pass this updated invariant to my Codex worker in terminal t42, launched with
--no-daemon: "sink tensors load sharded on axis 0 by TP rank". The last time you
did this, `hc send t42 '...'` failed with a connection error and we never found
out whether the message arrived. How do you handle that case this time, and
should you wait to see what the worker does with it? Explain only; do not run
commands or send messages.
