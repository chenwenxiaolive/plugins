# Plugin maintenance

- Keep each plugin in `plugins/<name>/` and list it in both marketplace catalogs.
- Share skill content across clients; keep the portable and Claude manifest names
  and versions consistent.
- Install and update this repository's skills with `npx skills`, targeting both
  `codex` and `claude-code` in symlink mode. Keep one shared active installation
  under `~/.agents/skills` and preserve local edits in the repository before updates.
- Keep plugin instructions focused on their workflow. Put machine-specific
  service mappings in a referenced file.
- Keep credentials, generated previews, runtime logs, and local installation
  settings out of this repository.
- Run `python3 scripts/validate.py` (or pass changed plugin names) for metadata
  and reference checks; see README.md for its scope. For skill changes, exercise
  the affected workflow and report what was actually checked.
- Use a development branch and pull request. Merge only when the owner asks.
