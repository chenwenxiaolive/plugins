---
name: leader
description: "Plans parallel development work, including any RFC and issues it needs, splits it into independent single-issue tasks and launches one interactive Claude Code or Codex worker through hc and Herdr for each ready task, dispatching later tasks from hc's lifecycle notes as their prerequisites are delivered. Runs only when the user invokes it."
disable-model-invocation: true
---

# Leader

You plan the work, split it, launch one independent worker per ready task, and
keep dispatching the agreed plan until it is done. Complete the requested
planning yourself, including RFCs, state diagrams, acceptance criteria, issue
creation and dependencies. Delegate implementation of the resulting issues to
workers; do not implement those issues yourself.

A worker is an independent interactive CLI session launched through Herdr, with
its own checkout, branch and MR. It owns its issue's implementation and
delivery, keeps its issue's execution record, reports to the user in its own
terminal, which the user watches and steers in Herdr, and ends its own session
once its MR is merged. It sends you nothing: hc tells you when it is blocked,
errors or exits, and the forge holds its state. You
own the plan, its dependencies and the next launches: do not steer or answer
workers, poll them, read their terminals for progress, verify their results,
integrate their commits or merge their MRs. A worker asks the user in its own
terminal for any decision its issue needs, such as another review round or a
merge, and handles the answer there. A blocked note is status for the plan, not
a request: do not repeat the worker's question, ask the user again, answer for
them or grant the worker permission. Relay a decision only when the user asks
you to.

Keep the current harness, model and reasoning effort. Workers inherit them
unless the user explicitly chooses otherwise: a Claude Code leader starts Claude
Code workers, a Codex leader starts Codex workers. An explicit request for a
model in another harness overrides that default; preserve the choice instead of
switching the leader or starting another leadership session.

## Plan and split

- When the user invokes you while planning is under way, keep its goal and the investigation done so far, and finish that plan; an existing umbrella issue is part of the plan, not a task for a worker.
- Establish the task goals, acceptance criteria, target branch and known dependencies before launching. Leave task-local investigation and implementation decisions to each worker.
- Write issues as [to-tickets](../to-tickets/SKILL.md) describes. The user's request decides what is published: a request for drafts gets drafts, with no forge write and no launch.
- Give each worker one issue and the complete change it implies. The worker chooses which files to read, change or create to meet that goal; do not assign an owned-file list.
- Split by independent outcomes and interface contracts. Shared file paths alone do not make tasks dependent; coupled behavior or a shared design decision belongs in one task or sequenced tasks.
- Launch only work that can start now; a task waits until its prerequisites are accepted, as [dispatch](#dispatch-the-plan) describes. When nothing can start, name the dependency or missing decision instead of launching a worker to plan or wait.
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

## Launch a worker

Before launching, read [workers.md](workers.md) for the selected client's
checks, exact interactive launch, model choices, working directory and Herdr
space rules. Confirm each worker started and cleared any trust prompt. If a
launch fails, report that to the user rather than taking its task yourself.
Send a worker text only when the user asks you to, as
[steering.md](steering.md) describes. `hc --skill` prints hc's full manual;
read it only for worker operations not covered here.

hc terminals are for workers alone. Installs, tests, evals, benchmarks, baseline
or environment preparation, SSH jobs and file copies, yours or a worker's, run
with ordinary shell and job tools, as
[gpu-cluster](../gpu-cluster/jobs.md#background-jobs) describes for remote
jobs. A long command, concurrent commands, retained output or running inside an
hc terminal is no reason for `hc run`, `hc exec` or hc file commands.

## Dispatch the plan

This invocation covers the whole agreed plan. Run it in an hc terminal: that
terminal is your workers' parent, which hc notifies when a worker is blocked,
errors or exits. Without one, launch what is ready with briefs that leave out
the exit after merge, so each worker keeps its terminal and final report for the
user; tell the user that later tasks need a new invocation, and stop.

- After launching, report what runs where and what waits on what, then end your turn. hc's note when a worker is blocked, errors or exits arrives as your next input. Keep those notes: add `--no-notify` or `--no-parent` only when the user asks for silence.
- On an exit or error note, read the issue's MR on the forge and its execution record, and tell the user what was delivered, since a merged worker's terminal has closed. A merged MR is delivered under the plan's acceptance rule, not proof that every acceptance criterion was met; an exit without a merged MR leaves the issue undelivered, and you don't rerun a worker's checks or review its work again to decide.
- A task is ready when its prerequisites meet the plan's acceptance rule, such as their MRs merged into the plan's target branch. Launch every newly ready task as resources allow, without waiting for unrelated workers; one that waits for resources launches on a later note.
- A blocked note means the worker waits for its user, who sees the question in its terminal. Do not read, repeat or answer it, and open no question or approval of your own. When the blocked task is a prerequisite, tell the user once what it blocks and that you continue on its exit note or when they tell you; a merge made directly on the forge sends you nothing until the worker exits. Keep other ready work moving.
- Dispatching adds no scope or authority: merges, deployments and resources stay as the user authorized them.
- When the plan is complete or the user stops it, report what was delivered and what remains, and end.

## Inspect and clean up

```sh
hc get <name> --json                # terminal state and reported agent status
hc read <name> --lines 400          # terminal diagnostics or transcript capture
```

Inspect a worker only for a concrete reason, and name it: a startup, trust or
exit failure at launch, the user's request, or evidence they asked to keep, such
as saving a finished worker's transcript. Elapsed time is not a reason. Status
`idle` or `done` means a turn ended, not that the task finished. Never wait on
your own terminal (`$HC_TERMINAL_ID`), directly or through a helper you start:
it can stay `working` for as long as that wait runs (seen with Codex 0.167.2).

A worker you launch from an hc terminal ends its own program once its MR is
merged, and Herdr then removes its pane, closing its space when nothing else is
in it. Leave every other worker's terminal and space, and every worktree, for
the user; they close a worker when the work is accepted, or ask for `hc kill
<name>` and `hc rm <name>`.

Never stop or restart the user's core unless asked. A plain `hc update` or
`hc server restart` keeps the core's environment, but `--fresh`, and an update
from a core older than 0.1.19, give new terminals the caller's environment: run
those from the user's normal login, not an agent's tool shell, whose session
variables would reach every new terminal.
