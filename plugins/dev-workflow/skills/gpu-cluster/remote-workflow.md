# Remote workflow: checkouts, Git synchronization and validation

<!-- Moved from ~/.claude/CLAUDE.md on 2026-10-16; the always-loaded rules there still apply. -->

## Formatting a local file with a node's tools

- Project formatters and linters therefore run from the node checkout's environment. To check a local file before committing, pipe it through that environment's tools, in the order the project's own format script or pre-commit config runs them, passing the file name so each tool finds the project's configuration. For example, for a project that formats with isort and black and lints with ruff: `ssh sh-0 "cd -- <checkout> && .venv/bin/isort --filename <path> - | .venv/bin/black -q --stdin-filename <path> - | .venv/bin/ruff check --fix --quiet --stdin-filename <path> -" < <path>`. Choose the node for the task's cluster. The node checkout must be on a commit with the same formatter configuration and its environment synced to that commit's lock.

## Project paths and instruction loading
- **Use the same absolute checkout path locally and remotely**: main project checkouts normally use `/volume/workspace/<project>[/<checkout>]`; herdr worktrees and their remote counterparts use `/volume/worktree/<repo>/<worktree-name>`. Start Codex or Claude Code in that real local Git checkout. The local directory contains the source code and its Git metadata or a `.git` file pointing to it.
- Work only in the checkout I select. Starting a task in herdr selects that checkout; its branch follows the assigned issue/MR. Verify the repository identity, current branch or detached HEAD, and identical local/remote absolute path from Git and the selected checkout. Create a missing remote counterpart only as authorized below; other extra checkouts and migrations require my request.
- Read applicable local project instructions before editing: `AGENTS.override.md` takes precedence over `AGENTS.md` in the same directory; also read applicable `CLAUDE.md`, `CLAUDE.local.md`, and their referenced guidance. Follow nested instructions in the scope of the files being changed.
- Before the first remote operation for a task, read any project instruction files that exist in the remote checkout, from its root down to the working subdirectory (`/volume/cluster-ops` for ops work). Read remote-only operational guidance and resolve references relative to their instruction file. This global Git workflow supersedes the obsolete editing/placeholder rules (see machines.md).
- Confirm both local and remote repository identity, branch, HEAD, and working-tree state before synchronization. After resume or compaction, reload required instructions missing from context. Re-check state before acting; startup snapshots are not current state.
- Outside the selected `/volume` project path, perform local configuration/ops work or preparatory inspection. Ask for the intended matching path before starting project development there; do not silently select a different checkout.

## Reusing worktrees for issues and MR review
- Worktree names may identify stable working directories such as `dev-1`, `dev-2`, `dev-3` and `review`. Each can serve successive issues/MRs without renaming the directory. Create a stable-named worktree with Git from the target branch's fetched commit: `git fetch origin && git worktree add --no-track -b <branch> /volume/worktree/<repo>/<name> origin/<target>`, then push it with `git push -u origin <branch>`. The Herdr app's New worktree instead names the folder after the branch, under `~/.herdr/worktrees/<repo>/` (a link to `/volume/worktree/<repo>/` on this machine), and branches from the current HEAD.
- On assignment or resumption, read the relevant issue, MR description, current diff and latest review discussions when present. Continue the same issue/MR on its existing development branch. Assignment to another issue authorizes creating or switching to its branch in this worktree without another confirmation. Base an independent issue's new branch on the intended target branch's current fetched commit; use an unmerged task branch as the base only for an explicitly intended dependency.
- Handle one active task per worktree. Before switching a checkout to another issue/MR, require a clean working tree, commit and push the outgoing task's changes, and confirm that no other agent or running command uses that checkout. Find local ones by their working folder, which the kernel reports with links resolved (`W=<checkout>; for p in /proc/[0-9]*; do c=$(readlink "$p/cwd" 2>/dev/null) && case $c in "$W"|"$W"/*) echo "${p#/proc/} $c";; esac; done`); hc's `cwd` field can be stale. Apply these checks separately to an existing remote counterpart before changing it, including jobs on every node sharing its storage. Preserve unexpected changes and investigate branch occupancy instead of forcing a switch.
- The coder reviews its own MR on its existing development branch under the bounded loop below. If I explicitly request a standalone review in a separate worktree, use detached HEAD at the MR's exact source commit so the development branch remains available. Preserve any existing review worktrees.
- When I later ask for changes based on human feedback, read the latest discussions and source commit and continue on the MR's development branch. After the automatic round limit, follow my specific instructions; resume automatic rounds only with an explicit new allowance.

