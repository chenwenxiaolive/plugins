# Personal skills

Personal skills for Codex and Claude Code, installed with `npx skills` as one
shared copy for both clients. There is no plugin or marketplace packaging.

## Skills

Each skill lives in `plugins/<group>/skills/<name>/`:

| Group | Skills | Purpose |
| --- | --- | --- |
| `preview` | [preview](plugins/preview/skills/preview/SKILL.md) | Publish HTML and Markdown pages through the bundled preview server. |
| `dev-workflow` | [implement](plugins/dev-workflow/skills/implement/SKILL.md), `gpu-cluster`, `grilling`, `to-tickets`, `pr`, `leader`, `herdr-core`, `retro`, `improve-codebase-architecture`, `aliyun-pai`, `siflow` | Discuss designs, write issues, implement and review changes, describe requests and weigh their merge risk, run the GPU clusters, launch independent workers, improve the workflow, inspect Alibaba Cloud PAI and the SiFlow AI platform. |
| `docker-build` | [docker-build](plugins/docker-build/skills/docker-build/SKILL.md) | Build and publish images on the shared build host. |

- The `dev-workflow` skills link to each other, so install them together.
- `improve-codebase-architecture`, `leader` and `retro` run only when invoked: `disable-model-invocation` in `SKILL.md` for Claude Code, `allow_implicit_invocation: false` in `agents/openai.yaml` for Codex.
- `to-tickets` is also selected for plain requests to create or draft issues; the user's request, not the skill, decides whether anything is published.
- They expect this environment: `gpu-cluster` the global instructions, SSH aliases and cluster layout; `aliyun-pai` authenticated `pai` and `aliyun` CLIs; `siflow` `uv` and the SiFlow AK/SK environment variables; `docker-build` the build host and registry access; `herdr-core` `hc` on `PATH` and signed-in Claude Code and Codex. Installing them creates no infrastructure and authorizes no jobs, cloud changes or publication.
- The workflow skills state rules and facts; the agent runs `git`, `glab`, `ssh`, `nvidia-smi`, `pai`, `aliyun` and the SiFlow SDK itself. `gpu-cluster` bundles its machine allocation table, `docker-build` its `run-build.sh`, and `preview` its server.
- `preview` needs Linux, Python 3.10+ and Node.js 18+. This machine's settings are in [service.md](plugins/preview/skills/preview/references/service.md), the server's features and tests in [its README](plugins/preview/skills/preview/server/README.md).

## Install

From the committed checkout (this machine: `/volume/repo/plugins`), or from
`chenwenxiaolive/plugins` with GitHub authentication:

```sh
DISABLE_TELEMETRY=1 npx skills add /volume/repo/plugins \
  --skill '*' --global --agent codex claude-code --yes
```

The files land in `~/.agents/skills/<name>` (read by Codex), linked from
`~/.claude/skills/` (Claude Code). `skills update` skips local sources, so rerun
`skills add` to refresh. `python3 scripts/check_installation.py [--source-ref <sha>]`
compares the installation with a commit (contents, modes, links and the recorded
source) and never writes anything.

## Checks

```sh
python3 scripts/validate.py [group...]   # Markdown links and anchors, `claude plugin validate --strict`
python3 -B -m unittest discover -s tests/docker-build -v
python3 -B -m unittest discover -s tests/preview -v
python3 -B -m unittest discover -s tests/repository -v
GPU_ALLOCATION_TEST_TMPDIR=<run-directory> python3 -B -m unittest discover -s tests/gpu-cluster -v
python3 -B -m unittest discover -s plugins/preview/skills/preview/server/tests -v
```

The tests use fake external commands and temporary directories; they never touch a node, the registry or the deployed preview service.
Don't remove client-supported frontmatter such as `disable-model-invocation` to
satisfy a generic validator. Work on a branch with a pull request; merge only on
the owner's request.
