# Personal plugins

Personal agent plugins for Codex and Claude Code, maintained in
[chenwenxiaolive/plugins](https://github.com/chenwenxiaolive/plugins).
The marketplace name is `chenwenxiaolive-plugins`.

## Plugins

| Plugin | Version | Purpose |
| --- | --- | --- |
| [preview](plugins/preview/skills/preview/SKILL.md) | 0.1.0 | Write HTML and Markdown artifacts to the existing preview service and return verified browser links. |
| [dev-workflow](plugins/dev-workflow/skills/implement/SKILL.md) | 0.1.0 | Discuss designs, create tickets, implement and review changes, operate the GPU cluster, and improve the development workflow. |
| [docker-build](plugins/docker-build/skills/docker-build/SKILL.md) | 0.1.0 | Build and publish container images through the existing dedicated build host. |

`dev-workflow` contains `gpu-cluster`, `grilling`, `implement`,
`improve-codebase-architecture`, `retro`, and `to-tickets`. These skills share
relative links, so they ship together without duplicating the cluster procedures.
The last three retain their explicit-invocation policy.

`preview` packages instructions and the personal service mapping. It has no MCP
server, hooks, executable scripts, package dependencies, or credentials. The
preview web server is an existing environment prerequisite.

## Install

The repository is private. Use the GitHub authentication already configured on
the machine.

### Codex

```bash
codex plugin marketplace add chenwenxiaolive/plugins --ref main
codex plugin add preview@chenwenxiaolive-plugins
```

Start a new session and ask: "Use the preview plugin to create a Markdown report
in /preview and give me its browser URL."

### Claude Code

```bash
claude plugin marketplace add chenwenxiaolive/plugins
claude plugin install preview@chenwenxiaolive-plugins
```

Start a new session and invoke `/preview:preview`, or ask for a document preview.

Replace `preview` in the installation command with another plugin name to install
it separately. For Claude Code, a skill in the workflow bundle is invoked as
`/dev-workflow:implement`, `/dev-workflow:grilling`, or the corresponding skill
name. New plugins become available from GitHub's `main` after their import PR is
merged.

### Local development

To use an unmerged checkout, register its absolute path in place of the GitHub
source. On the current control machine that path is `/volume/workspace/plugins`.
Use the same plugin installation commands above after adding the local source.

```bash
codex plugin marketplace add /volume/workspace/plugins
claude plugin marketplace add /volume/workspace/plugins
```

## Imported personal skills

The global skills were imported from `/root/.agents/skills` with their referenced
documents, scripts, and client metadata. Only plugin manifests and marketplace
entries were added around them; their operating procedures were preserved.

The import excludes the third-party `find-skills` package from
`vercel-labs/skills`, Herdr's automatically maintained `herdr-gpui-browser`, and
the clients' system or curated skills.

The original local skills remain in place and active. This import does not
install a second active copy of them or change their local links. When adopting
the repository versions, choose one discovery source for each skill to avoid
loading both the original and plugin copy.

These are personal environment workflows. `gpu-cluster` expects the existing
global instructions, SSH aliases, credentials, and cluster layout; `docker-build`
expects the configured build host and registry access. Installing the plugins
does not create that infrastructure or authorize jobs or publication.

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

Instructions are shared between both clients. Each portable `plugin.json` and
Claude manifest carry the same name and version. Increment both versions when
publishing an update and update the table above. Preserve skill-relative
references and explicit-invocation settings when moving or editing skills.

Validate metadata with the installed client:

```bash
claude plugin validate --strict .
claude plugin validate --strict plugins/preview
claude plugin validate --strict plugins/preview/skills
```

Repeat the plugin and skill checks for each changed plugin. Metadata validation
does not exercise infrastructure workflows: copying a Docker helper is not a
container build, and importing cluster instructions does not require running a
GPU job. Check imported file contents and modes against their source, resolve
relative references inside each package, and report this validation scope.

Use a development branch and pull request for changes. Merge only on the owner's
request.

Package formats follow the official
[OpenAI plugin documentation](https://developers.openai.com/plugins/build/plugins)
and [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces).