### Issue branch identity

Name a new branch implementing issue `#K` as
`K-<short-description>`, for example `42-fix-cache` for issue `#42`,
`Fix cache`. Use the issue number without `#`; GitLab uses the project-local
`iid`, not the global issue ID. Summarize the issue in a short English description,
usually 2–4 lowercase words separated by hyphens. Do not add an `agent/` prefix
or a hash suffix.

Resolve the issue in its source repository and use its execution record to track
the actual worktree, branch and MR.
Continue an existing issue/MR on its current branch; this naming rule does not
authorize renaming existing branches or moving stable worktree directories.

## Issue execution record

For an assigned implementation issue, maintain one editable issue comment using
the marker below. Creating and updating this record is part of the authorized
implementation task. Read [gitlab.md](gitlab.md) before accessing GitLab. A task
without an issue does not require creating one solely for tracking.

- Before coding or resuming, read the issue's existing execution record and compare it with the actual checkout, branch and MR. Search all comment pages for the marker; reuse the existing comment by its note ID. Create one only when none exists. Multiple matching records or a conflicting active owner require resolving ownership before proceeding; do not overwrite or delete another coder's record.
- **Read that record before naming an issue as available, not only before starting it**: recommending what to work on next, calling an issue unclaimed, or listing open work all assert that nobody owns it. An issue's comment count is the cheap signal — `glab issue view` prints `comments: N`, and on a `ready-for-agent` issue a nonzero count is usually an execution record, so reading the body alone answers the technical question and not the ownership one. Branch and worktree occupancy are the second signal (`git worktree list`, `git ls-remote --heads origin | grep '<K>-'`). Report an owned issue as owned, with its worktree and status, instead of proposing it.
- Record the selected checkout's full absolute path and the branch actually checked out after the reuse checks. This identifies the current execution even when coders share one GitLab account; it is not a permanent issue-to-worktree assignment or an atomic lock. An old timestamp alone is not permission to take over. An explicit reassignment authorizes a handoff after checking the previous execution and preserving its work.

```markdown
<!-- coder-execution-record -->
### Execution record

| Field | Value |
|---|---|
| Worktree | <absolute checkout path> |
| Branch | <development branch> |
| MR | <MR URL, or Not opened> |
| Status | <current phase and any blocker or handoff context> |
| Updated | <UTC timestamp> |
```

