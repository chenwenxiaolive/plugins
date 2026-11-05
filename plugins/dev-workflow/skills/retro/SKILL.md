---
name: retro
description: "Reviews a development session or a completed issue or MR for concrete improvements to this user's coding, validation and review workflow. Runs only when the user invokes it."
disable-model-invocation: true
---

# Retro

Find the few changes that would make the next task more reliable or less
repetitive. Default to the current session; use another session, issue or MR the
user names.

- Work from evidence: the conversation, MR discussions, commits, checks and run records. Look for recurring friction (repeated review findings, environment failures, unnecessary confirmations); a one-off problem gets a local fix, not a rule.
- For each finding: the evidence, its cost, the smallest change and where it belongs (project instructions, the global instructions, or the skill that covers the step), stated once. Prefer stating a missing fact or boundary to adding a procedure; a tested script is fine when it makes a step reliable.
- Report in chat by default, and say so when no change is justified. Apply changes only when asked.
