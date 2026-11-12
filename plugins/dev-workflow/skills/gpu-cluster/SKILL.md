---
name: gpu-cluster
description: "Guides this environment's cluster and internal GitLab operations. Use before SSH, remote checkout work, GPU or background jobs, /volume temporary files, GitLab calls or pushes, and gate changes."
---

# GPU cluster operations

The rules in `~/.claude/CLAUDE.md` apply to every task; these references hold the
facts behind them. Read the one for what the task does next, not all:

| Doing | Read |
|---|---|
| ssh to a node or gate; node hardware, storage, network or tools; a node that stops answering | [machines.md](machines.md) |
| syncing a remote checkout, creating a remote counterpart, remote commands, formatting with a node's tools, where validation runs | [remote-workflow.md](remote-workflow.md) |
| requesting or returning a GPU machine, checking GPU use, `/volume` paths, temporary files, `TMPDIR`, background jobs and OSS credentials, freeing GPU memory | [jobs.md](jobs.md) |
| GitLab issues, MRs, API calls or pushes; a dependency fetched from GitLab | [gitlab.md](gitlab.md) |
| gate deployment, its saved configuration, the proxy and tunnel | [gate.md](gate.md) |

CPU-only work on a node exports `CUDA_VISIBLE_DEVICES=` (empty) so it can't touch a GPU.
