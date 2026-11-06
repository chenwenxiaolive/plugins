---
tags: [gpu-cluster]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

My remote worktree /volume/worktree/mini-vllm/dev-3 on sh shares its clone's .git with other sessions' worktrees, and `git fetch` there doesn't bring in my new branch fix-cache. How do I update the worktree to the branch's pushed commit?
