---
tags: [implement]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Round 0 of codex review on my MR came back with three findings:

1. The variable `cfg2` could have a more descriptive name.
2. The new config loader doesn't handle YAML files larger than 2 GB; ours are a few KB.
3. The cache key ignores the model revision, so two revisions share cached weights.

The issue asked for revision-aware caching. Which findings should I fix before asking for a merge, and what do I do with the others?
