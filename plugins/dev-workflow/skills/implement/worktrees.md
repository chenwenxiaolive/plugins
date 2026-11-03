# Worktrees, branches and issue execution records

Checkout paths, remote counterparts and synchronization follow
[remote-workflow.md](../gpu-cluster/remote-workflow.md); this file covers which
task a worktree serves and how that is recorded.

## Reusing worktrees for issues and MR review
- Worktree names may identify stable working directories such as `dev-1`, `dev-2`, `dev-3` and `review`. Each can serve successive issues/MRs without renaming the directory. Create a stable-named worktree with Git from the target branch's fetched commit: `git fetch origin && git worktree add --no-track -b <branch> /volume/worktree/<repo>/<name> origin/<target>`, then push it with `git push -u origin <branch>`. The Herdr app's New worktree instead names the folder after the branch, under `~/.herdr/worktrees/<repo>/` (a link to `/volume/worktree/<repo>/` on this machine), and branches from the current HEAD.
- On assignment or resumption, read the relevant issue, MR description, current diff and latest review discussions when present. Continue the same issue/MR on its existing development branch. Assignment to another issue authorizes creating or switching to its branch in this worktree without another confirmation. Base an independent issue's new branch on the intended target branch's current fetched commit; use an unmerged task branch as the base only for an explicitly intended dependency.
- Handle one active task per worktree. Before switching a checkout to another issue/MR, require a clean working tree, commit and push the outgoing task's changes, and confirm that no other agent or running command uses that checkout. Find local ones by their working folder, which the kernel reports with links resolved (`W=<checkout>; for p in /proc/[0-9]*; do c=$(readlink "$p/cwd" 2>/dev/null) && case $c in "$W"|"$W"/*) echo "${p#/proc/} $c";; esac; done`); hc's `cwd` field can be stale. Apply these checks separately to an existing remote counterpart before changing it, including jobs on every node sharing its storage. Preserve unexpected changes and investigate branch occupancy instead of forcing a switch.
- If I explicitly request a standalone review in a separate worktree, use detached HEAD at the MR's exact source commit so the development branch remains available, and preserve any existing review worktrees. [review.md](review.md#standalone-review) says how to review and what to report.
- Retain local and remote worktrees and their environments after a task finishes. Worktree removal is outside routine workflow cleanup: the user does it manually or explicitly asks the leader to do it. For a requested removal, preserve uncommitted and unmerged work and check that no agent or job uses the affected checkout, including every node sharing a remote counterpart's storage. Releasing an issue's worktree assignment below does not delete its directory.


### Issue branch identity

Name a new branch implementing issue `#K` as
`issue-K-<short-description>`, for example `issue-42-fix-cache` for issue `#42`,
`Fix cache`. Use the issue number without `#`; GitLab uses the project-local
`iid`, not the global issue ID. Summarize the issue in a short English description,
usually 2–4 lowercase words separated by hyphens. Use the `issue-` prefix without
an additional agent prefix or hash suffix.

Resolve the issue in its source repository and use its execution record to track
the actual worktree, branch and MR.
Continue an existing issue/MR on its current branch; this naming rule does not
authorize renaming existing branches or moving stable worktree directories.

## Issue execution record

For an assigned implementation issue, maintain one editable issue comment using
the marker below. Creating and updating this record is part of the authorized
implementation task. Read [gitlab.md](../gpu-cluster/gitlab.md) before accessing GitLab. A task
without an issue does not require creating one solely for tracking.

- Before coding or resuming, read the issue's existing execution record and compare it with the actual checkout, branch and MR. Search all comment pages for the marker; reuse the existing comment by its note ID. Create one only when none exists. Multiple matching records or a conflicting active owner require resolving ownership before proceeding; do not overwrite or delete another coder's record.
- **Read that record before naming an issue as available, not only before starting it**: recommending what to work on next, calling an issue unclaimed, or listing open work all assert that nobody owns it. An issue's comment count is the cheap signal — `glab issue view` prints `comments: N`, and on an issue ready for work a nonzero count is usually an execution record, so reading the body alone answers the technical question and not the ownership one. Branch and worktree occupancy are the second signal (`git worktree list`, `git ls-remote --heads origin 'refs/heads/issue-<K>-*'`). This pattern matches the full issue prefix, so issue 42 does not match issue 142. For an existing task, inspect the actual branch named in its execution record regardless of naming convention; an empty prefix search does not establish that an issue is unowned. Report an owned issue as owned, with its worktree and status, instead of proposing it.
- Record the selected checkout's full absolute path and the branch actually checked out after the reuse checks. This identifies the current execution even when coders share one GitLab account; it is not a permanent issue-to-worktree assignment or an atomic lock. An old timestamp alone is not permission to take over. An explicit reassignment authorizes a handoff after checking the previous execution and preserving its work.

```markdown
<!-- coder-execution-record -->
### Execution record

| Field | Value |
|---|---|
| Worktree | <absolute checkout path> |
| Branch | <development branch> |
| MR | <MR URL, or Not opened> |
| Status | <overall task status and any blocker or handoff context> |
| Updated | <UTC timestamp> |
```

- Update this same comment when the task is claimed or resumed, its checkout or branch changes, the MR opens, work becomes blocked, it is handed off or stopped, or it reaches `ready-for-merge` or `merged`. Record the information needed to establish ownership, locate the work and act on a blocker; use `active` while implementation or review is in progress. Keep review rounds, findings, fixes and validation evidence in the MR's review-status section; starting another review or corrective round alone does not require an issue update. A failed third corrective round is `needs-human`; include what needs attention. Use `merged` only after confirming the merge. If a task leaves `ready-for-merge` for further work, update that coarse status so the issue does not imply it is still ready.
- The agent executing an authorized merge owns the final record update. If the user merges in the UI, the next agent reading that task or reusing its worktree reconciles the record with the actual MR under [merge completion](merge.md#record-merge-completion). Check this before labeling the outgoing task paused.
- Before reusing the worktree for another issue, update the outgoing issue's record: mark Worktree as `Released (last used: <path>)`, preserve its branch and MR links, and keep its actual task status. Use `paused` with the remaining work if an unfinished task is being set aside. On resumption or handoff, update the same record to the new actual checkout after the ownership and reuse checks.
- Re-read before editing the comment to detect another coder's update, and verify the saved result. If a write times out, inspect the issue before retrying so a successful creation is not duplicated. Resolve conflicting changes instead of repeatedly overwriting them. Report an unresolved tracking failure rather than claiming the record is current.
