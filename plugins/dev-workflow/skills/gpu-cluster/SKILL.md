---
name: gpu-cluster
description: Operating this setup's GPU nodes, gates and internal GitLab. Use before a task's first ssh or remote command, checkout sync, remote run or background job, GPU use, /volume temporary file, GitLab API or glab call, push to the internal GitLab, or gate deployment.
---

# GPU cluster operations

The rules in `~/.claude/CLAUDE.md` apply to every task; these references hold the
procedures and facts behind them. Read the one for what the task does next, not all:

| Doing | Read |
|---|---|
| ssh to a node or gate; node hardware, storage, network or tools; a node that stops answering | [machines.md](machines.md) |
| checkout paths and project instructions, syncing a checkout, creating a remote counterpart, commands in a remote checkout, formatting a local file with a node's tools, or where validation runs and what it records | [remote-workflow.md](remote-workflow.md) |
| `/volume` paths, temporary files, `TMPDIR`, checking whether GPUs are free, a background job, freeing GPU memory | [jobs.md](jobs.md) |
| GitLab issues, MRs, API calls or pushes; a dependency fetched from GitLab; OSS credentials for jobs | [gitlab.md](gitlab.md) |
| gate deployment, its saved configuration, the proxy and tunnel | [gate.md](gate.md) |

The issue/MR process (worktree reuse, branch names, execution records, review and
merging) is in the [implement](../implement/SKILL.md) skill.

A procedure is done when its own checks pass: a synced checkout at the exact SHA and
clean, a job's `exit.status` read, a cleanup confirmed on the GPUs it targeted.
