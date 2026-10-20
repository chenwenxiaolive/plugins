---
name: to-tickets
description: "Turn the current discussion or a supplied plan into actionable GitLab issues for independent coders in reusable worktrees."
disable-model-invocation: true
---

# To Tickets

Produce issues that a fresh coder can implement without the planning conversation.
Use the selected project's instructions and existing issue conventions.
Before accessing GitLab, use [gpu-cluster](../gpu-cluster/SKILL.md) and its
[GitLab guidance](../gpu-cluster/gitlab.md).

## Establish the work

- Read the supplied plan or issue, relevant code and existing issues. Reuse decisions already made in the conversation.
- Resolve the target repository from the selected checkout. Ask for the project if it cannot be determined; draft useful content while that is unresolved.
- Ask only about missing decisions that change scope, acceptance or dependencies. State reasonable assumptions for routine details.
- An explicit request to run this skill authorizes publishing the resulting issues. Honor requests for drafts or discussion only. Existing authorization to create issues needs no second confirmation.

## Split for the coders

- Make each issue a coherent, independently verifiable result suitable for one development branch and MR. A small change may need only one issue.
- Give each issue enough context, acceptance criteria and validation guidance to stand alone. Link shared decisions and source material instead of copying a long conversation.
- Declare real prerequisites and shared interface decisions. Separate work that can proceed concurrently from work whose dependencies must land first.
- Split by useful behavior or a concrete technical result, including kernel or performance work where relevant. Do not force an artificial UI/API/database split.
- For performance work, define the workload, baseline, metric and acceptance threshold if known. Leave unresolved targets explicit rather than inventing them.
- Worktree names such as `dev-1`, `dev-2` and `dev-3` identify reusable directories. Issues have no permanent worktree assignment; the user selects which coder handles each issue.

Use these fields when relevant, adapting to the project's template:

```markdown
## Goal and context
The current problem, intended behavior, and links to prior decisions.

## Scope
The result this issue delivers and important exclusions.

## Acceptance criteria
- Observable outcomes that establish completion.

## Validation
Required checks or benchmark method, including any remote/GPU requirements.

## Dependencies
Blocking issues and shared interface decisions, or none.
```

## Publish and hand off

Check for existing equivalent issues before creating new ones. Create prerequisites
first, then use their real links in dependent issues. Use native blocking
relationships if supported; otherwise make blockers explicit in the descriptions.
Use existing project labels where helpful, without creating a new label taxonomy.

If publication is interrupted or times out, inspect what was created before
retrying. Update an existing issue only within the requested scope; creating
children does not authorize closing the parent.

Return the issue links, brief outcomes, dependencies and which issues are ready to
start. If publication is blocked, distinguish drafts from published issues.
Implementation begins when the user assigns an issue to a coder.
