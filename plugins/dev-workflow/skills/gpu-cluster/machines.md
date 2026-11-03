# Machines, nodes and network

## Two-tier setup

Two-tier setup: **edit real local Git checkouts on this control machine, commit and push through Git, then update and run the same commit on the remote GPU nodes over ssh**. The local and remote checkout must have **the same absolute path**: normally `/volume/workspace/<project>[/<checkout>]` for main project checkouts, or `/volume/worktree/<repo>/<worktree-name>` for herdr worktrees and their remote counterparts. Worktree names may stay fixed while the assigned issue/MR and checked-out branch or commit change.
The local `/volume` is ordinary storage on this control machine, not a mount of the nodes' shared disk. Matching paths contain independent Git checkouts; Git synchronizes their source code.

## This machine (control machine)
- Ubuntu 22.04 VPS, running as root, timezone UTC, **4 vCPU / 4 GiB RAM / approximately 80 GB root disk**, no GPU. Check free space before disk-intensive work. Local `/volume` uses this same filesystem.
- **Local source-code editing is allowed** in the selected real Git checkout under `/volume/workspace` or `/volume/worktree`. The selected ops checkout is `/volume/cluster-ops` (see gate.md). Read, search, edit, review diffs, commit, and push locally.
- Follow [validation scope](remote-workflow.md#validation-scope) for the boundary between local static checks and remote project execution. Keep this machine's work lightweight.
  - Local Python is 3.10. The `venv` module exists, but `pip` and `ensurepip` are absent; do not assume a working virtualenv bootstrap. `uv` and `gcc` are absent too.
  - Keep model weights, datasets, large caches, and experiment output on the remote storage described in the node section below.
- Local `git`, `curl`, `jq`, `rsync`, Docker CLI, `gh` and `glab` are available; `rclone` is not on PATH, so use gate's. `gh` updates through GitHub's apt repository. `glab` has no apt repository: it was installed from GitLab's release `.deb`, so update it by installing a newer release's `.deb` after checking it against that release's `checksums.txt`. Docker CLI availability does not change the restriction on heavy local builds; use the remote Docker build workflow.
- The control machine uses its own `/root` shell configuration. Its `/volume/.bashrc`, `/volume/.ssh`, and `/volume/.config` are saved gate deployment inputs, not automatically the control machine's active configuration. Do not source the gate's `.bashrc` into the control shell to obtain credentials or tools.

## GPU nodes and gates

| Cluster | GPU aliases | Gate alias | Shared `/volume` |
|---|---|---|---|
| sh | `sh-0`, `sh-1`, `sh-2` | `sh-gate` | GPFS |
| zg | `zg-0`, `zg-1` | `zg-gate` | CPFS |
| th | `th-0`, `th-1` | none | GPFS |

- Connect with the aliases in `~/.ssh/config`, such as `ssh sh-0` or `ssh zg-0`; use that file as the source for addresses and ports. Check selected effective fields with `ssh -G <alias> | rg '^(hostname|port|user|proxyjump) '` when needed; do not dump credential-bearing fields such as `setenv`.
- **Local ssh has connection multiplexing enabled for all hosts** (`Host *` in `~/.ssh/config`, sockets in `~/.ssh/cm/`, closed after 10 minutes idle):
  - The first command to each node takes about 0.8 s, each subsequent one about 0.3 s, so there is no need to cram commands together to save connections
  - Node sshd has MaxSessions=10: when more than 10 sessions run concurrently on one node, the extra ones automatically open new connections; too many new connections at once get randomly rejected by MaxStartups (error `kex_exchange_identification`). Keep concurrency under 10
  - If commands hang after a pod rebuild because of a stale master connection, close that alias's old connection with `ssh -O exit <alias>` and then retry. Every local session's commands to an alias share its master, and `-O exit` cuts the ones in flight, so use it only for that hang; each command already starts a fresh remote shell, so a changed shell startup file needs no reconnect. Report connection timeouts, refusals, or host-key changes as described below.
- The nodes and gates are k8s pods with timezone **CST (UTC+8)**; this machine is UTC. A pod's hostname need not match its alias; identify machines by their configured SSH aliases. Hardware and mounts checked on 2026-10-16, th on 2026-10-18:
  - **sh-0, sh-1, sh-2**: 8×H200 (141 GB each), driver 580, 8 IB NICs (mlx5); `/volume` is a 50 TB GPFS mount with `HF_HOME=/volume/.cache` (seen on 2026-11-03; an older HF cache under `/volume/.cache/huggingface/hub` is outside that `HF_HOME`)
  - **zg-0, zg-1**: 8×H20-3e (141 GB each), driver 570 (CUDA 13 runs through its forward-compatibility libraries), 4 bonded IB NICs; `/volume` is a 3 PB CPFS FUSE mount that cannot host Unix sockets and has no HF cache
  - sh and zg: 192 cores, 2 TiB RAM, NVIDIA PyTorch container; tools Python + pip + uv, gcc, git, rg, jq, gh, glab, rsync, rclone; **no tmux or screen**
  - **th-0, th-1**: 8×B200 (179 GiB each), driver 590 (CUDA 13.1), 8 NDR IB NICs at 400 Gb/s (`mlx5_0`–`mlx5_7`) beside `mlx5_8`–`mlx5_9` (200 Gb/s) and `mezz_0`–`mezz_3` (100 Gb/s); 288 cores, 2.2 TiB RAM; the openrt development image (since 2026-10-24 `dev-20261024-d17e6bc1e841`: Ubuntu 24.04, CUDA 13.2.1 toolkit beside Torch's own CUDA 13.0 libraries, Python 3.12 with pip and uv in `/opt/venv`; it has no forward-compatibility driver library, so pods load the host's 590 `libcuda`); tools gcc, nvcc, nsys, ncu, git, rg, jq, gh, glab, rsync, rclone and tmux; `/volume` is a 1 TB GPFS mount with the HF cache in `/volume/.cache`
  - Background jobs use jobs.md's nohup launch on every cluster
- Storage:
  - **`/volume`**: persistent storage shared by the GPU nodes and gate of one cluster; no two clusters share it. **Remote project checkouts and persistent environments must live here**, separately on each cluster that uses them. For directory purposes and usage rules, see jobs.md
  - **`/volume/model`** holds the model checkpoints on every cluster; it is read-only during project work
  - `/root`, `/workspace`, `/mnt/workspace`, and `/tmp` are all pod-local storage — **they are gone after a pod rebuild** and are not shared between nodes. Packages installed into the system Python are lost the same way; environments that need to persist must be built on `/volume`
- Node shells automatically load their cluster's `/volume/.bashrc`, which sets up:
  - PATH
  - `HF_HOME=/volume/.cache` on sh and th (zg was documented as `/volume/.cache/huggingface`)
  - `TMPDIR=/tmp`, node-local, for programs' temporary files and Unix sockets
  - `http(s)_proxy` routing to the public internet through the gate proxy

  Public internet requests use the configured proxy without sourcing anything extra. Verify access to the service needed by the task; one successful endpoint does not establish that every external service is reachable. Use the current internal GitLab endpoint and existing session authentication described in gitlab.md; a historical host's `no_proxy` entry does not make it the current endpoint.
- The nodes run cluster-ops `keepalive.py` (seen on sh-0, sh-1, sh-2 and th-0 on 2026-11-03, earlier on th-1 and zg-0), which keeps the pods from being reclaimed as idle; its docstring says what it loads and how it yields to jobs. While no other process holds any GPU of the node, every GPU carries a `keepalive.py --occupy <GPU UUID>` worker; all of them leave within about 0.25 s of a process opening a CUDA context on any GPU, and they return together after 10 minutes without another process on the node. A GPU is free when no process other than these workers holds it; don't kill them. `scripts/job.py gpus <node>` (jobs.md) ignores them when checking GPUs before a launch.
- th differs:
  - Shells load `/volume/.bashrc` through the openrt image's own hook in `/etc/profile.d/openrt-dev.sh` (!214, `dev-20261018-32eaf362f5de` and later; th's pods run such an image since 2026-10-24). A th session without `HF_HOME` runs an older image or has lost the hook: tell me; meanwhile prefix commands that need `HF_HOME` or the `/volume/.config` Git, gh and glab settings with `. /volume/.bashrc &&`.
  - The pods' ssh login banner warns that pod-local storage (`/tmp`, `/root` and the like) is capped at 240 GiB and that writing more evicts the pod.
  - No gate proxy and no public internet: Hugging Face, GitHub and PyPI time out, while the internal GitLab answers directly over HTTPS. Public files reach th by copying them from the control machine.
