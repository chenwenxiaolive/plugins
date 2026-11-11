---
tags: [herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

I started an independent Claude Code worker fix-config on issue #22, in its own
worktree and its own Herdr terminal, from this Claude Code session on the same
host. I have just remembered an invariant it needs, and I also want to know when
it finishes. Should this session discover it with ListAgents and keep in touch
with SendMessage, set up notify_when_idle or an Agent Team, and then collect its
result? Explain what to do instead if not. Explain only; do not send anything or
change settings.
