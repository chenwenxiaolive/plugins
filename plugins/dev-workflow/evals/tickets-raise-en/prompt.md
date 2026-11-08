---
tags: [to-tickets]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

We just went through why `scripts/validate.py` in our plugins repository (GitHub: chenwenxiaolive/plugins) is misleading: it stops at the first group whose `claude plugin validate --strict` fails, so the groups after it are never checked and the output doesn't say so. We agreed it should check every requested group, print each group's failures and exit non-zero if any group failed, without changing which checks run.

raise an issue to plugins
