# /volume, temporary files, background jobs and GPUs

## /volume directory rules
These rules govern each cluster's shared `/volume`; the control machine has independent local storage at the same paths.

### Directory purposes
| Path | Purpose | May modify? |
|---|---|---|
| `/volume/workspace/<project>/...` | Project code (a project may have multiple checkouts, e.g. `vllm-open-mr/vllm-official`) | Only the checkout I specify |
| `/volume/worktree/<repo>/<worktree-name>` | Reusable development/review worktrees and their remote counterparts; names such as `dev-1` or `review` stay fixed across tasks | Only the selected checkout; reuse it as described in [worktrees.md](../implement/worktrees.md) and create its missing remote counterpart for requested remote testing as described in [remote-workflow.md](remote-workflow.md) |
| `/volume/tmp/<topic>-<YYYYMMDD>-<random suffix>/` | All temporary artifacts | Only create your own directories |
| `/volume/model` | Model checkpoints, on every cluster | Read-only |
| `/volume/.cache` on sh and th | i.e. `HF_HOME`, the shared HF cache | HF writes to it automatically when downloading models; do not modify or delete it manually |
| `/volume/cluster-ops` | Deployed ops scripts (`free-gpus.sh`, `gate-proxy.sh`, etc.), one copy per cluster; primary Git checkout on the control machine | Read-only during ordinary project work; ops development happens in the selected local checkout, deployment only for an authorized ops task |
| `/volume/.bashrc`, `.config`, `.ssh`, `.gate_proxy_addr`, `.claude*`, `.codex*`, `.gate-proxy/remote-hosts`, and other hidden files and directories | Shared configuration and credentials; independent saved deployment inputs on the control machine | Do not modify unless the task explicitly requests configuration/ops changes |

### Root directories
- **Do not scatter files in the `/volume`, `/volume/workspace` or `/volume/worktree` roots, and do not create temporary directories there**
- Create new project directories only when I explicitly ask or when setting up the authorized remote counterpart described in remote-workflow.md. Preserve existing worktree paths; the new layout applies to newly created worktrees. Existing configuration and shared directories keep their original purposes.

### Temporary files
- Temporary scripts, logs, PIDs, exit statuses, probes, and experiment artifacts all go in `/volume/tmp/<topic>-<YYYYMMDD>-<random suffix>/`
  - **Artifacts belonging to a checkout also go here**, not into the repo. Existing `scratch/` directories in repos are leftovers from the old rule; do not add anything new to them
  - For each run, create a new directory on the remote with `mktemp -d /volume/tmp/<topic>-$(date +%Y%m%d)-XXXXXX`; retries also get a new directory — do not overwrite or reuse
  - Use the node's date (CST)
- Temporary directories hold only scripts, logs, probes, and similar artifacts — **never copies of repositories**
- **Do not put your own scripts, logs, records or artifacts in the node's `/tmp`**: it is not shared, other nodes cannot read it, and it consumes the overlay disk. `/tmp` is only the programs' `TMPDIR` default (see below)
- Local scratch files are separate from remote storage. Anything a GPU node needs must be present on its shared `/volume`: transfer temporary run scripts/configuration into the allocated remote `/volume/tmp/...` directory with `scp` or quoted ssh stdin, and synchronize repository source through Git. An identical local path alone does not make a file available remotely.

### TMPDIR
- Two kinds of temporary files, two places:
  - **Programs** (library temp files, Unix sockets, pytest base directories): the default `TMPDIR=/tmp`, node-local, which every cluster's `/volume/.bashrc` exports. A CPFS `/volume` cannot host Unix sockets (`bind` fails with `EOPNOTSUPP`), so do not point `TMPDIR` at `/volume`
  - **Your own files** (scripts, logs, PIDs, exit statuses, probes, evidence): the run's `/volume/tmp/<topic>-<YYYYMMDD>-<random suffix>/` directory, as above
- A value explicitly set by the caller takes precedence over the default. To keep a job's program temp files apart, a short directory under `/tmp` may be used (`mktemp -d /tmp/<topic>-XXXXXX`); remove it when the job ends:
  - Python caches the temp directory, so set it before the process starts and make sure child processes inherit it too
  - Do not point `TEMP`, `TMP`, and `TMPDIR` at different directories
  - Do not create temp directories at shell startup
- SSH forwards only explicitly configured environment variables. Use the existing remote session authentication described in gitlab.md; set job-specific overrides explicitly in the remote command or `run.sh`.
- Keep directory names short: libraries append Unix socket paths beneath them, and paths that are too long cause errors. Do not embed the checkout path in the directory name

