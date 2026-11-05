---
tags: [to-tickets]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/to-tickets as drafts only, don't publish: Make model caching revision-aware. The downloader should key the cache by model and revision, the server should report cache hits and misses in /metrics, and the docs should explain the cache.
