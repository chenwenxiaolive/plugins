#!/usr/bin/env bash
set -euo pipefail

main_checkout=$(git -C "$(dirname "$0")" worktree list --porcelain | sed -n '1s/^worktree //p')
cd "$main_checkout"

exec 9>"$(git rev-parse --git-dir)/sync-installation.lock"
flock 9

if [ "$(git symbolic-ref --short HEAD)" != main ] || [ -n "$(git status --porcelain)" ]; then
    echo "$main_checkout is not a clean checkout of main; nothing was installed." >&2
    exit 1
fi

python3 scripts/check_installation.py
git fetch origin main
git merge --ff-only origin/main
DISABLE_TELEMETRY=1 npx skills add "$main_checkout" --skill '*' --global --agent codex claude-code --yes
python3 scripts/check_installation.py
