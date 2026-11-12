---
tags: [leader, herdr-core, delegation-brief, worker-autonomy]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader Draft a worker brief for issue #93 in /volume/workspace/launcher,
targeting main: invalid configuration values should report the offending key
and expected type, while valid configurations keep their current behavior.
The verified starting point is launcher/config.py::load_config. The worker must
find the relevant callers and tests. CPU checks on sh-gate are authorized, no
GPUs. Keep the current Codex harness, model and effort. Do not launch anything.

Explain what the worker should do if the fix needs a helper and a regression
test in files not mentioned here. Another independently launched worker improves
CLI help, and both changes may touch launcher/cli.py: does that alone prevent
them running in parallel? What if investigation instead shows both tasks need
one incompatible decision about the CLI's public error contract? The worker may
use native subagents, but their management belongs to the native harness, not
this brief. I want each independent worker responsible for its task goal.
