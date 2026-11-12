---
tags: [to-tickets]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Draft an issue for the plugins repository (GitHub: chenwenxiaolive/plugins), but don't file it: `scripts/check_installation.py` gains `--output <path>`, which writes its report to that file instead of stdout, with the same exit codes.
