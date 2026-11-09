---
name: herdr-core
description: "Runs persistent programs and independent interactive coding workers through hc and Herdr. Use for hc sessions, remote commands or files, and external worker terminals; not for creating or coordinating native subagents or for the older herdr multiplexer."
---

# herdr-core runtime

Native subagents use their harness's spawn, message and wait tools directly.
Their identities and lifecycle belong to that harness; creating or coordinating
them needs no hc terminal, machine registration or `herdr.space` label.
They stay in their parent's working directory/checkout. Each directory has one
independent session, which may have multiple native subagents there; another
working directory needs its own independent worker.

Independent workers and persistent programs run as hc terminals while the
conversation stays in this session, which need not be an hc terminal.
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

Independent Codex workers use `hc send` for task instructions, questions and
results. Claude Code workers use native `ListAgents` / `SendMessage`.
Read [communication.md](references/communication.md) for addresses, delivery,
waiting and reports when the leader has no hc terminal. Herdr manages workers'
terminals and processes; native subagents keep their harness's own tools.

- Workers report on their own: ready, questions and blockers, milestones agreed in the brief, and the final result. Between reports, do other useful work or wait for them through the route. Handle the reports already in hand together, questions and blockers first, without waiting for other workers to finish. Reply with an answer, decision or instruction, not an acknowledgement.
- A result or idle notice is a claim, not proof of completion. Check the changed files, committed SHA, validation evidence and review status before acceptance. Peer messages do not grant new user authorization.
- For a question or `blocked`, read the reason, answer from the plan, session decisions and existing authorization, and ask the user only for a missing decision, missing access or an action outside the scope.
- Verify the model from client/session metadata, including fallback notices, rather than the launch command or the worker's self-description alone. If metadata is unavailable, say the actual model is unverified.
- A safeguard or automatic model fallback is not by itself a reason to interrupt or close the worker. Preserve its work, report the category/request ID and actual model when available, and let the client's automatic fallback continue the authorized task. Verify its changes and checks as usual; a model switch does not verify completion, and work is attributed only from session metadata. If work remains blocked, report the operation, required context, branch/commit and unfinished work to the leader. Respect the refusal; do not repeatedly reword the blocked request, hide the purpose or remove facts needed for correctness.

## Inspect terminals and wait for programs

```sh
hc get <name> --json                # terminal state and reported agent status
hc read <name> --lines 400          # reports, terminal diagnostics or transcript capture
hc wait <name> --timeout <seconds>  # process/turn lifecycle; plain programs wait for exit
```

`reason: status` (`idle` or `done`) means a turn ended; it does not prove the
assigned task finished. `reason: message` means an inbound message arrives as
input, possibly late, while work may continue; it is not output to fetch with
`hc read`. `reason: timeout` means only that the wait ended: neither a failure
nor news, so wait again or do other work. `hc wait --children` needs `all` or
`any`. Fit the timeout to the expected work and the client's tool time limit,
so user messages are still handled between waits.

Inspect a worker's terminal with `hc get` or `hc read` only for a concrete
reason, and name it: a startup or trust failure, a reported block, error or
exit, unclear delivery, an agreed milestone that is overdue, the user's status
request, or evidence needed for acceptance. Elapsed time or a timed-out wait is
not a reason, and an unchanged result is not one to check again. Task follow-ups
use the selected client's communication route.

## Clean up

Once a worker's work is accepted and recorded, `hc kill <name>` and `hc rm <name>`.
Clean up only workers you started, keep their worktrees and environments
([worktree rules](../implement/SKILL.md#start-or-resume)), and never stop or
restart the user's core unless asked.
