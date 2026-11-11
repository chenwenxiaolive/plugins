---
tags: [herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

My Codex worker on issue #71 was started through hc with --no-daemon. Its
verified native session UUID is 11111111-2222-4333-8444-555555555555 and its
Herdr terminal is t42; the process is still live. I want to give it one extra
instruction from here, since I am not at the Herdr app. An earlier `codex queue`
exited zero and nothing came of it, and my thread tools, attached to a different
app-server, show notLoaded while wait_threads returns immediately. Where does its
report go, how do I send the instruction, and should I add --resume or remove
--no-daemon? Do not send anything or start a process.
