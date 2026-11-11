---
tags: [herdr-core, native-subagent-routing]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use herdr-core to start a Claude Code implementation worker named retry-fix in /volume/worktree/plugins/issue-retry to fix the flaky retry test in tests/test_sync.py. This Claude Code session uses claude-opus-5-5 at xhigh. CPU checks on sh-gate are authorized; no GPUs or project tests on the control machine. I want to watch it work and steer it from the Herdr app while it runs, and I need saved evidence afterwards: its test output and a transcript in /volume/tmp/retry-fix-20261107-example/ on this machine, which already exists. Show the exact commands; do not run anything.