- Update this same comment when implementation starts, the MR opens, review or a corrective round starts, work becomes blocked, or the task stops. Use factual statuses such as `implementing`, `reviewing`, `blocked`, `paused`, `needs-human`, `ready-for-merge` and `merged`. On a blocker or failed third corrective round, include what needs human attention. A passed review means `ready-for-merge`; use `merged` only after confirming the MR was merged. The MR's review-status section remains authoritative for round counts, findings and validation evidence.
- The agent executing an authorized merge owns the final record update. If the user merges in the UI, the next agent reading that task or reusing its worktree reconciles the record with the actual MR under [merge completion](merge-workflow.md#record-merge-completion). Check this before labeling the outgoing task paused.
- Before reusing the worktree for another issue, update the outgoing issue's record: mark Worktree as `Released (last used: <path>)`, preserve its branch and MR links, and keep its actual task status. Use `paused` with the remaining work if an unfinished task is being set aside. On resumption or handoff, update the same record to the new actual checkout after the ownership and reuse checks.
- Re-read before editing the comment to detect another coder's update, and verify the saved result. If a write times out, inspect the issue before retrying so a successful creation is not duplicated. Resolve conflicting changes instead of repeatedly overwriting them. Report an unresolved tracking failure rather than claiming the record is current.

## Coder-owned review after opening an MR

The coder owns implementation, MR creation, review and fixes in the selected
development worktree. Run this workflow as part of the implementation task,
without a separate reviewer role, review worktree, notification or polling step.

1. Complete the implementation, commit and push it, run the required checks on the committed code, and open the MR. Read the issue/spec and project standards. Fetch and record the MR source SHA, target SHA and merge-base; verify that the clean local HEAD is the MR source commit. Review the entire MR diff against that baseline, even when the working tree is clean.
2. Run the initial review, recording it as round 0. For this pass and every re-review, assess requirement acceptance as described below and perform code review through the following route:
   - **Claude Code:** invoke `/codex:review --wait --scope branch --base <target-sha>`. The installed command is review-only; wait for and retain its result, then continue the surrounding coder workflow to make fixes. Its return-only instructions apply to the review invocation, not to ending this user-authorized implementation workflow.
   - **Codex:** review the pinned MR diff directly in the current session against the issue/spec, project standards, correctness and regression risks. Keep the review assessment separate from the subsequent edits.
3. If changes are needed, perform at most **three corrective rounds, numbered 1, 2 and 3**. Each round is: address the findings → commit and push any fixes → synchronize and rerun the affected required checks under the validation rules → reassess requirement acceptance and re-review the full updated MR diff through the same tool/agent route. Requirement gaps and code-review findings share this round budget. Refresh and record the source SHA and baseline for each review. The initial review is separate, so the maximum is four review passes in total.
4. A pass requires every in-scope acceptance criterion to be evidenced as met, a completed code review with no unresolved actionable findings, and the required checks passing on the current source SHA. Distinguish optional suggestions from defects and explain any rejected finding with evidence; unresolved disputed findings need human handling. Missing tools, an incomplete assessment/review or failed checks are not a pass. If review or validation cannot run, report the blocker and stop rather than silently substituting a different review route.
5. Stop early when a review passes. If the re-review after corrective round 3 still does not pass, stop automated edits and reviews and wait for human handling. Preserve the branch and MR; report the MR link, reviewed SHA, round count, unmet or unverified criteria, remaining findings and check failures. Do not start round 4, reset the counter on resume, or treat review success as permission to merge.

Record each pass's round number, source SHA, baseline, requirement acceptance,
code-review findings, fixes and validation result in the MR description's
review-status section. Updating that section is part
of this workflow. Before starting a corrective round, record its number and mark
it in progress; after an interruption, continue that round rather than restarting
the count. Keep the status current before ending a turn, and update the issue's
[execution record](#issue-execution-record) to match the current phase or outcome.
Use the run artifact directory for detailed logs.

An authorized merge follows [merge-workflow.md](merge-workflow.md). Any fresh full
review needed there consumes the next remaining corrective round, including when
the change came from a server rebase or the target branch. Do not reset the count
or add review passes beyond the existing limit.

### Requirement acceptance within each review pass

The coder reads the issue/spec and relevant discussions and checks the implemented
behavior against the agreed scope, including requirements outside formal
checkboxes. When there is no issue, use the agreed task. Distinguish this MR's
scope from a larger parent issue. On resume or a scope change, refresh the source
material and preserve the user's agreed requirements.

In the MR's review-status section, map each criterion to its implementation and
evidence for the reviewed source SHA:

| Criterion and source | Implementation | Validation evidence | Result |
|---|---|---|---|
| Agreed behavior and its issue/spec reference | Relevant file, symbol or change | Test, measurement or inspection result; command and artifact link where applicable | met / unmet / unverified |

Choose evidence appropriate to the criterion. A passing unrelated test, the
existence of code, or a review reporting no findings does not establish acceptance.
Missing behavior is `unmet`; behavior that has not been adequately checked is
`unverified`. Resolve material ambiguity with the user instead of inventing a
requirement or weakening one to obtain a pass.

Keep this assessment distinct from code review. Claude Code's `codex:review`
receives the Git review target; do not assume it receives the current conversation
or issue contents. The coder therefore owns the requirement assessment in
addition to invoking the plugin. Codex records the same assessment alongside its
direct code review. Reuse evidence only while it remains valid for the current
commit and scope, under the existing validation rules.

## Creating a remote counterpart for a herdr worktree
- When I request remote testing for a selected herdr worktree, creating its missing remote counterpart at the identical absolute path is authorized without another confirmation. This includes the necessary parent directories on the task's cluster. GPU jobs still require the node I name and free GPUs.
- Inspect the destination before creating anything. If it exists, verify its repository, current task, branch or detached HEAD, full SHA, working-tree state, and use by jobs across the cluster. Reuse it under the rules above; investigate a different repository or unexpected state instead of replacing it.
- Create the counterpart through Git: add a worktree from a verified remote clone of the same repository without switching or changing that clone's working tree, or clone the verified repository directly into the selected destination. Keep Git metadata native to each machine; a linked worktree's `.git` file must reference its remote repository. Synchronize the selected task's committed SHA through Git and match the local branch or detached HEAD. The coder's MR review uses its development branch; detached HEAD is for an explicitly requested standalone review.
- Bootstrap commands may operate from the verified remote source repository or the destination's parent while the target does not yet exist. Once it exists, read its applicable instructions and use the identical local/remote checkout path for every project command. Finish setup with the exact committed SHA, a clean checkout, and the environment required for validation; the synchronization and job checks below still apply.

## Development and Git synchronization
- The local checkout is the primary place for source edits. Remote checkouts are for execution and validation. Avoid editing the same source files independently on both sides.
- Use a clearly identified development branch for each task. Preserve existing work and commit only this task's changes. For an authorized development task, normal phase commits and pushes to the intended development branch are part of synchronization; do not ask for approval again for each sync. Do not push directly to main/master, force-push, or rewrite shared history unless I request it. For a requested merge, use [merge-workflow.md](merge-workflow.md) to check the current source and target, handle any authorized server-side rebase, and validate its result.
- Synchronize a coherent, testable batch of changes, not each file save: review the local diff → commit → record the full commit SHA → push the development branch → update the remote checkout → verify the exact SHA → run the relevant checks remotely.
- Before the first push, verify the intended Git remote, branch, and available authentication. Resolve authentication through the normal login/credential flow without printing secrets. A successful clone alone does not prove push access.
- Before changing the remote checkout, check its branch and all uncommitted/untracked changes, and confirm that no running job on any node still depends on that checkout. Use task launch records and process checks as needed. Do not update a checkout while a job is using it.
- In a clean, idle, designated remote development checkout, select or create the matching tracking branch as needed and use fast-forward-only updates within that branch. `git pull --ff-only` is suitable when it advances to the intended commit. When precise targeting is needed, fetch the branch and fast-forward to the recorded commit SHA. For another assigned issue, switch branches under the reuse rules above; for an explicitly requested standalone review with detached local HEAD, check out the fetched source SHA with detached HEAD remotely too. If the histories diverge, local changes exist, or HEAD differs from the intended SHA after synchronization, investigate before running tests; never automatically reset, clean, stash, or overwrite existing work to make synchronization succeed.
- When the divergence is verified to come solely from an authorized server-side rebase, use the [history-preserving synchronization procedure](merge-workflow.md#synchronize-an-authorized-server-rebase) in the same checkout. Other divergence still requires investigation.
- **`/volume` is shared within each cluster** (see the machine table in machines.md): updating a given remote checkout once updates it for that cluster's nodes and gate. Do not pull separately on each node of a cluster; a checkout on the other cluster is a separate copy, synchronized through Git. Concurrent jobs requiring different versions need explicitly selected separate checkouts; do not create those implicitly.
- Before validation, verify that the remote checkout is clean, its full HEAD equals the committed local code being validated, and its environment matches the committed lock (for a uv project, `uv sync --locked --dry-run` lists no dependency changes, though the project's own local packages may be rebuilt; sync it only while no job uses the checkout). All changes relevant to the test/review claim must be included in that commit; report unrelated local changes separately. Verify the MR source commit and comparison baseline for reviews.
- For behavior changes, preserve the docs → failing test → minimal implementation → verification sequence. If the failing test requires the remote environment, push and validate the test phase there before implementing the fix locally. Intermediate development commits may be consolidated at merge time according to project conventions; do not rewrite history automatically.
- Associate every result with the tested commit, checkout path, execution node, command, and artifact directory. Further source changes require another commit/sync and re-verification of affected behavior. Generated files or remote edits must be accounted for before claiming a clean test result.
- Keep model weights, datasets, logs, caches, secrets, and temporary run scripts out of synchronization commits. Git is the routine source-code transport; temporary remote run artifacts use the directory rules in jobs.md.

## How to operate remotely
- Use `sh-0` for file/Git operations on the sh cluster, and `zg-0` for the zg cluster when that cluster is part of the task. Their storage is independent; an update on the sh cluster cannot update the zg cluster. **GPU jobs run only on the node I specify**; selecting a node for synchronization is not permission to use its GPUs.
- Run local source operations in the selected real checkout. After the bootstrap exception above, every command acting on the remote project must first `cd` to the checkout's physical path, `pwd -P`, and stop if it fails. In a Herdr app worktree `$PWD` keeps the `~/.herdr/worktrees` link, which the nodes don't have:

  ```bash
  ssh sh-0 "cd -- $(printf %q "$(pwd -P)") && "'git status --short --branch'
  ```

- The single-quoted remote command is not expanded locally. Quote paths and arguments with `printf %q`. If the local shell is outside the project, first move into the selected local project directory before constructing a project command; do not accidentally use `/root` as the remote checkout.
- Read and search source code locally. Use ssh to inspect remote environment details, run state, logs, and checkout status, and to update the checkout through Git.
- Create temporary run directories on the remote with `mktemp` as described in jobs.md. Run scripts and job configuration may be prepared locally and transferred with `scp` or an explicitly quoted ssh stdin command into that run directory. This is for run artifacts; source-code changes are committed locally and transferred through Git.
- After synchronization and before running, verify the remote branch, full HEAD, and working-tree state. After execution, inspect results and any generated changes on the remote.

## Repository and development principles
- Work only in the selected local checkout and its remote counterpart at the same absolute path. Creating a missing remote counterpart under the rule above is allowed; other additional clones or worktrees, repository copies, and switches to another existing checkout require my request.
- When the current directory genuinely cannot accomplish the task, first explain why and which path you intend to use, and wait for my approval before acting. "Isolated work", "easier comparison", and "preserving the old branch" do not count as reasons
- Leave existing worktrees as they are; do not migrate or delete them in passing
- Tests and reviews must target the same committed code state across the selected local and remote checkouts. Before starting, verify the full commit SHA, working-tree state, and comparison baseline; for an MR, also verify its source commit.
  - Remote validation uses the committed snapshot; local changes are not remotely tested until committed, pushed, synchronized, and checked. Any further relevant changes require re-verification.
- Projects are all internal and still under development: use KISS design, keep no backward-compatibility layers, and write no data migrations
- For new features and bug fixes, follow this order: update docs and comments first → write a minimal test that currently fails → write the minimal implementation → finally check that tests, code, and docs are consistent
