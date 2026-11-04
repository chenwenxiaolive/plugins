---
name: improve-codebase-architecture
description: "Inspects a project's architecture and proposes focused structural changes that make implementation, testing or performance work easier. Runs only when the user invokes it."
disable-model-invocation: true
---

# Improve Codebase Architecture

Find the structural problems in the selected checkout that make changes, tests or
performance work hard, starting from the module the user names or else from recent
changes and issues. Use [gpu-cluster](../gpu-cluster/SKILL.md) before GitLab or
remote access; inspection needs no GPU job.

- Propose the few strongest changes, each with its evidence from the code (files, real callers, a concrete example), how to validate it and its tradeoffs. Performance gains are hypotheses until measured.
- Say so when the current structure is adequate; a new layer, wrapper or extension point needs a concrete benefit.
- Report in chat by default; a standalone report goes under `/preview`. Issues follow [to-tickets](../to-tickets/SKILL.md) (read its file; only the user can invoke it as a skill), implementation through [implement](../implement/SKILL.md), when the user asks.
