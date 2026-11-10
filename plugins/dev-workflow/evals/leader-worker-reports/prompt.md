---
tags: [leader, herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader I am the Claude Code leader. While I was reviewing a diff, three final
native messages arrived from my independent Claude Code workers:

- parser (dev-1): "done: tokenizer at 3f2a1c9, MR !41 ready-for-merge, risk 1, checks pass"
- docs (dev-2): "done: MR !42 ready-for-merge, risk 2, checks pass at 9b8e7d6"
- cli (dev-3): "blocked: should an unknown --format value fail or fall back to text?"

The plan we agreed says an unknown --format must fail with exit code 2. parser
and docs have finished. What do you do with these reports, in what order, and
which messages do you send? Explain only; do not send messages or run commands.
