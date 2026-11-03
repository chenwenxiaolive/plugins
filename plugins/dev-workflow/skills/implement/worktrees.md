# Worktrees, branches and issue execution records

Checkout paths, remote counterparts and synchronization follow
[remote-workflow.md](../gpu-cluster/remote-workflow.md); this file covers which
task a worktree serves and how that is recorded.

## Reusing worktrees for issues and MR review
- Worktree names may identify stable working directories such as `dev-1`, `dev-2`, `dev-3` and `review`. Each can serve successive issues/MRs without renaming the directory. Create a stable-named worktree with Git from the target branch's fetched commit: `git fetch origin && git worktree add --no-track -b <branch> /volume/worktree/<repo>/<name> origin/<target>`, then push it with `git push -u origin <branch>`. The Herdr app's New worktree instead names the folder after the branch, under `~/.herdr/worktrees/<repo>/` (a link to `/volume/worktree/<repo>/` on this machine), and branches from the current HEAD.
- On assignment or resumption, read the relevant issue, MR description, current diff and latest review discussions when present. Continue the same issue/MR on its existing development branch. Assignment to another issue authorizes creating or switching to its branch in this worktree without another confirmation. Base an independent issue's new branch on the intended target branch's current fetched commit; use an unmerged task branch as the base only for an explicitly intended dependency.
- Handle one active task per worktree. Before switching a checkout to another issue/MR, require a clean working tree, commit and push the outgoing task's changes, and confirm that no other agent or running command uses that checkout: run [checkout.py](../gpu-cluster/scripts/checkout.py) `busy <node>` from it, which lists processes working in the checkout here and on every machine sharing that node's `/volume` (without a node, only here). It skips its own ancestors; judge every other listed process, since your own session's helpers, such as the Codex plugin's app-server broker, can appear. hc's `cwd` field can be stale. Check an existing remote counterpart's working tree too before changing it. Preserve unexpected changes and investigate branch occupancy instead of forcing a switch.
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
the marker below with [scripts/issue_record.py](scripts/issue_record.py), run
from the checkout so `glab` infers the project. Creating and updating this record
is part of the authorized implementation task. Read
[gitlab.md](../gpu-cluster/gitlab.md) before accessing GitLab. A task without an
issue does not require creating one solely for tracking. The script is
GitLab-only; on GitHub keep the same comment format with `gh`.

- Before coding or resuming, run `issue_record.py show <iid>` and compare its records with the actual checkout, branch and MR. It reads every comment page and prints the records, the comment count, the remote `issue-<iid>-*` branches plus any branch a record names, and local worktrees on such branches, pushed or not.
- `issue_record.py set <iid> --worktree <path> --branch <branch> --status active` creates the record when none exists or updates the single existing one in place; later updates pass only what changed, such as `--mr <url>` or `--status ready-for-merge`. It keeps the other fields, stamps Updated and reads the saved note back. It refuses when several records exist, when another active worktree holds the record (pass `--takeover` only for an explicit reassignment), or when the note changed during the edit. Resolve such conflicts instead of overwriting them; do not delete another coder's record.
- **Read that record before naming an issue as available, not only before starting it**: recommending what to work on next, calling an issue unclaimed, or listing open work all assert that nobody owns it. Reading the issue body answers the technical question, not the ownership one: run `issue_record.py show <iid>`, which reports the record and the branch and worktree occupancy. Its branch search matches the full `issue-<iid>-` prefix, so issue 42 does not match issue 142, and it also checks the branch a record names; an empty branch search alone does not establish that an issue is unowned. Report an owned issue as owned, with its worktree and status, instead of proposing it.
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
- Before reusing the worktree for another issue, release the outgoing issue's record with `issue_record.py set <iid> --release --status <actual status>`: Worktree becomes `Released (last used: <path>)` and its branch and MR links stay. Use `paused` with the remaining work if an unfinished task is being set aside. On resumption or handoff, update the same record to the new actual checkout after the ownership and reuse checks.
- If a write fails or times out, run `show` before retrying so a successful creation is not duplicated. Report an unresolved tracking failure rather than claiming the record is current.