- Git identity and credential helpers are already configured through the existing environment. Gates and nodes can set `GIT_CONFIG_GLOBAL=/dev/null` and provide Git settings via `GIT_CONFIG_COUNT`; `GH_CONFIG_DIR` and `GLAB_CONFIG_DIR` alone do not imply file-based credentials are active. Do not unset these settings or replace them with the saved deployment files merely to diagnose access.
- Use HTTPS Git remotes; the internal GitLab is `https://gitlab.iquest-inner.com/` (its HTTP endpoint stopped answering on 2026-10-26; gitlab.md). Nodes cannot reach external Git SSH port 22, so remotes of the form `git@...` will not connect.
- Anonymous GitHub API access hits the egress IP's rate limit (returns 403 rate limit exceeded); use the logged-in `gh api ...` instead
- Node ssh host keys come from pod environment variables and do not change across pod rebuilds. What is more likely to change after a rebuild is the NodePort, which shows up as a connection timeout or refusal (`Connection timed out` / `Connection refused`)
  - When this happens, tell me first; I will provide the new port and then `~/.ssh/config` gets updated
  - If you see `REMOTE HOST IDENTIFICATION HAS CHANGED`, something is wrong — also tell me first, and do not delete entries from known_hosts yourself

## Gates

- Use `sh-gate` for the sh cluster and `zg-gate` for the zg cluster; th has no gate. Each gate shares its cluster's `/volume`; deployment details are in gate.md.
- The control machine's internal GitLab proxy tunnel uses `sh-gate`; see gitlab.md.
