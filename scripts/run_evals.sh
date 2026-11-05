#!/usr/bin/env bash
# Run a skill group's eval suite with Claude Code's `claude plugin eval`.
#
#   scripts/run_evals.sh <group> [claude plugin eval options...]
#   scripts/run_evals.sh dev-workflow --runs 1 --judge-model sonnet --tag retro leader
#
# The groups carry no plugin manifest, which `claude plugin eval` needs to load
# their skills. This copies plugins/<group>/skills and plugins/<group>/evals into
# a temporary plugin with one, in a new /volume/tmp run directory, and writes the
# results and report.html to <run directory>/results. --scaffold runs the cases'
# setup.sh scripts, which create sample files in each run's empty workspace.
# Every case also gets ~/.claude/CLAUDE.md as appended system prompt, in both
# arms, as real sessions load it, so a case measures what its skill adds on top.
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
python3 - "$run/plugin/evals" "$HOME/.claude/CLAUDE.md" <<'PY'
import pathlib, sys
lines = pathlib.Path(sys.argv[2]).read_text().splitlines()
block = "append_system_prompt: |\n" + "".join(f"  {line}\n" if line.strip() else "\n" for line in lines)
for prompt in pathlib.Path(sys.argv[1]).glob("*/prompt.md"):
    text = prompt.read_text()
    if not text.startswith("---\n"):
        sys.exit(f"{prompt}: no frontmatter")
    prompt.write_text("---\n" + block + text[4:])
PY
printf 'run directory: %s\n' "$run"
claude plugin eval "$run/plugin" --trust-plugin --scaffold --no-publish --output-dir "$run/results" "$@"
