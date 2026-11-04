---
name: gpu-cluster
description: Operating this setup's GPU nodes, gates and internal GitLab. Use before a task's first ssh or remote command, checkout sync, remote run or background job, GPU use, /volume temporary file, GitLab API or glab call, push to the internal GitLab, or gate deployment.
---

# GPU cluster

The rules in `~/.claude/CLAUDE.md` apply to every task. This page holds the facts
behind them that you can't discover yourself.

## Machines

| Cluster | Nodes | Gate | Shared `/volume` | GPUs per node |
|---|---|---|---|---|
| sh | `sh-0`, `sh-1`, `sh-2` | `sh-gate` | 50 TB GPFS | 8×H200 141 GB, driver 580 |
| zg | `zg-0`, `zg-1` | `zg-gate` | 3 PB CPFS (FUSE; no Unix sockets) | 8×H20-3e 141 GB, driver 570 (CUDA 13 via forward compatibility) |
| th | `th-0`, `th-1` | none | 1 TB GPFS | 8×B200 179 GiB, driver 590 |

- This control machine: Python 3.10 without `pip` or `gcc`, `uv` in `~/.local/bin`, plus `git`, `gh`, `glab`, `jq`, `rsync` and the Docker CLI. Its `/volume/.bashrc`, `.ssh` and `.config` are the saved inputs for gate deployments, not its own configuration.
- ssh multiplexes per alias. Keep under 10 concurrent sessions per node: MaxSessions is 10, and bursts of new connections fail with `kex_exchange_identification`. If commands hang after a pod rebuild, `ssh -O exit <alias>` drops the stale master. A rebuild can change the NodePort (timeout or refusal) while host keys stay.
- sh and zg run the NVIDIA PyTorch image (pip, uv, gcc, rg, gh, glab, rclone; no tmux). th runs the openrt development image (Ubuntu 24.04, CUDA 13.2 toolkit beside Torch's CUDA 13.0, Python 3.12 venv in `/opt/venv`, nvcc, nsys, ncu, tmux). InfiniBand: sh 8 mlx5 NICs, zg 4 bonded, th `mlx5_0`–`mlx5_7` at 400 Gb/s (`mlx5_8`–`9` and `mezz_*` are slower).
- Node shells load `/volume/.bashrc`: PATH, `HF_HOME=/volume/.cache` (sh and th), `TMPDIR=/tmp`, and the gate proxy to the public internet. On th the image's `/etc/profile.d/openrt-dev.sh` loads it; a th shell without `HF_HOME` has lost that hook, so prefix commands with `. /volume/.bashrc &&` and tell the user.
- th has no public internet (Hugging Face, GitHub and PyPI time out) but reaches the internal GitLab; copy public files there from this machine.
- `/root`, `/tmp` and the system Python are pod-local and vanish with the pod, so persistent environments live on `/volume`. th pods are evicted past 240 GiB of pod-local data.
- Git credentials and identity come from the environment (`GIT_CONFIG_COUNT`, `GIT_CONFIG_GLOBAL`); don't unset or replace them. Remotes use HTTPS, because outbound port 22 is closed. Anonymous GitHub API calls hit the egress rate limit, so use `gh api`.

## Checkouts and validation

### Validation scope

- This machine runs only light static checks. Project tests (small ones included), builds, formatters and linters run in the node checkout's environment.
- CPU-only work may run on the cluster's `-0` node with `CUDA_VISIBLE_DEVICES=` (empty); GPU work needs the node the user named.
- To format a local file, pipe it through the node environment's tools with `bash -o pipefail`, and use the output only if the command succeeds.

### Checkouts

- Remote project commands start with `cd -- $(printf %q "$(pwd -P)")`: a Herdr worktree's `$PWD` goes through `~/.herdr/worktrees`, which the nodes don't have. Use `sh-0`, `zg-0` or `th-0` for Git and file work; each cluster's `/volume` holds one copy of a checkout.
- Update a remote checkout only with `git fetch` and `git merge --ff-only <sha>` (or `git switch --detach <sha>` for a review checkout), and only when it is clean and idle. Idle means no process on any machine of that cluster has its working directory in it (`/proc/*/cwd`), and run records show no job using it. A detached HEAD must first be in a fetched origin branch.
- For requested remote testing of a herdr worktree, create the missing counterpart at the same path with Git: a clone, or a worktree of an existing clone.
- Before validating a uv project, `uv sync --locked --dry-run` must show no dependency changes. Sync only while no job uses the environment.

## Jobs and GPUs

- `run.sh` records the real exit code. An EXIT trap alone writes `0` when the script is killed by SIGTERM:

  ```bash
  trap 'echo $? > <run_dir>/exit.status' EXIT
  trap 'exit 143' TERM; trap 'exit 130' INT; trap 'exit 129' HUP
  ```

  Keep the job in the foreground: `cmd & wait` leaves an orphan holding the GPU. Start it from the checkout with `nohup bash <run_dir>/run.sh > <run_dir>/run.log 2>&1 < /dev/null &`. ssh passes only configured variables, so set what the job needs in `run.sh`. To select GPUs by `nvidia-smi` index, export `CUDA_DEVICE_ORDER=PCI_BUS_ID` with `CUDA_VISIBLE_DEVICES`.
- Keep `TMPDIR` on `/tmp`, with short paths: CPFS can't host Unix sockets, and long socket paths fail.
- Idle GPUs carry `keepalive.py --occupy <GPU UUID>` workers (cwd `/`, 100% utilization). They leave within about 0.25 s of a CUDA context opening on any GPU, return after 10 idle minutes, and count as free; never stop them. Their exit overlaps a job's first 0.1–0.2 s, so time only after warm-up.
- `/volume/cluster-ops/free-gpus.sh` frees GPU memory but must run here, since nodes can't ssh to each other: `ssh <node> 'cat /volume/cluster-ops/free-gpus.sh' | DRY_RUN=1 OWNER_CWD=<physical checkout path> bash -s -- <nodes>`. It marks matching processes `WOULD kill` and leaves keepalive workers alone. It swallows ssh errors, so an empty result proves nothing; check `nvidia-smi` too.

## GitLab

- The endpoint is `https://gitlab.iquest-inner.com/`. `gitlab-cn-beijing.siflow.cn` in old files is historical; use a per-command URL override (such as `MEGATRON_REPO_URL`) rather than editing pins.
- Authentication is already configured here and on the nodes; `glab auth status` showing no login means nothing. Test with a read-only request instead.
- Run `glab` in the checkout so it infers the project. Notes come newest first, 20 per page: `glab api --paginate 'projects/:id/issues/<iid>/notes?sort=asc&per_page=100'`. `glab api` has no `--jq`.
- From this machine, GitLab goes through `sh-gate`'s proxy over `gate-proxy-tunnel.service` (`127.0.0.1:18080`), which `glab` and Git already use. For raw requests, use `curl --proxy http://127.0.0.1:18080 --noproxy '' <url>`. If access fails, check that service first.
- A closing keyword (`closes`, `fixes`, `resolves`) in a commit merged to the default branch closes the issue; for one item of a tracking issue write `#<N> item <X>`.
- OSS credentials for jobs: `source /volume/.config/oss/<account>.env` in `run.sh` (`qr` for bucket skyinfer-qr, `zg` for skyinfer-zg).

## Gates

- cluster-ops is maintained in `/volume/cluster-ops` here (origin `https://gitlab.iquest-inner.com/xqing/cluster-ops.git`) and deployed at the same path on each cluster.
- `profile.sh push <gate> [--dry-run]` deploys the saved `.config` (including OSS files) to a gate. `bootstrap-gate.sh <alias> --dry-run` previews a new gate deployment.
- `/volume/.gate-proxy/remote-hosts` is persistent per-cluster configuration, not runtime state. A gate may run an older image: check `rclone version` there.
