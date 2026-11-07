---
tags: [leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader Two native subagents are editing disjoint files in the leader's /volume/workspace/launcher checkout on fix-config-errors for one MR. The config worker has finished launcher/config.py and asks to commit its files and run checks now. The tests worker is still editing tests/test_config.py. Meanwhile main advanced and the leader wants to merge it. What should each agent do next, and how do we get to validated changes ready for review?
