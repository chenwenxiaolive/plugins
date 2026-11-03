# Machines, nodes and network

## Control machine (this one)

- Ubuntu 22.04, root, UTC, 4 vCPU / 4 GiB RAM / about 80 GB disk, no GPU. Edit, commit and push the selected checkout here; keep work light ([validation scope](remote-workflow.md#validation-scope)). Its `/volume` is local disk, not the nodes' storage.
- Tools: Python 3.10 without `pip`, `ensurepip`, `uv` or `gcc`; `git`, `curl`, `jq`, `rsync`, Docker CLI, `gh`, `glab`. Use gate's `rclone`. Docker builds go to the build host (docker-build skill). `glab` came from GitLab's release `.deb`: update it by installing a newer `.deb` checked against `checksums.txt`.
- Its `/volume/.bashrc`, `/volume/.ssh` and `/volume/.config` are saved gate deployment inputs (gate.md), not this machine's configuration; don't source them here.

## GPU nodes and gates

| Cluster | Nodes | Gate | Shared `/volume` | GPUs per node |
|---|---|---|---|---|
| sh | `sh-0`, `sh-1`, `sh-2` | `sh-gate` | 50 TB GPFS | 8×H200 141 GB, driver 580 |
| zg | `zg-0`, `zg-1` | `zg-gate` | 3 PB CPFS (FUSE; no Unix sockets) | 8×H20-3e 141 GB, driver 570 (CUDA 13 via forward compatibility) |
| th | `th-0`, `th-1` | none | 1 TB GPFS | 8×B200 179 GiB, driver 590 |

- Connect with the `~/.ssh/config` aliases; read fields with `ssh -G <alias>`, never the `setenv` ones. ssh multiplexes connections (sockets in `~/.ssh/cm/`); keep under 10 concurrent sessions per node (MaxSessions; bursts of new connections hit MaxStartups with `kex_exchange_identification`). If commands hang after a pod rebuild, `ssh -O exit <alias>` drops the stale master, cutting every session using it.
- The nodes and gates are k8s pods in CST (UTC+8); identify them by alias, not hostname.
- sh and zg: 192 cores, 2 TiB RAM, NVIDIA PyTorch image with Python, pip, uv, gcc, git, rg, jq, gh, glab, rsync, rclone; no tmux. th: 288 cores, 2.2 TiB RAM, the openrt development image (Ubuntu 24.04, CUDA 13.2 toolkit beside Torch's CUDA 13.0, Python 3.12 with pip and uv in `/opt/venv`, nvcc, nsys, ncu, tmux). InfiniBand: sh 8 mlx5 NICs, zg 4 bonded, th 8 NDR 400 Gb/s (`mlx5_0`–`mlx5_7`; `mlx5_8`–`9` and `mezz_*` are slower). Check `nvidia-smi` and the image for current details.
- Storage: each cluster's `/volume` is shared by its nodes and gate and by no other cluster; project checkouts and persistent environments live there. `/volume/model` holds checkpoints (read-only). `/root`, `/workspace`, `/tmp` and the system Python are pod-local and vanish with the pod. th's pods are evicted when pod-local storage passes 240 GiB.
- Node shells load `/volume/.bashrc`: PATH, `HF_HOME=/volume/.cache` (sh and th), `TMPDIR=/tmp`, and the gate proxy for the public internet. Check the service you need; one reachable endpoint doesn't prove others are. On th the image's `/etc/profile.d/openrt-dev.sh` loads it: a th shell without `HF_HOME` has lost that hook, so tell the user and prefix commands with `. /volume/.bashrc &&`.
- th has no gate proxy and no public internet (Hugging Face, GitHub, PyPI time out) but reaches the internal GitLab; copy public files there from this machine.
- The nodes run cluster-ops `keepalive.py`, which keeps pods from being reclaimed as idle. While no other process holds a GPU of the node, every GPU carries a `keepalive.py --occupy <GPU UUID>` worker; they leave within about 0.25 s of a CUDA context opening on any GPU and return after 10 idle minutes. A GPU is free when only these workers hold it; never stop them (jobs.md).
- Git: credentials and identity come from the existing environment (`GIT_CONFIG_COUNT`, `GIT_CONFIG_GLOBAL`); don't unset or replace them. Use HTTPS remotes (gitlab.md); outbound SSH port 22 is closed. Use the logged-in `gh api`: anonymous GitHub API calls hit the egress rate limit.
- Host keys survive pod rebuilds; the NodePort may not, showing as a connection timeout or refusal. Tell the user and wait for the new port. `REMOTE HOST IDENTIFICATION HAS CHANGED` means something is wrong: tell the user and leave `known_hosts` alone.
- Gates: `sh-gate` and `zg-gate` share their cluster's `/volume` (gate.md); this machine's GitLab tunnel runs through `sh-gate`.
