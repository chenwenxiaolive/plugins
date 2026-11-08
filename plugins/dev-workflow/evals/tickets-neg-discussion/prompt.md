---
tags: [to-tickets]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

We're still deciding the design, so no ticket or code yet: our job launcher should retry failed node allocations. Should the retries back off exponentially or use a fixed interval, and should the retry budget be per job or global? Give me your recommendation and the tradeoffs.
