#!/usr/bin/env bash
set -euo pipefail

# bash reads a script while running it, and the fast-forward below can rewrite this file.
{
    main_checkout=$(git -C "$(dirname "$0")" worktree list --porcelain | sed -n '1s/^worktree //p')
    cd "$main_checkout"

    exec 9>"$(git rev-parse --git-dir)/sync-installation.lock"
    flock 9

    if [ "$(git symbolic-ref --short HEAD)" != main ] || [ -n "$(git status --porcelain -- plugins)" ]; then
        echo "$main_checkout is not on main with plugins/ committed; nothing was installed." >&2
        exit 1
    fi

    python3 scripts/check_installation.py
    git fetch origin main
    if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then
        echo "The installation already matches origin/main."
        exit 0
    fi
    git merge --ff-only origin/main
    if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
        echo "main in $main_checkout is ahead of origin/main; nothing was installed." >&2
        exit 1
    fi
    DISABLE_TELEMETRY=1 npx skills add "$main_checkout" --skill '*' --global --agent codex claude-code --yes
    python3 scripts/check_installation.py
    exit
}
