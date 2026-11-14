# Plugin maintenance

- Keep each skill in `plugins/<group>/skills/<name>/`; there is no plugin or
  marketplace packaging. Share skill content across clients, and keep an
  explicit-invocation skill's `disable-model-invocation` and
  `agents/openai.yaml` policy in step.
- Install and update this repository's skills with `npx skills`, targeting both
  `codex` and `claude-code` in symlink mode. Keep one shared active installation
  under `~/.agents/skills` and preserve local edits in the repository before updates.
  Keep the installation at the latest `origin/main`: after a merge into `main`,
  before reporting it, and whenever the installation is behind, fetch and
  fast-forward `/volume/repo/plugins` to `origin/main` and install from it, only
  while that checkout is clean on `main`, with
  `DISABLE_TELEMETRY=1 npx skills add /volume/repo/plugins --skill '*' --global --agent codex claude-code --yes`;
  `skills update` skips local sources, so rerun that command to refresh them.
- Run `python3 scripts/check_installation.py` from `/volume/repo/plugins` to
  compare the installed skills with a source commit before editing and after
  installation; see README.md.
- Keep plugin instructions focused on their workflow. Put machine-specific
  service mappings in a referenced file.
- Keep credentials, generated previews, runtime logs, and local installation
  settings out of this repository.
- Run `python3 scripts/validate.py` (or pass changed group names) for link and
  frontmatter checks; see README.md for its scope. For skill changes, exercise
  the affected workflow and report what was actually checked.

## Writing skills

Follow Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

- The description says in the third person what the skill does and when to use
  it; with the name, it is all the model sees before the skill loads.
- Add only what the model can't know or discover: this environment's facts, the
  owner's standing decisions, hard boundaries and gotchas. Leave out generic
  advice and anything the global instructions already say (`~/.claude/CLAUDE.md`,
  which `~/.codex/AGENTS.md` links to).
- State a goal, fact or boundary rather than a procedure. Give exact commands or
  a tested script where a step is fragile or must be deterministic, and say
  whether to run or read it.
- Keep `SKILL.md` short, with detail in references one level below it.
- No emphasis, capitals or dated history; date a measurement that can drift.
