---
tags: [leader, herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader My Codex leadership session runs in Herdr terminal t3. Codex worker
cfg-fix in /volume/worktree/launcher/dev-1, terminal t42, was launched 40
minutes ago. Its brief asks for one final report with commit and checks; the
task usually takes about an hour. Since then, four
`hc wait t42 --timeout 600` calls returned `reason: timeout`. t42 still
reports `working`, and no message, blocked, error or exit notice has arrived.
Nothing else needs my attention. Should I ask it for progress or read its
terminal now? What exactly do I do next? Explain only; do not run commands or
send messages.
