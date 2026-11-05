# Machines, nodes and network

## Control machine (this one)

- Ubuntu 22.04, root, UTC, 4 vCPU / 4 GiB RAM / about 80 GB disk, no GPU; the [validation scope](remote-workflow.md#validation-scope) says what runs here.
- Tools: Python 3.10 without `pip`, `ensurepip` or `gcc`; `uv` in `~/.local/bin`; `git`, `curl`, `jq`, `rsync`, Docker CLI, `gh`, `glab`. Use gate's `rclone`. Docker builds go to the build host (docker-build skill). `glab` came from GitLab's release `.deb`: update it by installing a newer `.deb` checked against `checksums.txt`.
- Its `/volume/.bashrc`, `/volume/.ssh` and `/volume/.config` are saved gate deployment inputs (gate.md), not this machine's configuration; don't source them here.

## GPU nodes and gates

Identify nodes and gates by alias, not hostname, and check a node's driver, cores,
memory and tools on the node itself (`nvidia-smi`, the image). Each GPU has 141 GB
on sh (H200) and zg (H20-3e) and 179 GiB on th (B200). zg's CPFS is its own file
system, not the one PAI jobs mount at `/cpfs01`; it runs on FUSE and can't host
Unix sockets.

- Read alias fields with `ssh -G <alias>`, never the `setenv` ones. ssh multiplexes connections (sockets in `~/.ssh/cm/`); keep under 10 concurrent sessions per node (MaxSessions; bursts of new connections hit MaxStartups with `kex_exchange_identification`). If commands hang after a pod rebuild, `ssh -O exit <alias>` drops the stale master, cutting every session using it.
- On th, InfiniBand traffic belongs on `mlx5_0`–`mlx5_7` (NDR 400 Gb/s); `mlx5_8`–`9` and `mezz_*` are slower.
- Storage: project checkouts and persistent environments live on `/volume`, checkpoints in `/volume/model`. `/root`, `/workspace`, `/tmp` and the system Python are pod-local and vanish with the pod; th's pods are evicted when pod-local storage passes 240 GiB.
- Node shells load `/volume/.bashrc`: PATH, `HF_HOME=/volume/.cache` (sh and th), `TMPDIR=/tmp`, and the gate proxy for the public internet. Check the service you need; one reachable endpoint doesn't prove others are. On th the image's `/etc/profile.d/openrt-dev.sh` loads it: a th shell without `HF_HOME` has lost that hook, so tell the user and prefix commands with `. /volume/.bashrc &&`.
- th has no gate proxy and no public internet (Hugging Face, GitHub, PyPI time out) but reaches the internal GitLab; copy public files there from this machine.
- Git: credentials and identity come from the existing environment (`GIT_CONFIG_COUNT`, `GIT_CONFIG_GLOBAL`); don't unset or replace them. Use HTTPS remotes (gitlab.md); outbound SSH port 22 is closed. Use the logged-in `gh api`: anonymous GitHub API calls hit the egress rate limit.
- Host keys survive pod rebuilds; the NodePort may not, which shows as a connection timeout or refusal until the alias gets the new port. A changed host key (`REMOTE HOST IDENTIFICATION HAS CHANGED`) therefore means something is wrong.
