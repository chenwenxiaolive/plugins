---
name: implement
description: "Implement an assigned issue or agreed development task in the selected checkout, through validation, MR or PR creation, coder-owned review and a requested merge. Also use before reusing a worktree for another issue/MR, proposing an issue as next work, or reviewing an MR."
---

# Implement

Own the assigned task through its MR and review outcome. Work in the checkout the
user selected and read its project instructions. This skill's references hold the
development process; read the one for what the task does next:

| Doing | Read |
|---|---|
| starting, resuming or switching a worktree to another issue/MR; naming a branch; the issue's execution record; saying whether an issue is free | [worktrees.md](worktrees.md) |
| reviewing an MR you opened, recording acceptance, or a standalone review | [review.md](review.md) |
| a requested merge, synchronizing after a server-side rebase, or recording an observed merge | [merge.md](merge.md) |

Use [gpu-cluster](../gpu-cluster/SKILL.md) for the nodes and GitLab:
[remote-workflow.md](../gpu-cluster/remote-workflow.md) for checkout paths,
synchronization, remote execution and where validation runs, and
[gitlab.md](../gpu-cluster/gitlab.md) for GitLab access.

On a GitHub repository, use `gh` for the same steps: a pull request is the MR,
the execution record is an issue comment, and `gh pr merge --match-head-commit
<sha>` is the merge API's `sha` guard. The project's own merge rules come first.

## Establish or resume the task

- Read the issue, relevant discussions and any existing MR. Identify the intended result, acceptance criteria and prerequisites. Use an already agreed task directly; a separate issue is not a prerequisite to coding.
- Continue an existing issue/MR on its development branch. For a new assignment, follow the [worktree reuse checks](worktrees.md#reusing-worktrees-for-issues-and-mr-review) before creating or switching branches. Keep the selected directory, including stable names such as `dev-1`.
- Name new issue branches using the [issue branch identity rules](worktrees.md#issue-branch-identity).
- When implementing an issue, read and maintain its [execution record](worktrees.md#issue-execution-record). Confirm ownership before coding, reuse the same comment on resume, and record the actual worktree and branch. A task without an issue needs no extra issue or record.
- If the MR was already merged, [reconcile its execution record](merge.md#record-merge-completion) before resuming or reusing the checkout. Report the merged MR and any remaining issue scope; do not recreate a deleted source branch or resume implementation without a new assignment.
- Resolve unmet dependencies before building on them. Use another unmerged task branch only for an explicitly intended dependency.
- On resume, inspect the actual branch, worktree, MR source commit, review findings and persisted round count. Preserve existing work and running jobs; handle unclear ownership or divergence before switching or synchronizing.

## Implement and validate

- For new features and bug fixes, follow this order: update docs and comments first → write a minimal test that currently fails → write the minimal implementation → finally check that tests, code, and docs are consistent. When the test runs remotely, push and validate the failing-test phase before implementing the fix locally. Choose a test that exercises the real behavior through an appropriate existing interface.
- Expected results must come from a specification, known example or independent reference. Prefer real internal behavior; isolate external dependencies or nondeterminism when needed. Routine test choices do not require a separate confirmation.
- Projects are internal and still under development: use KISS design, keep no backward-compatibility layers, and write no data migrations. Prefer small interfaces and keep related behavior together. Add abstraction for current requirements rather than anticipated extensions.
- For a hard bug, establish a useful reproduction, compare plausible causes and change one variable at a time. For a performance regression, measure a baseline with a controlled workload before claiming improvement. Recheck the original symptom after the fix.
- Use [validation scope](../gpu-cluster/remote-workflow.md#validation-scope) to choose local checks or remote execution and record results.
- GPU execution requires a user-designated node and free GPUs. If the node or another essential validation input is missing, continue independent local preparation and request the missing input. Preserve the failing-test-before-implementation sequence for dependent work. Do not claim an unrun check passed.
- Run checks that establish the acceptance criteria and cover affected behavior. Remove temporary instrumentation and keep run artifacts outside the repository under the prescribed temporary directory.

## Deliver and review

Commit only this task's changes, push its development branch and create or update
the MR. Use the project template; describe the resulting behavior, issue links,
validation evidence and material limitations. Use a closing reference only when
the MR fulfills that issue. Add its link to the issue's execution record and update
that record at its defined milestones. Keep review details in the MR.

Continue into the [coder-owned review loop](review.md#coder-owned-review-after-opening-an-mr)
for the review command, the acceptance record, the corrective-round limit and
the records to keep across interruptions. An issue-free task uses the agreed
request as its source.

Finish with the MR link, source commit, validation outcome and review status. If
the loop reaches its limit or a required review/check cannot run, report the
remaining findings or blocker for human handling. A successful review leaves the
MR ready for the user's merge decision; merge only when requested, following
[merge.md](merge.md).
