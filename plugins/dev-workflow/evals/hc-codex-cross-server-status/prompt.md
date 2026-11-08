---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

My Codex leader runs on the Codex desktop app-server. Its worker in Herdr terminal t42 is an interactive codex --no-daemon session with native UUID 11111111-2222-4333-8444-555555555555 in /volume/worktree/mini-vllm/dev-1. On the leader, read_thread for that UUID returns status notLoaded and a latest turn "interrupted" with no completedAt, and wait_threads with timeoutMs 0 returns at once with reason inactiveStatus. hc get t42 reports live and working. The leader proposes calling send_message_to_thread for that UUID to wake the worker and continue its task on the desktop app-server. Is the worker interrupted or finished, and should we do this? Explain only; do not send anything or run commands.
