---
name: improve-codebase-architecture
description: "Inspect a project's architecture and propose focused changes that improve implementation, testing or performance work in this development workflow."
disable-model-invocation: true
---

# Improve Codebase Architecture

Find the structural problems in the selected checkout that make changes, tests or
performance work hard, starting from the module the user names or else from recent
changes and issues. Use [gpu-cluster](../gpu-cluster/SKILL.md) before GitLab or
remote access; inspection needs no GPU job.

- Trace real callers and data flow. Look for changes that ripple through unrelated modules, leaky interfaces, duplicate sources of truth, hidden state, and behavior that can't be tested through a useful interface. For GPU code, account for data movement, allocation and synchronization; performance gains are hypotheses until measured.
- For each of the few strongest candidates give the evidence (files, callers, a concrete example), the change, what stays the same, how to validate it, and its tradeoffs. Say so when the current structure is adequate; new layers, wrappers or extension points need a concrete benefit.
- Report in chat by default; a standalone report goes under `/preview`. Issues follow [to-tickets](../to-tickets/SKILL.md) (read its file; only the user can invoke it as a skill), implementation through [implement](../implement/SKILL.md), when the user asks.
