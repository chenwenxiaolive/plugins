---
name: implement
description: "Implements development tasks and manages issue ownership, PR/MR reviews and merges in the selected checkout. Use for task execution, issue availability, review findings or merge requests."
---

# Implement

Handle the requested operation in the selected checkout under its project rules.
A status or availability question does not claim an issue or start implementation.
An implementation task continues through validation, MR/PR and review, then merge
when authorized by the [merge rules](#merge). On GitHub, use `gh` for the same work.

## Start or resume

- Read the issue, its discussions and any existing MR. An agreed task needs no issue.
- Name a new issue branch `issue-<iid>-<2-4 words>`, e.g. `issue-42-fix-cache`, created from the fetched target branch; base it on another unmerged branch only for an intended dependency.
- One issue gets one worktree and one branch, for that issue alone. Create them if they don't exist yet, with `git worktree add --no-track -b <branch> /volume/worktree/<repo>/issue-<iid> origin/<target>`, naming the worktree for the task when it has no issue; a checkout prepared for this task and already on its branch needs nothing. Leave a worktree to its own task rather than switching it to the next one, and never remove one unless the user asks.
- If the MR was already merged, update the execution record and report; don't recreate its branch.

## Execution record

Read [issue ownership](references/issue-ownership.md) before proposing or claiming
an issue and when updating its execution record.

## Implement and validate

- Update docs when documented behavior or usage changes; add or adjust tests when the changed behavior needs coverage beyond existing checks. Choose validation to match the task and its acceptance criteria.
- Expected results come from a specification, known example or independent reference.
- Take each acceptance criterion's run from the issue as written. Where the issue gives none, state one before changing code, against the real surface: the command, the request or the stored value; a criterion on instruction text needs none ([review.md](references/review.md)). The MR's evidence carries the runs, marks the ones you stated and gives the reason for any of the issue's you had to change; the review repeats them, so a criterion without one is a gap to report, not a pass.
- A bug fix starts from a run that fails on the target commit for the reported reason; when that run is a new test, commit the test before the fix.
- Tests on the target commit pass unedited. Edit or delete one only when a requirement changes what it expects, and list it in the MR's contract.
- Where the project has a [verify skill](references/project-verify.md), launch and drive it as that says, and update it in the same MR when the task changes how the project starts or what a feature shows.
- Let errors propagate and the task or process fail unless a requirement calls for handling or recovery: the original error and traceback are an acceptable result, also for a reachable file, dependency or resource failure. That a call can fail is no such requirement and earns no guard, catch, retry, fallback, default, wrapper or failure-only test. Implement and check the recovery a task does ask for.

## Deliver and review

Push the branch and open the MR, writing its description and risk statement as
[pr](../pr/SKILL.md) describes and keeping the project's own template where it
has one. When the target branch moves under a pushed MR, merge the
target into the branch, resolve it there and rerun the affected checks; rebasing
or resetting a pushed branch would need a force-push.

In Mermaid state diagrams, use commas instead of literal `;` in transition labels:
the parser can turn the remaining words into disconnected states without an error.
When asked to fix a published diagram, correct the MR/PR's Mermaid source as well
as any preview copy.

For the implementation's review or a requested standalone review, read
[review.md](references/review.md): the verifier for each client and where it runs, what counts as a finding, what instruction text gets instead, the
single corrective round and the status record. A standalone review ends with a verdict in chat;
post it to the MR only when asked.

## Merge

After review passes, or when the user requests a merge, read
[merge.md](references/merge.md) for the risk rating, authorization, current-commit
checks, guarded merge and recovery after a timeout. Do not treat a pending merge
as completed.
