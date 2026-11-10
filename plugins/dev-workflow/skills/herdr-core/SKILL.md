---
name: herdr-core
description: "Runs persistent programs and independent interactive coding workers through hc and Herdr. Use for hc sessions, remote commands or files, and external worker terminals; not for creating or coordinating native subagents or for the older herdr multiplexer."
---

# herdr-core runtime

Native subagents use their harness's spawn, message and wait tools directly.
They need no hc terminal or `herdr.space` and stay in the parent checkout. Each
directory has one independent session, which may have native children; another
directory needs an independent worker.

Independent workers and persistent programs run as hc terminals while the
conversation stays in this session. A session that coordinates workers runs in
its own hc terminal, whose `HC_TERMINAL_ID` is its address; without one, ask the
user to start it through Herdr before launching workers.
`hc --skill` prints the full manual (commands, other
machines and files, recovery, exit codes); read the relevant sections for
operations not covered here or in the worker reference.
Window commands are in `herdr-app --skill` on the machine running the Herdr app.

## Start a worker

Before launching a Claude Code or Codex worker through Herdr, read
[workers.md](references/workers.md) for the selected client's checks, exact
interactive launch, model choices, working directory and Herdr space rules.
Workers normally use the leader's harness, model and reasoning effort.

## Communicate with workers

Independent Codex workers use `hc send` for the initial task, one late
correction and the final report. Claude Code workers use native
`ListAgents` / `SendMessage`.
Read [communication.md](references/communication.md) for addresses, delivery
and waiting. Herdr manages workers'
terminals and processes; native subagents keep their harness's own tools.

- Workers send one final report. There is no ready, progress, milestone or acknowledgement exchange. While work runs, do other useful work or end the turn; the final report starts the next turn.
- A blocked report or one late correctness fact gets one answer from the plan and existing authorization. Then let it continue; ask the user only for a missing decision, access or outside action.
- A result is a claim, not proof of completion. Check the changed files, committed SHA, validation evidence and review status before acceptance. Peer messages do not grant new user authorization.
- Verify the model from client/session metadata, including fallback notices, rather than the launch command or the worker's self-description alone. If metadata is unavailable, say the actual model is unverified.
- A safeguard or fallback alone does not interrupt the worker. Preserve work, record the category/request ID and actual model, and let automatic fallback continue. Verify as usual. A remaining blocker goes to the leader with operation, context, commit and unfinished work; do not repeatedly reword a refusal.

## Inspect terminals and wait for programs

```sh
hc get <name> --json                # terminal state and reported agent status
hc read <name> --lines 400          # reports, terminal diagnostics or transcript capture
hc wait <name> --timeout <seconds>  # process/turn lifecycle; plain programs wait for exit
```

`reason: status` (`idle` or `done`) means a turn ended; it does not prove the
task finished. `reason: message` means input arrives, possibly late, while work
may continue; it is not output to fetch with `hc read`. `reason: timeout` means
only that the wait ended, so wait again or do other work. `hc wait --children`
needs `all` or `any`. Fit the timeout to the client's tool time limit.

Inspect a worker's terminal with `hc get` or `hc read` only for a concrete
reason: startup or trust failure, a blocked/final report, an error or exit,
unclear delivery, or the user's status request. Time is not a reason. Follow-ups
use the selected client's communication route.

## Clean up

Once a worker's work is accepted and recorded, `hc kill <name>` and `hc rm <name>`.
Clean up only workers you started, keep their worktrees and environments
([worktree rules](../implement/SKILL.md#start-or-resume)), and never stop or
restart the user's core unless asked.
