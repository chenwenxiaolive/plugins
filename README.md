# Personal skills

Personal skills for Codex and Claude Code, maintained in
[chenwenxiaolive/plugins](https://github.com/chenwenxiaolive/plugins).
Use `npx skills` to install and update one shared copy for both clients.
The repository also retains the `chenwenxiaolive-plugins` packaging metadata.

## Plugins

| Plugin | Version | Purpose |
| --- | --- | --- |
| [preview](plugins/preview/skills/preview/SKILL.md) | 0.4.1 | Preview HTML and Markdown locally or through an SSH tunnel, and manage the bundled service. |
| [dev-workflow](plugins/dev-workflow/skills/implement/SKILL.md) | 0.1.10 | Discuss designs, create tickets, implement and review changes, operate the GPU cluster, inspect Alibaba Cloud PAI, manage persistent agent terminals, lead background workers, and improve the development workflow. |
| [docker-build](plugins/docker-build/skills/docker-build/SKILL.md) | 0.1.0 | Build and publish container images through the existing dedicated build host. |

`dev-workflow` contains `aliyun-pai`, `gpu-cluster`, `grilling`, `herdr-core`,
`implement`, `improve-codebase-architecture`, `leader`, `retro`, and
`to-tickets`. Several of these skills share relative links, so they ship
together without duplicating the cluster procedures.
`improve-codebase-architecture`, `leader`, `retro`, and `to-tickets` retain
their explicit-invocation policy.

`herdr-core` coordinates background Claude Code and Codex workers through hc
from the current session, with verified launch, wait, read-back and Herdr
sidebar procedures; agents read `hc --skill` for the full hc manual.

`preview` includes its preview server, Markdown renderer, theme assets, and
start/stop/status commands. It needs Linux, Python 3.10+, and Node.js 18+; no
dependency installation is required. Installation does not start a service.
Documents, logs, and process state live outside the installed plugin.

## Install and update

The repository is private. Use the GitHub authentication already configured on
the machine. Install all eleven skills for both clients with one command:

```sh
DISABLE_TELEMETRY=1 npx skills add chenwenxiaolive/plugins \
  --skill '*' --global --agent codex claude-code --yes
```

The shared files live in `~/.agents/skills/<name>`. Codex reads that directory;
Claude Code uses links under `~/.claude/skills/`. Keep the default symlink mode.
The installer records each source in `~/.agents/.skill-lock.json`. Disabling
telemetry also disables external skill-audit requests for this private source.

Rerun the same command to refresh this repository's skills for both clients.
To select a subset, replace `'*'` with skill names. Install the `dev-workflow`
skills together because some of their relative references cross skill
directories.

Start a new session and ask for the skill by name. In Claude Code, use `/preview`,
`/implement`, or the corresponding skill name. The explicit-invocation policies
of `improve-codebase-architecture`, `leader`, `retro`, and `to-tickets` are
preserved.

Use this shared installation as the active source. If a repository plugin is
already enabled in either client, verify the shared skills first, then remove
that duplicate plugin registration. Keep unrelated plugins installed normally.

### Current control machine

The selected source is the real checkout at `/volume/repo/plugins`. After
committing the intended changes there, install or update all its skills with:

```sh
DISABLE_TELEMETRY=1 npx skills add /volume/repo/plugins \
  --skill '*' --global --agent codex claude-code --yes
```

Local installations record the checkout as their source. `skills update` skips
local sources; rerun this `skills add` command to refresh them. This updates the
shared skill content and client links without changing the deployed preview
service or starting infrastructure jobs.

## Imported personal skills

The global skills were imported from `/root/.agents/skills` with their referenced
documents, scripts, and client metadata. Only plugin manifests and marketplace
entries were added around them; their operating procedures were preserved.
`herdr-core` is not an import: it was written from `hc --skill`,
`herdr-app --skill` and checks on real workers.

The import excludes the third-party `find-skills` package from
`vercel-labs/skills` and the clients' system or curated skills.

The repository is the maintained source for these personal skills. Before
replacing an existing shared installation, compare its files with the repository
and reconcile local edits into the repository. Update the shared files through
`npx skills` after committing those changes; keep other skill sources unchanged.

These are personal environment workflows. `gpu-cluster` expects the existing
global instructions, SSH aliases, credentials, and cluster layout; `aliyun-pai`
expects an Alibaba Cloud CLI profile with read access to the selected PAI region
and workspace; `docker-build` expects the configured build host and registry
access; `herdr-core` expects `hc` (herdr-core) on `PATH` and signed-in Claude
Code and Codex CLIs. Installing the plugins does not create that infrastructure
or authorize jobs, cloud mutations, or publication.

## Preview behavior

- Standalone deliverables go under `/preview`; tracked repository documentation
  stays in its repository.
- The service binds to loopback by default. On the current control machine,
  open browser links through an SSH local forward using the service reference.
- The service renders Markdown at its `.md` URL and serves HTML directly.
- Markdown `mermaid` fences render as diagrams with theme support and a source
  toggle, using a bundled library without browser CDN requests.
- `?raw=1` returns source text; `?download=1` downloads the original file.
- Directory listings can be sorted by Name, Size, or Updated. Click a column
  heading again to reverse its order; directories remain first.
- The skill verifies artifact content at the service endpoint. For SSH access,
  browser links require an active tunnel on the user's computer.
- Existing files are preserved unless the task asks to update them.

The current machine's address and override rules are documented in
[the service reference](plugins/preview/skills/preview/references/service.md).
The plugin reuses an available service and can start its bundled server when
setup is requested. See the service reference for configuration and commands.
The service source is maintained directly in
`plugins/preview/skills/preview/server/`. Change its code, tests, and documentation
in this repository and release them with the plugin. No separate service
repository or source import step is required.

## Maintenance

Each plugin lives in `plugins/<name>/`. Register it in both marketplace catalogs:

- `.agents/plugins/marketplace.json` for Codex.
- `.claude-plugin/marketplace.json` for Claude Code.

Instructions are shared between both clients. Each portable `plugin.json` and
Claude manifest carry the same name and version. Increment both versions when
publishing an update and update the table above. Preserve skill-relative
references and explicit-invocation settings when moving or editing skills.
Use the shared `npx skills` installation workflow for this repository's skills.

Run the repository's static checks with Python 3 and the installed Claude Code
CLI; no dependency installation is needed:

```bash
python3 scripts/validate.py                 # all plugins
python3 scripts/validate.py dev-workflow    # selected plugin(s)
```

The entry point checks both catalogs, manifest names and versions, the version
table above, and relative inline Markdown file links in the selected plugins and this
README. It runs `claude plugin validate --strict` on the marketplace, each selected
plugin and its `skills` component directory. Skill schemas belong to the installed
client: a generic frontmatter helper may reject supported fields such as
`disable-model-invocation`. Do not remove those fields to satisfy that helper.

These checks do not exercise infrastructure workflows, fetch external links, or
validate Markdown anchors. Copying a Docker helper is not a container build, and
importing cluster instructions does not require running a GPU job. Exercise changed
workflow behavior separately; for installation updates, compare installed file
contents and modes with their committed source. Report what was actually checked.

Use a development branch and pull request for changes. Merge only on the owner's
request.

The shared installer is documented in the
[Skills CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).
Package formats follow the official
[OpenAI plugin documentation](https://developers.openai.com/plugins/build/plugins)
and [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces).
