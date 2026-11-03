---
name: retro
description: "Review a development session or completed issue/MR for concrete improvements to this user's coding, validation and review workflow."
disable-model-invocation: true
---

# Retro

Find the few changes that would make the next task more reliable or less
repetitive. Default to the current session; use another session, issue or MR the
user names ([gpu-cluster](../gpu-cluster/SKILL.md) before GitLab or remote access).

- Work from evidence: the conversation, MR discussions, commits, checks and run records. Look for recurring friction (repeated review findings, environment failures, unnecessary confirmations); a one-off problem gets a local fix, not a rule.
- For each finding: the evidence, its cost, the smallest change and where it belongs (project instructions, `implement`, or `gpu-cluster`), stated once. Prefer removing or shortening a rule to adding one, and a rule to a script.
- Report in chat by default, and say so when no change is justified. Apply changes only when asked; a standalone report goes under `/preview`.
