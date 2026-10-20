# Personal plugins

Personal agent plugins for Codex and Claude Code, maintained in
[chenwenxiaolive/plugins](https://github.com/chenwenxiaolive/plugins).
The marketplace name is `chenwenxiaolive-plugins`.

## Plugins

| Plugin | Version | Purpose |
| --- | --- | --- |
| [preview](plugins/preview/skills/preview/SKILL.md) | 0.1.0 | Write HTML and Markdown artifacts to the existing preview service and return verified browser links. |

`preview` packages instructions and the personal service mapping. It has no MCP
server, hooks, executable scripts, package dependencies, or credentials. The
preview web server is an existing environment prerequisite.

## Install

The repository is private. Use the GitHub authentication already configured on
the machine.

### Codex

After the plugin branch is merged into `main`:

```bash
codex plugin marketplace add chenwenxiaolive/plugins --ref main
codex plugin add preview@chenwenxiaolive-plugins
```

Start a new session and ask: "Use the preview plugin to create a Markdown report
in /preview and give me its browser URL."

### Claude Code

After the plugin branch is merged into `main`:

```bash
claude plugin marketplace add chenwenxiaolive/plugins
claude plugin install preview@chenwenxiaolive-plugins
```

Start a new session and invoke `/preview:preview`, or ask for a document preview.

### Local development

To use an unmerged checkout, register its absolute path in place of the GitHub
source. On the current control machine that path is `/volume/workspace/plugins`.
Use the same plugin installation commands above after adding the local source.

```bash
codex plugin marketplace add /volume/workspace/plugins
claude plugin marketplace add /volume/workspace/plugins
```

## Preview behavior

- Standalone deliverables go under `/preview`; tracked repository documentation
  stays in its repository.
- The service renders Markdown at its `.md` URL and serves HTML directly.
- `?raw=1` returns source text; `?download=1` downloads the original file.
- The skill checks the actual artifact URL before calling it available.
- Existing files are preserved unless the task asks to update them.

The current machine's address and override rules are documented in
[the service reference](plugins/preview/skills/preview/references/service.md).
The plugin reuses the service; it does not start or reconfigure it.

## Maintenance

Each plugin lives in `plugins/<name>/`. Register it in both marketplace catalogs:

- `.agents/plugins/marketplace.json` for Codex.
- `.claude-plugin/marketplace.json` for Claude Code.

The preview instructions are shared between both clients. Its portable
`plugin.json` and Claude manifest carry the same name and version. Increment both
versions when publishing an update and update the table above.

Validate metadata with the installed client:

```bash
claude plugin validate --strict .
claude plugin validate --strict plugins/preview
claude plugin validate --strict plugins/preview/skills
```

Use a development branch and pull request for changes. Merge only on the owner's
request.

Package formats follow the official
[OpenAI plugin documentation](https://developers.openai.com/plugins/build/plugins)
and [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces).
