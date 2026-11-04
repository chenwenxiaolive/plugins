# Plugin maintenance

- Each skill is one `SKILL.md` in `plugins/<group>/skills/<name>/`: only facts an agent can't discover and the owner's rules. No helper scripts, no reference files, no procedures a capable agent can work out. Fix a gap with one precise sentence, not code.
- Keep an explicit-invocation skill's `disable-model-invocation` and `agents/openai.yaml` policy in step.
- Check a change with `claude plugin validate --strict plugins/<group>/skills`, confirm that its relative links and anchors resolve, and exercise the workflow it describes. Report what was actually checked.
- After committing, install with `DISABLE_TELEMETRY=1 npx skills add /volume/repo/plugins --skill '*' --global --agent codex claude-code --yes`. Then `diff -r plugins/<group>/skills/<name> ~/.agents/skills/<name>` shows nothing, and `~/.claude/skills/<name>` links there.
- The preview server in `plugins/preview/server/` is a program with its own tests (`python3 -B -m unittest discover -s plugins/preview/server/tests`).
- Keep credentials, generated previews, runtime logs and local installation settings out of the repository. Use a development branch and pull request; merge only when the owner asks.
