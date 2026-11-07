---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

My Codex leader started a Codex worker through hc with --no-daemon. Its verified native session UUID is 11111111-2222-4333-8444-555555555555 and its Herdr terminal is t42. That process is still live. The leader's thread tools, attached to a different app-server, show notLoaded and wait_threads returns immediately. codex queue exited zero, but the worker has not returned its result yet. Explain how to send another instruction and receive the worker's report, what these statuses prove, and whether we should add --resume or remove --no-daemon. Do not send anything or start a process.
