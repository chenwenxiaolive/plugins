---
tags: [leader, worker-brief]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader Draft a delegation plan and one implementation brief for my GPT-6-Astra xhigh Codex leadership session; do not launch anything. We are in /volume/workspace/launcher on fix-config-errors, targeting main in one existing MR. Delegate the scoped config error fix in launcher/config.py::load_config and tests/test_config.py to a worker while the leader updates README.md. Invalid configs should identify the offending key, and valid configs must still load. All three paths are the complete change; no separate delivery, terminal or model is needed. CPU checks on sh-gate are authorized, no GPUs. Explain which worker mechanism and checkout you would use, who handles Git and the MR, and when validation runs.
