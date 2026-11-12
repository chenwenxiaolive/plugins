---
tags: [implement]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Round 0 of codex review on my MR for issue #40 came back with three findings.
The issue asks for `load_manifests(directory)`, which returns every `*.json`
manifest in file-name order for the hand-run `sync` command; it says nothing
about bad files.

1. `load_manifests` does not catch `JSONDecodeError`: one malformed manifest crashes the sync with a traceback.
2. A read from the shared volume can fail transiently, and there is no retry or fallback.
3. The manifests come back in modification-time order, not file-name order.

Which findings do I fix before asking for a merge, and what do I do with the others?
