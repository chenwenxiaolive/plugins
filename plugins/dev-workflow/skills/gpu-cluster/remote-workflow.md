# Remote workflow: checkouts, Git synchronization and validation

## Validation scope

- The control machine runs only light static checks with the tools it has: syntax, metadata, documentation links, Git refs. It installs no project dependencies and starts no project services.
- Project tests (small unit tests included), builds, benchmarks, training, formatters and linters run in the node checkout's environment.
- A documentation-only change needs its static checks and a read against realistic task cases, not a failing test.
- Report results for a clean committed snapshot: full SHA, checkout path, host, command and artifact directory.

## Checkouts

- The local and remote checkout share one absolute path: `/volume/workspace/<project>[/<checkout>]`, or `/volume/worktree/<repo>/<name>` for herdr worktrees. Work only in the selected one; ask before using any other. Leave existing worktrees where they are.
- Read the project instructions locally and, before the first remote command, in the remote checkout: `AGENTS.override.md` over `AGENTS.md`, plus `CLAUDE.md` and what they reference.
- For requested remote testing of a herdr worktree, create its missing remote counterpart through Git (a clone, or a worktree of an existing clone of the same repository) at the same path. If something already exists there, inspect it and reuse or report it; never replace it.

## Development and Git synchronization

- Edit locally and execute remotely. Commit a testable batch, push the development branch, update the remote checkout, verify its exact SHA, then run.
- Update a remote checkout with `git fetch` and `git merge --ff-only <sha>`, or `git switch --detach <sha>` for a detached review checkout. First make sure it is clean, on the expected branch, holds no unpushed commit (after `git fetch --prune origin`, `git branch -r --contains HEAD --list 'origin/*'` must list a branch for a detached HEAD), and is idle: no process on any machine sharing that `/volume` has its working directory in it (`/proc/*/cwd`). Investigate divergence or dirt; never reset, clean or stash.
- Each cluster's `/volume` is shared, so update a checkout once per cluster; other clusters have their own copies.
- Before validating, the remote checkout must be clean, at the committed SHA, and match its lock: for a uv project, `uv sync --locked --dry-run` shows no dependency changes. Sync the environment only while no job uses it.
- Verify the push remote and authentication before the first push; a clone does not prove push access.

## Operating remotely

- Use `sh-0`, `zg-0` or `th-0` for Git and file work on that cluster. GPU jobs run only on the node the user names.
- Start every remote project command by changing to the checkout's physical path. A Herdr worktree's `$PWD` goes through `~/.herdr/worktrees`, which the nodes don't have:

  ```bash
  ssh sh-0 "cd -- $(printf %q "$(pwd -P)") && "'git status --short --branch'
  ```

- To format a local file before committing, pipe it through the node environment's tools, in the order of the project's format config, with explicit `pipefail`. Use the output only if the command succeeds, and never redirect it over its input:

  ```bash
  ssh sh-0 "bash -o pipefail -c 'cd -- <checkout> && .venv/bin/black -q --stdin-filename <path> - | .venv/bin/ruff check --fix --quiet --stdin-filename <path> -'" < <path>
  ```

- Run scripts and configs go into the run's `/volume/tmp` directory (jobs.md) with `scp` or ssh stdin; source code travels only through Git.
