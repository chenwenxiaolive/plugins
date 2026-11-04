#!/usr/bin/env bash
# Run a skill group's eval suite with Claude Code's `claude plugin eval`.
#
#   scripts/run_evals.sh <group> [claude plugin eval options...]
#   scripts/run_evals.sh dev-workflow --runs 1 --judge-model sonnet --case 'gpu-*'
#
# The groups carry no plugin manifest, which `claude plugin eval` needs to load
# their skills. This copies plugins/<group>/skills and plugins/<group>/evals into
# a temporary plugin with one, in a new /volume/tmp run directory, and writes the
# results and report.html to <run directory>/results.
set -euo pipefail

group=${1:-}
src=$(cd -- "$(dirname -- "$0")/.." && pwd -P)/plugins/$group
if [[ -z "$group" || ! -d "$src/evals" ]]; then
  printf 'usage: %s <group> [claude plugin eval options...]; groups with evals: %s\n' \
    "$0" "$(cd -- "$(dirname -- "$0")/../plugins" && echo */evals | sed 's|/evals||g')" >&2
  exit 2
fi
shift

run=$(mktemp -d "/volume/tmp/skill-evals-$group-$(date +%Y%m%d)-XXXXXX")
mkdir -p "$run/plugin/.claude-plugin"
printf '{"name": "%s"}\n' "$group" > "$run/plugin/.claude-plugin/plugin.json"
cp -R "$src/skills" "$src/evals" "$run/plugin/"
printf 'run directory: %s\n' "$run"
claude plugin eval "$run/plugin" --trust-plugin --no-publish --output-dir "$run/results" "$@"
