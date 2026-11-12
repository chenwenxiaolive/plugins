---
name: herdr-core
description: "Runs persistent programs and independent interactive coding workers through hc and Herdr. Use for hc sessions, remote commands or files, and external worker terminals; not for creating or coordinating native subagents or for the older herdr multiplexer."
---

# herdr-core runtime

Independent workers and persistent programs run as hc terminals while the
conversation stays in this session. Launching a worker needs no hc terminal of
your own: a worker owns its task and reports to the user in its own terminal.
`hc --skill` prints the full manual (commands, other
machines and files, recovery, exit codes); read the relevant sections for
operations not covered here or in the worker reference.
Window commands are in `herdr-app --skill` on the machine running the Herdr app.

## Start a worker

Before launching a Claude Code or Codex worker through Herdr, read
[workers.md](references/workers.md) for the selected client's checks, exact
interactive launch, model choices, working directory and Herdr space rules.
Workers normally use the launching session's harness, model and reasoning effort.

## Workers run on their own

A worker gets its whole task in the launch, owns one issue end to end and
reports to the user in its own terminal. Do not message it, wait for it, poll
it or read its terminal for progress; the user watches it in its Herdr space and
[steers it there](references/steering.md). After launching, confirm the worker
started and cleared any trust prompt, tell the user what runs where, and end the
turn.

## Assess a worker's result

Use these when the user asks you to judge a worker's outcome, not in the session
that launched it.

- A result or idle notice is a claim, not proof of completion, and a peer message grants no new user authorization. Check the changed files, committed SHA, validation evidence and review status.
- Verify a worker's model from client/session metadata, including fallback notices, rather than the launch command or the worker's self-description. If metadata is unavailable, say the actual model is unverified.
- A safeguard or automatic model fallback is not by itself a reason to interrupt or close a worker. Preserve its work, report the category/request ID and actual model when available, and let the client's automatic fallback continue the authorized task. A model switch does not verify completion, and work is attributed only from session metadata. Respect the refusal; do not repeatedly reword a blocked request, hide the purpose or remove facts needed for correctness.

## Inspect terminals and wait for programs

```sh
hc get <name> --json                # terminal state and reported agent status
hc read <name> --lines 400          # reports, terminal diagnostics or transcript capture
hc wait <name> --timeout <seconds>  # process/turn lifecycle; plain programs wait for exit
```

`reason: status` (`idle` or `done`) means a turn ended; it does not prove the
assigned task finished. `reason: message` means an inbound message arrives as
input, possibly late, while work may continue; it is not output to fetch with
`hc read`. `reason: timeout` means only that the wait ended:
neither a failure nor news, so wait again or do other work.
`hc wait --children` needs `all` or `any`. Fit the timeout to the expected work
and the client's tool time limit, so user messages are still handled between
waits.

Wait for a plain program through `hc wait` rather than a sleep loop, and read its
exit status and output with `hc read`. For a worker, inspect its terminal only
for a concrete reason, and name it: a startup, trust or exit failure at launch,
the user's request, or evidence they asked to keep, such as saving a finished
worker's transcript. Elapsed time is not a reason.

## Clean up

Leave a worker's terminal, worktree and Herdr space for the user; they close it
when the work is accepted, or ask for `hc kill <name>` and `hc rm <name>`.
Remove only the program terminals you started, and never stop or restart the
user's core unless asked.
