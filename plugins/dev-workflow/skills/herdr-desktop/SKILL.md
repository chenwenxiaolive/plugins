---
name: herdr-desktop
description: Coordinate background Claude Code and Codex workers through hc from the current session, and show them in the Herdr desktop app. Use when starting, instructing, waiting for, or reading back worker agents, checking that the worker CLIs are ready, or showing workers in Herdr's sidebar.
---

# Herdr desktop coordination

Keep the main conversation in the current session and run workers as hc
terminals. The session does not need to run inside a Herdr terminal. For hc
itself read `hc --skill` (the herdr-core skill); for window commands read
`herdr-app --skill` on the machine that runs the app.

Verified on 2026-11-02 with hc 0.1.16, Claude Code 2.1.295 and Codex 0.163.0,
with the Herdr app connected to this machine over SSH.

## Before the first worker

```sh
hc --version && claude --version && codex --version
claude auth status   # JSON: read only loggedIn
codex login status   # read only whether it says "Logged in"
hc exec -- sh -c 'command -v claude codex hc'   # what workers will find
```

- Never print the auth output: capture it and report only signed in or not.
  If a CLI is missing, install it with its official installer. If one is
  not signed in, ask the user to sign in; never ask for a key or token.
- Workers start with the core's environment, not this shell's. If the last
  check misses an agent, a worker can't start it; if it misses `hc`, a worker
  can't report. Write hc's absolute path into tasks: `HC=$(command -v hc)`.
- Claude Code reports status from 2.1.295, Codex from 0.163.0. Older ones
  never leave `reported: false`, so waits only end at exit or timeout.

## Start a worker

Give every worker its own `--name`, an explicit `--cwd`, and the whole task
in the launch, not in a later send. Set the model and reasoning effort
explicitly; if that model or configuration is unavailable, tell the user
instead of picking another.

```sh
HC=$(command -v hc)
SPACE="sp$(python3 -c 'import uuid; print(uuid.uuid4().hex)')"
REPORT="When done, run exactly once: $HC send $HC_TERMINAL_ID '<name> done: <one-line summary>'"
```

Claude Code:

```sh
hc run --bg --name <name> --cwd <dir> --label "herdr.space=$SPACE" \
  claude --model claude-opus-5-5 --effort xhigh "<task> $REPORT"
```

Codex, read-only with network so it can reach hc:

```sh
hc run --bg --name <name> --cwd <dir> --label "herdr.space=$SPACE" \
  codex --no-daemon -m gpt-6-astra -c 'model_reasoning_effort="xhigh"' \
  -c 'permissions.hcread.extends=":read-only"' \
  -c 'permissions.hcread.network.enabled=true' \
  -c 'default_permissions="hcread"' -a never "<task> $REPORT"
```

- `--no-daemon` keeps Codex's commands inside hc. Codex's plain read-only
  sandbox blocks hc (`Failed to connect to bus`); the profile above allows
  network and still blocks writes. `-a never` makes a refused command fail
  instead of waiting for an approval nobody sees.
- A Codex worker that must edit files uses `-s workspace-write -c
  sandbox_workspace_write.network_access=true` instead. Only the sandbox was
  checked (`codex sandbox ... -- hc ls`), not a full worker.
- Outside an hc terminal `$HC_TERMINAL_ID` is empty: leave `$REPORT` out
  and collect results with wait and read below.

## Show workers in Herdr

When the user wants to see workers, label them as above. The app puts a live
terminal labeled `herdr.space=<id>` into that space, creating an unnamed
space named after the folder when the id is new. Use a fresh id per worker,
or reuse one (and `herdr.tab=<id>`) to group them. A closed app places
still-running workers when it opens. Unlabeled workers show only under their
parent in the app's agents list. The app marks placed terminals `keep`, and
closing their space or pane in the app ends them.

## First start in a new folder

Agents ask once whether to trust a new folder, and the task waits until
answered. `hc read <name>` shows it: Claude Code asks "Is this a project you
trust?" with "No, exit" selected. Answer only for a folder the user owns or
approved (`hc keys <name> down enter` picks "Yes" there); otherwise, or if
the worker stays stuck, tell the user.

## Wait, read, follow up

```sh
hc wait <name> --timeout 600      # until it stops working
hc get <name> --json              # state, reported, status, turn
hc read <name> --lines 400        # its actual answer and history
hc send <name> "<feedback>"       # continue the same conversation
```

- `reason: status` with `idle` or `done`: the turn ended; read the answer.
- `reason: message`: a report reached you as your next input while the
  worker may still be working. Process it, then wait again.
- `reason: timeout`: a check-in, not failure. Read, then wait again.
- A report is a summary. Read the worker's answer with `hc read` and check
  its claims (cited files, changes, test output) before relying on it.
- Send feedback to the same worker; its earlier context stays.

## Clean up

When its work is accepted and recorded, `hc kill <name>` and `hc rm <name>`.
Only remove workers and worktrees you started, after checking the worktree
holds nothing unsaved.
