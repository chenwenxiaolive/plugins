---
name: implement
description: "Implement an assigned issue or agreed development task in the selected checkout, through validation, MR or PR creation and coder-owned review."
---

# Implement

Own the assigned task through its MR and review outcome. Work in the checkout the
user selected. Read its project instructions and use
[gpu-cluster](../gpu-cluster/SKILL.md), especially
[remote-workflow.md](../gpu-cluster/remote-workflow.md) and
[gitlab.md](../gpu-cluster/gitlab.md). These are authoritative for checkout reuse,
remote execution, GitLab access and the bounded review loop.

On a GitHub repository, use `gh` for the same steps: a pull request is the MR,
the execution record is an issue comment, and `gh pr merge --match-head-commit
<sha>` is the merge API's `sha` guard. The project's own merge rules come first.

## Establish or resume the task

- Read the issue, relevant discussions and any existing MR. Identify the intended result, acceptance criteria and prerequisites. Use an already agreed task directly; a separate issue is not a prerequisite to coding.
- Continue an existing issue/MR on its development branch. For a new assignment, follow the worktree reuse checks before creating or switching branches. Keep the selected directory, including stable names such as `dev-1`.
- Name a new issue implementation branch `agent/K-<short-description>`, such as `agent/42-fix-cache`, using the [issue branch identity rules](../gpu-cluster/remote-workflow.md#issue-branch-identity).
- When implementing an issue, read and maintain its [execution record](../gpu-cluster/remote-workflow.md#issue-execution-record). Confirm ownership before coding, reuse the same comment on resume, and record the actual worktree and branch. A task without an issue needs no extra issue or record.
- If the MR was already merged, [reconcile its execution record](../gpu-cluster/merge-workflow.md#record-merge-completion) before resuming or reusing the checkout. Report the merged MR and any remaining issue scope; do not recreate a deleted source branch or resume implementation without a new assignment.
- Resolve unmet dependencies before building on them. Use another unmerged task branch only for an explicitly intended dependency.
- On resume, inspect the actual branch, worktree, MR source commit, review findings and persisted round count. Preserve existing work and running jobs; handle unclear ownership or divergence before switching or synchronizing.

## Implement and validate

- Follow the existing docs/comments → minimal failing test → minimal implementation → consistency checks sequence for features and fixes. Choose a test that exercises the real behavior through an appropriate existing interface.
- Expected results must come from a specification, known example or independent reference. Prefer real internal behavior; isolate external dependencies or nondeterminism when needed. Routine test choices do not require a separate confirmation.
- Prefer small interfaces and keep related behavior together. Add abstraction for current requirements rather than anticipated extensions. Follow the existing KISS, compatibility and migration rules.
- For a hard bug, establish a useful reproduction, compare plausible causes and change one variable at a time. For a performance regression, measure a baseline with a controlled workload before claiming improvement. Recheck the original symptom after the fix.
- Execute tests, builds and GPU work under the remote workflow, against committed code in a clean checkout at the same absolute path. Record the required commit, node, command and artifacts with the result.
- GPU execution requires a user-designated node and free GPUs. If the node or another essential validation input is missing, continue independent local preparation and request the missing input. Preserve the failing-test-before-implementation sequence for dependent work. Do not claim an unrun check passed.
- Run checks that establish the acceptance criteria and cover affected behavior. Remove temporary instrumentation and keep run artifacts outside the repository under the prescribed temporary directory.

## Deliver and review

Commit only this task's changes, push its development branch and create or update
the MR. Use the project template; describe the resulting behavior, issue links,
validation evidence and material limitations. Use a closing reference only when
the MR fulfills that issue. Add its link to the issue's execution record and keep
that record's status current through review, blockers and the final outcome.

Record the agreed criteria, their implementation and validation evidence in the
MR's review-status section using the
[requirement acceptance procedure](../gpu-cluster/remote-workflow.md#requirement-acceptance-within-each-review-pass).
An issue-free task uses the agreed request as its source. A code review reporting
no findings is not sufficient to establish requirement completion.

Continue into the
[coder-owned review loop](../gpu-cluster/remote-workflow.md#coder-owned-review-after-opening-an-mr):
Claude Code invokes `codex:review`; Codex reviews directly. The initial review is
followed by at most three fix-and-re-review rounds, shared by requirement gaps and
code-review findings. Refresh the acceptance assessment on each pass. Persist the
round count and evidence in the MR, and resume the existing count after interruptions.

Finish with the MR link, source commit, validation outcome and review status. If
the loop reaches its limit or a required review/check cannot run, report the
remaining findings or blocker for human handling. A successful review leaves the
MR ready for the user's merge decision; merge only when requested.

When the user requests merging, follow the shared
[merge workflow](../gpu-cluster/merge-workflow.md), including rechecking the current
source and target, preserving the review-round count, and updating the issue's
execution record after the merge is confirmed.