### Traceability and cleanup
- Record the following in the run record so that artifacts outside the repo are traceable:
  - Absolute checkout path (identical locally and remotely) and execution node
  - Full tested commit SHA, branch or detached HEAD, and working-tree state
  - Launch command, necessary configuration, and artifact directory
- Record configuration from the run's own config file or launch command; keep the environment out of run records, since an `env` filter lets tokens through into shared `/volume/tmp`
- When a job finishes, delete only temp directories you created that no process is still using
- When results need to be kept, list the paths in the summary and say which ones can be deleted

## Long-running background jobs
- Write a `run.sh` in the run directory that uses trap at the top to record the real exit code. **An EXIT trap alone is not enough**: when `run.sh` is killed by SIGTERM it records `0` and is treated as success. Also convert signals to a `128+N` exit:

  ```bash
  trap 'echo $? > <run_dir>/exit.status' EXIT
  trap 'exit 143' TERM; trap 'exit 130' INT; trap 'exit 129' HUP
  ```

  Keep the job command in the foreground (no `cmd & wait`, otherwise the job becomes an orphan after `run.sh` exits and keeps holding the GPU). When selecting GPUs by their `nvidia-smi` index, export `CUDA_DEVICE_ORDER=PCI_BUS_ID` with `CUDA_VISIBLE_DEVICES`; CUDA's default order can differ. Then launch it like this:

  ```bash
  printf -v remote_start \
    'cd -- %q && { nohup bash %q > %q 2>&1 </dev/null & printf "%%s\\n" "$!" > %q; }' \
    "$(pwd -P)" "$run_dir/run.sh" "$run_dir/run.log" "$run_dir/run.pid"
  ssh <node> "$remote_start"
  ```

- A successful launch only means the job was submitted; **the job's result is determined by `exit.status`**. If the process has exited but there is no status file, treat it as a failure
- If ssh disconnects or returns non-zero, the job may already have started: first check the log, status file, and processes on the node, and only after confirming nothing is running retry with a new directory
- Logs are on the shared disk, so `tail` them from any node in the same cluster. Stop polling once success or failure is confirmed; if the job misbehaves or makes no progress for a long time, investigate the cause rather than waiting indefinitely

## GPU usage
- Nodes are shared by multiple people: only stop processes that belong to this job or that I have explicitly said may be stopped; do not kill in bulk by process name; do not occupy nodes I have not specified
- Free GPU memory with `/volume/cluster-ops/free-gpus.sh`; do a dry run first, and only after confirming every candidate process may be stopped, run it again without `DRY_RUN=1`
  - This script ssh-es to the target nodes itself, and **nodes cannot ssh to each other**, so it must **run on this machine**: read the script contents from the target cluster's `sh-0`, `zg-0` or `th-0` and pipe them into local bash
  - If run on a node, it silently does nothing and still returns 0
  - Example:

  ```bash
  node=sh-0    # zg-0 or th-0 for a checkout on those clusters.
  owner=$(ssh "$node" "cd -- $(printf %q "$(pwd -P)") && pwd -P")    # physical path of the project
  ssh "$node" 'cat /volume/cluster-ops/free-gpus.sh' | DRY_RUN=1 OWNER_CWD="$owner" bash -s -- <node...>
  ```

  - The script selects compute processes whose cwd is in `OWNER_CWD` or its subdirectories and marks them `WOULD kill`; other processes are marked `LEAVE`
  - Pass the physical path (`pwd -P`), otherwise symlinks cause missed matches
  - The script swallows ssh errors: **no output from the dry run does not mean there are no processes on the node**; cross-check separately with `ssh <node> nvidia-smi`
  - A single checkout may have multiple jobs. Confirm each one against the PID and launch command recorded for the job; if the candidate list mixes in processes from other jobs, do not clean them up as a batch
  - By default the script watches GPU memory usage across all GPUs on the node, so it may time out because of other people's jobs. **Do not widen the cleanup scope because of this**; judge the cleanup result by whether the target processes exited and whether memory on the relevant GPUs dropped
- Before launching, confirm the GPUs to be used are free and have enough free memory, e.g. with `nvidia-smi --query-gpu=index,uuid,memory.free --format=csv` and `nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv`, then each PID's `/proc/<pid>/cmdline`
  - An idle GPU still shows 100% utilization and a `keepalive.py --occupy <GPU UUID>` process (cwd `/`): it yields to a new job by itself (machines.md), so count only other processes and their memory, and never stop the workers; `free-gpus.sh` leaves them whatever the selector (`LEAVE ... keepalive's worker`)
  - The workers' teardown overlaps a job's first 0.1–0.2 s after its CUDA contexts appear; time only after warm-up
- When looking up processes with `pgrep -f` or `ps | grep`, the `bash -c` process that ssh runs on the remote will itself match; exclude it when counting
