# Personal skills

Personal skills for Codex and Claude Code, installed with `npx skills` as one
shared copy for both clients.

Each skill is one `SKILL.md` in `plugins/<group>/skills/<name>/`, holding only the
facts an agent can't discover and the owner's rules; the agent does the work with
the tools it already has. There are no helper scripts or reference files.

| Group | Skills | Purpose |
| --- | --- | --- |
| `preview` | [preview](plugins/preview/skills/preview/SKILL.md) | Publish HTML and Markdown pages through the preview server. |
| `dev-workflow` | [implement](plugins/dev-workflow/skills/implement/SKILL.md), [gpu-cluster](plugins/dev-workflow/skills/gpu-cluster/SKILL.md), `grilling`, `to-tickets`, `leader`, `herdr-core`, `retro`, `improve-codebase-architecture`, `aliyun-pai` | Discuss designs, write issues, implement and review changes, run the GPU clusters, lead background workers, improve the workflow, inspect Alibaba Cloud PAI. |
| `docker-build` | [docker-build](plugins/docker-build/skills/docker-build/SKILL.md) | Build and publish images on the shared build host. |

- The `dev-workflow` skills link to each other, so install them together.
- `improve-codebase-architecture`, `leader`, `retro` and `to-tickets` run only when invoked: `disable-model-invocation` in `SKILL.md` for Claude Code, `allow_implicit_invocation: false` in `agents/openai.yaml` for Codex.
- The skills describe this environment (SSH aliases, clusters, build host, PAI, preview service). Installing them creates no infrastructure and authorizes no jobs, cloud changes or publication.
- The [preview server](plugins/preview/server/README.md) is the one program here: the service behind the `preview` skill, kept outside the skill so agents don't get its source installed.

## Install

From the committed checkout on this machine:

```sh
DISABLE_TELEMETRY=1 npx skills add /volume/repo/plugins \
  --skill '*' --global --agent codex claude-code --yes
```

Files land in `~/.agents/skills/<name>` (read by Codex), linked from
`~/.claude/skills/<name>` (Claude Code). `skills update` skips local sources, so rerun
`skills add` to refresh.
