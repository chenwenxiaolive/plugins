---
tags: [herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Using herdr-core, show the command or short script to run our existing CPU-only check `python3 check_links.py` in the background from /volume/worktree/docs/dev-1. Save stdout and stderr to /volume/tmp/docs-check-20261107-example/check.log and keep the output visible in its own Herdr space while it runs. The directory already exists. A failing check must still make the job fail. Show only; do not run anything.
