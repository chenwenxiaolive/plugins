---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

My Codex leader runs in Herdr terminal t3 and coordinates a Codex worker in
terminal t42, launched with --no-daemon. Earlier, two `hc wait t42 --timeout 600`
calls returned `reason: timeout` while t42 kept reporting `working`. Then the
leader sent an updated invariant with `hc send t42 '...'`, and that command
failed with a connection error, so we do not know whether the message arrived.
What should the leader do about the failed send, and what should it have done
after those timeouts? Explain only; do not run commands or send messages.
