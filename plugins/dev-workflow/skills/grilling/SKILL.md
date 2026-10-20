---
name: grilling
description: "Clarify or stress-test a feature, technical design or development plan when the user asks for grilling, probing questions or a design discussion."
---

# Grilling

Help the user reach a decision that can become an issue or an implementation task.
Build on the current conversation and selected project's instructions.

## Investigate before asking

Read the relevant code, documentation and existing decisions to establish facts.
Check assumptions about current behavior against the implementation. Use
[gpu-cluster](../gpu-cluster/SKILL.md) before GitLab access or remote operations.
Gather independent facts yourself; delegate only when authorized.

Distinguish:

- Decisions already settled by the user or project conventions.
- Facts you can verify.
- Choices the user needs to make because the alternatives change the result.

## Discuss the important choices

Ask a small batch of questions that can be answered now, usually one to three.
For each, explain the concrete consequence, offer a recommendation and name the
main tradeoff. Follow dependencies between decisions instead of asking about
details that an earlier answer may invalidate.

Focus on intended behavior, scope, acceptance, important interfaces and real
constraints. Where relevant, discuss correctness, numerical tolerance, workloads,
latency/throughput, memory use and available validation resources.

Probe uncertainty with concrete scenarios or counterexamples. Distinguish measured
facts from estimates and proposals. Inspect available evidence before proposing
an experiment; running a GPU experiment still needs the user's node selection.

Avoid reopening settled choices or turning routine implementation details into
approval requests. Record a reasonable assumption when the difference is minor;
ask when the alternatives materially change the user's outcome.

## Close with a usable decision

Stop when the goal, scope, acceptance criteria and material tradeoffs are clear
enough for the requested next step. Summarize decisions, assumptions and genuine
open questions, referencing existing issue or design material where useful.

Discussion alone produces this summary. If the user has already requested issue
creation or implementation, proceed under that authorization; a second blanket
confirmation is unnecessary. Follow the [ticket workflow](../to-tickets/SKILL.md)
or [implementation workflow](../implement/SKILL.md) for the requested next step.
Creating tickets or editing code requires that next step to be within the user's
request.
