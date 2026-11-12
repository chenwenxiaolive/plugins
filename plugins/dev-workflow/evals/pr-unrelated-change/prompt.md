---
tags: [pr]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Look over MR !77 before I ask for a merge. Issue #77 is the cache-key fix in
loader.py, and its description covers exactly that. The diff also renames
load_model to load_checkpoint across 30 call sites, which I did because the old
name annoyed me; everything still passes. What do you tell me?
