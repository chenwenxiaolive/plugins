---
name: retro
description: "Review a development session or completed issue/MR for concrete improvements to this user's coding, validation and review workflow."
disable-model-invocation: true
---

# Retro

Find a small number of changes that would make the next task more reliable or
less repetitive. Default to the current task or session; use another session,
issue or MR when the user identifies it.

## Use actual evidence

Review the relevant conversation, issue/MR discussions, commits, check results and
run records that are available. Use [gpu-cluster](../gpu-cluster/SKILL.md) before
GitLab or remote access. Read only the records needed for this retrospective,
respecting the existing credential and artifact rules.

Look for recurring friction such as unclear acceptance criteria, unnecessary
confirmations, worktree switching problems, repeated environment failures,
ineffective tests or repeated review findings. A one-off problem may deserve a
local fix without becoming a rule for every future task.

Separate observed facts, plausible causes and unresolved questions. Do not claim
access to missing session history or attribute a failure to a cause without
supporting evidence.

## Recommend a narrow improvement

For each worthwhile finding, state:

- The event or repeated pattern and its evidence.
- Its effect on correctness, time or user effort.
- The smallest useful change and where it belongs.
- How a later task could show whether the change helped.

Use project tests or existing automated checks for deterministic project errors.
Use project instructions for project conventions, `implement` and its references
for the development process across projects, and `gpu-cluster` references for
infrastructure procedures. Change the authoritative location once rather than copying a rule
into several skills.

Keep the report short and prioritize by likely benefit. There is no quota of
findings; report that no workflow change is justified when the evidence is weak.

## Act within the request

By default, return recommendations in chat. If the user has asked to apply the
improvements, make the supported changes within that scope and verify them.
Existing authorization needs no repeat confirmation. Proposals for new policies,
hooks, infrastructure changes or unrelated refactors do not authorize those
changes by themselves.

State which changes were applied and which remain proposals. If a standalone
report is requested, follow the `/preview` rule; keep operational records in the
prescribed run directory. Prefer links to existing evidence over duplicate logs.
