---
name: implement
description: "Implements an assigned issue or agreed development task in the selected checkout, through validation, an MR or PR, its review and a requested merge, under this user's rules for branches, execution records, which review findings to fix or reject, and merge guards. Use it for any question about this user's issues, MRs or PRs: starting, resuming or claiming an issue, checking whether one is free or proposing it as next work, reusing a worktree, reviewing an MR or acting on its codex review findings, and merging, including after a failed or timed-out merge."
---

# Implement

Own the assigned task through its MR and review outcome, in the checkout the user
selected. Read its project instructions. On GitHub, `gh` does the same steps: a pull
request is the MR. The project's own rules come first.

## Start or resume

- Read the issue, its discussions and any existing MR. An agreed task needs no issue.
- Name a new issue branch `issue-<iid>-<2-4 words>`, e.g. `issue-42-fix-cache`, created from the fetched target branch; base it on another unmerged branch only for an intended dependency.
- Create a worktree with `git worktree add --no-track -b <branch> <path> origin/<target>`. Before switching one to another task, its work must be committed and pushed, and no process may be working in it, here or on the nodes sharing its remote counterpart. Never remove a worktree unless the user asks.
- If the MR was already merged, update the execution record and report; don't recreate its branch.

## Execution record

An implemented issue carries one editable comment that says who works on it:

```markdown
<!-- coder-execution-record -->
### Execution record

| Field | Value |
|---|---|
| Worktree | <absolute checkout path, or Released (last used: <path>)> |
| Branch | <development branch> |
| MR | <MR URL, or Not opened> |
| Status | active / blocked / needs-human / ready-for-merge / merged / paused, with context |
| Updated | <UTC timestamp> |
```

- Another active worktree owns the issue until it is released or the user reassigns it.
- Create or edit it with `glab api` (or `gh`) when you claim the task, open the MR, get blocked, reach `ready-for-merge` or `merged`, or release the worktree. Keep one record per issue and never overwrite another coder's.

## Implement and validate

- For features and fixes: update docs → write a minimal failing test → implement → check that tests, code and docs agree. When tests run remotely, validate the failing test there before the fix.
- Expected results come from a specification, known example or independent reference.

## Deliver and review

Push the branch and open the MR with the project's template: behavior, issue
links, validation evidence and limitations. Use a closing reference only when the
MR completes the issue.

Then review it yourself:

1. Round 0: in the clean checkout at the MR source commit, run `codex review --base <target-sha> < /dev/null > <run_dir>/review-0.md 2> <run_dir>/review-0.log` (minutes; run it in the background). Separately check the change against the issue's requirements, which `codex review` does not see.
2. A pass means the requirements are met with evidence, no actionable finding is left and the checks pass on the current commit. Weigh each finding against KISS: fix real defects in scope with the smallest change; reject style preferences and findings about rare or hypothetical cases nobody asked for, with a one-line reason in the MR.
3. Otherwise fix, push, rerun affected checks and review again: at most three corrective rounds. If round 3 still fails, stop, set `needs-human` and report what remains. After that, follow the user's feedback; further automatic rounds need their explicit allowance.
4. Record each round's commit, checks and outcome in a review-status section of the MR description, so that the count survives interruptions. A later merge recheck uses the remaining rounds and never resets them.

A standalone review the user requests uses a detached checkout at the MR's source
commit, the same command, and a verdict in chat; post it to the MR only when asked.

## Merge, only when the user asks

- Recheck the MR, its source SHA and the current target. If either moved since the passing review, reassess what changed, using a remaining round if a new review is needed.
- Merge with the reviewed SHA as a guard: `glab mr merge <iid> --sha <sha>` or `gh pr merge <n> --merge --match-head-commit <sha>`. While a pipeline runs, `glab` schedules an auto-merge instead: wait until the MR shows merged before the next step. After an error or timeout, read the MR and target back before retrying. A 504 can still merge: if the target already holds a merge of the reviewed SHA while the MR stays open, close the MR with a note naming that commit instead of merging again.
- If the forge's rebase leaves a checkout diverged only by that rebase, rename its old branch to an archive name with `git branch -m` and recreate the branch at the new SHA.
- Confirm the merge commit, then set the execution record to `merged` and delete the merged source branch on the forge.
