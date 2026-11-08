---
tags: [to-tickets]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Thanks, that settles the config loader for now. We might open an issue later to cache parsed configs, but not today. Quick question: does Python's `functools.lru_cache` work on a function that takes a dict argument?
