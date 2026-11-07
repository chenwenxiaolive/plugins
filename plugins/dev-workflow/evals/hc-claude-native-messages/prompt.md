---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

We have a Claude Code leader and an independent Claude Code worker fix-config, both running on this host in separate Herdr terminals. The worker owns /volume/worktree/launcher/dev-1. Explain how the leader should discover the correct worker, send an additional invariant, receive its result and get a notice when it becomes idle. Do we need an Agent Team or hc send for this? What if SendMessage reports that the message reached the inbox but is held? Explain only; do not send anything or change settings.
