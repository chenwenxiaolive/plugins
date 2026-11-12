---
name: leader
description: "Plans parallel development work, splits it into independent single-issue tasks and launches one Herdr worker for each. Runs only when the user invokes it."
disable-model-invocation: true
---

# Leader

You plan the work, split it, and launch one independent worker per piece.
Launching is the whole task: report which workers run, where and on what, then
end your turn. Later work on the same project is a new invocation, not a
continuation of this session.

A worker is an independent interactive CLI session launched through Herdr, with
its own checkout, branch and MR. Workers report to the user in their own
terminals, which the user watches and steers in Herdr. Nothing reports to you:
do not wait for workers, ask for progress, read their terminals, verify their
results, integrate their commits or merge their MRs. Act on a report that
reaches you anyway only by passing it to the user. You need no hc terminal of
your own, and you do not implement any part of the work yourself.

Keep the current harness, model and reasoning effort. Workers inherit them
unless the user explicitly chooses otherwise: a Claude Code leader starts Claude
Code workers, a Codex leader starts Codex workers. An explicit request for a
model in another harness overrides that default; preserve the choice instead of
switching the leader or starting another leadership session.

## Plan and split

- Establish the task goals, acceptance criteria and known dependencies before launching. Leave task-local investigation and implementation decisions to each worker.
- Give each worker one issue and the complete change it implies. The worker chooses which files to read, change or create to meet that goal; do not assign an owned-file list.
- Split by independent outcomes and interface contracts. Shared file paths alone do not make tasks dependent; coupled behavior or a shared design decision belongs in one task or sequenced tasks.
- Launch only work that can start now. When a task needs another task's commits, launch the first and tell the user the second is sequenced behind it; no one is coordinating the handover.
- Give each worker its own GPUs, or a whole node when its validation needs one; never the same GPUs to two workers.
- Explain the split briefly, then launch the independent tasks. A worker grows to about 500 MB (measured 2026-11-02) and a fresh one doesn't show in `free -m` yet, so launch in batches that keep about 500 MB available.

## Prepare a worktree per issue

Each worker gets one issue, one worktree and one branch, and keeps them for that
issue alone. Create the worktree and its branch at
`/volume/worktree/<repo>/issue-<iid>`, or named for the task when it has no
issue, under implement's
[branch and worktree rules](../implement/SKILL.md#start-or-resume) before
launching, and pass it as the worker's `--cwd`; say in the brief that the
checkout is ready, so the worker does not create it again; a worker that changes no
repository files, such as a deployment, gets its own directory too and names the
remote paths it needs in its brief instead of working in them. Invoking this
skill authorizes creating those worktrees and branches. The first build in a new
remote counterpart is slow, and the worker sets it up when its checks need it.

## Brief each worker

Each worker reads its task and its issue, not this skill. Build the assignment
from [delegation-brief.md](delegation-brief.md), and send the assignment with the
facts it needs, not this conversation or unrelated project documents. Always name
the target branch: project docs may say `main` while this work goes into a feature
branch. Claude Code keeps memory per repository, so workers would write into
yours; record what is worth keeping yourself.

Launch through [herdr-core](../herdr-core/SKILL.md#start-a-worker), confirming
each worker started and cleared any trust prompt. If a launch fails, report that
to the user rather than taking its task yourself.
