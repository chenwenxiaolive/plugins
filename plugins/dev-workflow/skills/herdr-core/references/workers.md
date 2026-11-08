# Launching coding workers

Tested with hc 0.1.16, Claude Code 2.1.295 and Codex 0.167.0.

## Before the first worker

Check `hc --version` and only the client selected for this launch:

- Claude Code: `claude --version` and `claude auth status | jq -r .loggedIn`.
- Codex: `codex --version` and `codex login status 2>&1 | grep -q 'Logged in' && echo signed-in || echo signed-out`.

Install a missing CLI needed for this launch with its official installer; ask the
user to sign in only if that client's authentication is missing.

- Workers inherit the core's environment, whose `PATH` lacks `~/.local/bin` (`hc`, `uv`): launch them through `env PATH="$PATH"`.
- Claude Code reports status from 2.1.295, Codex from 0.163.0. Older versions stay `reported: false`: no Herdr sidebar entry, and waits end only at exit or timeout.

## Start a worker

Each working directory has one independent session. A worker may create native
subagents in its own working directory/checkout under
[leader's shared-checkout rules](../../leader/SKILL.md#shared-checkout).
Never place a native subagent in another working directory or worktree; arrange
an independent worker there instead. For code work, subdirectories within the
same checkout/worktree are part of the same boundary.

Give each Herdr worker its own `--name`, an exact scope and the whole task in the
launch (a message to a booting agent can be lost), and a `--cwd` where no other
independent Claude Code or Codex session runs: sessions in one directory share
its working tree, Git index and HEAD, uncommitted files, and per-directory session
state and settings. Set the model and effort explicitly; if unavailable, tell the user
instead of substituting. Both run with full access and no approval prompts, so the
task sets what they and their local native subagents may change.

Use the leader's harness, model and reasoning effort unless the user explicitly
chooses otherwise. Read [communication.md](communication.md) and include the
leader's native reply address and a route nonce in the launch task, or the bridge
for an explicit cross-harness assignment. The worker's ready report returns the
nonce with its own native address and checkout; match that identity and finish
the [route check](communication.md#route-check) before follow-ups.
Use the Herdr worker section of [leader's brief](../../leader/delegation-brief.md#herdr-worker)
for implementation assignments.
Fill the model and effort placeholders below from the selected role.

```sh
# Claude Code (IS_SANDBOX=1 lets root use --dangerously-skip-permissions)
hc run --bg --name <name> --cwd <dir> \
  --label "herdr.space=sp$(python3 -c 'import uuid; print(uuid.uuid4().hex)')" \
  env IS_SANDBOX=1 PATH="$PATH" claude --dangerously-skip-permissions \
  --name <name> --model <model> --effort <effort> "<task with native reply address>"

# Codex
hc run --bg --name <name> --cwd <dir> \
  --label "herdr.space=sp$(python3 -c 'import uuid; print(uuid.uuid4().hex)')" \
  env PATH="$PATH" codex --no-daemon --yolo -m <model> \
  -c 'model_reasoning_effort="<effort>"' "<task with native reply address>"
```

- Launch a coding worker directly as interactive `claude` or `codex`, as above, so its Herdr space shows the agent's own UI and stays steerable. Never use `claude -p`, `codex exec`, `codex review`, or a shell, redirect, `tee` or log tail around the agent in place of that UI; for saved evidence, have the worker write files or save `hc read` output afterwards. Checks and evals may run as background programs, but they are not workers; don't report them as such.
- hc's `cwd` can be stale; list the directories agents really run in with `for p in $(pgrep -x claude; pgrep -x codex); do readlink /proc/$p/cwd; done`.
- `--no-daemon` keeps Codex's execution backend under the Herdr terminal; the shared daemon would execute commands outside hc's process ownership. Native `codex queue` still works. Don't pass Codex `--worktree`: it ignores `-c` for its root and leaves `<root>/<hex>/<repo>` checkouts behind. Prepare the checkout under the project's worktree rules and pass it as `--cwd`.
- The native reply address works whether or not the leader is in an hc terminal; do not use `$HC_TERMINAL_ID` as a native session address.
- The `herdr.space=<id>` label puts the worker's live terminal in that Herdr space, naming a new one after its folder. Give every worker its own new id, as above: a shared id opens the workers as panes of one space, which this owner never wants. Unlabeled workers appear only under their parent. Closing a placed terminal's space or pane in the app ends it.
- A new folder triggers a trust prompt that blocks the task. `hc read <name>` shows Claude Code's "Is this a project you trust?" or Codex's "Trust this folder?"; for a folder the user owns or approved, `hc keys <name> down enter` answers Claude Code and `hc keys <name> enter` Codex (its first option, "Trust and continue", is selected). Otherwise, or if it stays stuck, tell the user.
- A worker's own `hc run --bg` programs are its children: they end when it ends unless started with `--outlive-parent`, and their exit note starts its next turn.
