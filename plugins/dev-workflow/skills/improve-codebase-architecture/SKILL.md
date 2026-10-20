---
name: improve-codebase-architecture
description: "Inspect a project's architecture and propose focused changes that improve implementation, testing or performance work in this development workflow."
disable-model-invocation: true
---

# Improve Codebase Architecture

Identify concrete structural problems and practical improvements in the selected
checkout. Start with the module or concern the user names. If none is named,
inspect recent changes and existing issues for areas that are repeatedly hard to
change, understand or test.

Read the project's instructions, relevant code, tests and existing architectural
decisions. Use [gpu-cluster](../gpu-cluster/SKILL.md) before GitLab access, remote
commands or experiments.

## Find consequential problems

Trace real callers and data flow. Look for:

- A change to one behavior repeatedly requiring unrelated modules to be edited.
- Interfaces that expose internal details or require callers to coordinate too many steps.
- Duplicate sources of truth, unclear ownership, or hidden state and ordering assumptions.
- Tests that miss important behavior because the useful interface is difficult to exercise.
- Structure that makes an identified correctness or performance problem difficult to measure or fix.

Judge a proposed module by the complexity its interface hides and the behavior it
keeps together. Prefer existing interfaces and current requirements. Splitting
files, adding wrappers or introducing extension points needs a concrete benefit.

For inference or GPU code, inspect boundaries such as scheduling, cache ownership,
execution and kernels only where relevant to the project. Account for data
movement, allocation, synchronization and call overhead when proposing a change.
Treat performance benefits as hypotheses until measured under the existing
remote validation rules; architectural inspection itself needs no GPU job.

## Present actionable candidates

For each substantial candidate, show:

- **Evidence:** relevant files, callers or tests and a concrete example of the problem.
- **Change:** the proposed responsibility or interface change and why it helps.
- **Scope:** what behavior remains the same, intended behavior changes if any, and affected callers.
- **Validation:** checks that protect behavior and any measurement needed to test a performance claim.
- **Tradeoffs:** complexity, risks and prerequisites.

Prioritize the few candidates with the strongest evidence. Include a small
before/after diagram when it clarifies the structure. State when the current
architecture is adequate instead of manufacturing a refactor.

Use concise findings in chat by default. A requested standalone Markdown or HTML
report belongs under `/preview` with its service URL.

## Follow the user's next step

An architecture assessment produces recommendations. If the user requests issues,
use the [ticket workflow](../to-tickets/SKILL.md) for the selected candidates. If
the user requests implementation, use the [implementation workflow](../implement/SKILL.md)
in the selected worktree. Keep ordinary improvements within the existing KISS,
compatibility, migration and merge rules.

When the implementation scope is already authorized and clear, proceed without a
second blanket approval. When materially different designs remain, explain their
tradeoffs and ask for the decision that affects the result before doing dependent
work.
