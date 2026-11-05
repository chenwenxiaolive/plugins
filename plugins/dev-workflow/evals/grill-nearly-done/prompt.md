---
tags: [grilling]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Design discussion: I want a --dry-run flag for our job launcher that prints the resolved command and exits. Goal: let people check configs without using GPUs. Scope: the launcher CLI only. Acceptance: --dry-run prints the exact command, touches no GPU and exits 0. We already decided it won't validate remote paths. Anything left before I write the issue?
