---
tags: [implement]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Round 0 of codex review on my MR came back with four findings:

1. The variable `cfg2` could have a more descriptive name.
2. The new config loader doesn't handle YAML files larger than 2 GB; ours are a few KB.
3. The cache key ignores the model revision, so two revisions share cached weights.
4. The cache-key function lacks a null guard and null-input tests for `config.revision`. The config loader validates it as a required string before constructing the internal config type, and all cache-key callers use that type.

The issue asked for revision-aware caching. Which findings should I fix before asking for a merge, and what do I do with the others?
