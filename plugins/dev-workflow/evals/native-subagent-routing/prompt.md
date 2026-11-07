---
tags: [herdr-core, leader, native-subagent-routing]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

I am in a Codex session with native spawn, message, and wait tools. Delegate two
read-only investigations in this checkout: one agent should trace how config.py
loads configuration, and another should inspect the existing config tests.
Return both summaries in this chat. This machine has no hc installed, and I have
not requested a separate interactive CLI session. Explain how you would launch,
follow up with, and wait for the agents, whether hc must be installed, and where
I should look for their activity. Draft the plan only; do not launch agents or
run commands.
