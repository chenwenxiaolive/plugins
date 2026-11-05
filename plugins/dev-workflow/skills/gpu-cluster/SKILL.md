---
name: gpu-cluster
description: "Holds the facts about this setup's GPU nodes, gates, shared /volume storage and internal GitLab, and how work runs there. Use before a task's first ssh or remote command, a remote checkout sync, a remote run or background job, GPU use, a /volume temporary file, a GitLab API or glab call, a push to the internal GitLab, or gate work."
---

# GPU cluster operations

The rules in `~/.claude/CLAUDE.md` apply to every task; these references hold the
facts behind them. Read the one for what the task does next, not all:

| Doing | Read |
|---|---|
| ssh to a node or gate; node hardware, storage, network or tools; a node that stops answering | [machines.md](machines.md) |
| syncing a remote checkout, creating a remote counterpart, remote commands, formatting with a node's tools, where validation runs | [remote-workflow.md](remote-workflow.md) |
| `/volume` paths, temporary files, `TMPDIR`, checking whether GPUs are free, a background job and its OSS credentials, freeing GPU memory | [jobs.md](jobs.md) |
| GitLab issues, MRs, API calls or pushes; a dependency fetched from GitLab | [gitlab.md](gitlab.md) |
| gate deployment, its saved configuration, the proxy and tunnel | [gate.md](gate.md) |

CPU-only work on a node exports `CUDA_VISIBLE_DEVICES=` (empty) so it can't touch a GPU.
