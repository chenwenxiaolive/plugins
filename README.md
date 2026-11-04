# Personal skills

Personal skills for Codex and Claude Code, installed with `npx skills` as one
shared copy for both clients. There is no plugin or marketplace packaging.

## Skills

Each skill lives in `plugins/<group>/skills/<name>/`:

| Group | Skills | Purpose |
| --- | --- | --- |
| `preview` | [preview](plugins/preview/skills/preview/SKILL.md) | Publish HTML and Markdown pages through the bundled preview server. |
| `dev-workflow` | [implement](plugins/dev-workflow/skills/implement/SKILL.md), `gpu-cluster`, `grilling`, `to-tickets`, `leader`, `herdr-core`, `retro`, `improve-codebase-architecture`, `aliyun-pai` | Discuss designs, write issues, implement and review changes, run the GPU clusters, lead background workers, improve the workflow, inspect Alibaba Cloud PAI. |
| `docker-build` | [docker-build](plugins/docker-build/skills/docker-build/SKILL.md) | Build and publish images on the shared build host. |

- The `dev-workflow` skills link to each other, so install them together.
- `improve-codebase-architecture`, `leader`, `retro` and `to-tickets` run only when invoked: `disable-model-invocation` in `SKILL.md` for Claude Code, `allow_implicit_invocation: false` in `agents/openai.yaml` for Codex.
- They expect this environment: `gpu-cluster` the global instructions, SSH aliases and cluster layout; `aliyun-pai` authenticated `pai` and `aliyun` CLIs; `docker-build` the build host and registry access; `herdr-core` `hc` on `PATH` and signed-in Claude Code and Codex. Installing them creates no infrastructure and authorizes no jobs, cloud changes or publication.
- The workflow skills state rules and facts; the agent runs `git`, `glab`, `ssh`, `nvidia-smi`, `pai` and `aliyun` itself. The only scripts are the preview server's helper and `docker-build`'s `run-build.sh`.
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
python3 -B -m unittest discover -s plugins/preview/skills/preview/server/tests -v
```

The tests use fake external commands and temporary directories; they never touch a node, the registry or the deployed preview service.

## Evals

`plugins/dev-workflow/evals/` (for `gpu-cluster` and `implement`) and
`plugins/preview/evals/` hold cases for Claude Code's
[`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals): a prompt a user
might type and graders for the answer, each run with and without the group's skills
to show what the skills add.

```sh
scripts/run_evals.sh dev-workflow --runs 1 --judge-model sonnet
scripts/run_evals.sh preview --runs 1 --judge-model sonnet
```

The script runs a copy of the group with a plugin manifest in a new `/volume/tmp`
run directory, which receives the results and `report.html`. Runs load no
`CLAUDE.md`, credentials or ssh configuration and get only read-only tools, so the
cases test what the skills tell the agent, not the live machines. Each run is a
full Claude Code session billed to your account; `--runs 1` keeps a pass at one
session per case and arm (the default is three).
Don't remove client-supported frontmatter such as `disable-model-invocation` to
satisfy a generic validator. Work on a branch with a pull request; merge only on
the owner's request.
