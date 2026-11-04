# /volume, temporary files, background jobs and GPUs

## /volume directories

Each cluster shares its own `/volume`; the control machine has independent local storage at the same paths.

| Path | Purpose | May modify? |
|---|---|---|
| `/volume/workspace/<project>/...` | Project checkouts | Only the selected checkout |
| `/volume/worktree/<repo>/<name>` | Reusable worktrees such as `dev-1` and their remote counterparts | Only the selected checkout ([implement](../implement/SKILL.md#start-or-resume)) |
| `/volume/tmp/<topic>-<YYYYMMDD>-<suffix>/` | All your temporary files | Only directories you created |
| `/volume/model` | Model checkpoints | Read-only |
| `/volume/.cache` on sh and th | `HF_HOME`, the shared HF cache | Only through HF downloads |
| `/volume/cluster-ops` | Deployed ops scripts (`free-gpus.sh`, `keepalive.py`, ...); the Git checkout is on the control machine | Read-only outside an authorized ops task |
| `/volume/.bashrc`, `.config`, `.ssh` and other hidden files | Shared configuration and credentials | Only on an explicit ops request |

## Temporary files

- Each run gets a new directory: `mktemp -d /volume/tmp/<topic>-$(date +%Y%m%d)-XXXXXX` on the node (CST date); a retry gets another. It holds the run's scripts, logs, PIDs, exit statuses and evidence, never repository copies.
- A node's `/tmp` is not shared and fills the pod's overlay disk; it is only the programs' `TMPDIR` (library temp files, Unix sockets), which `/volume/.bashrc` sets to `/tmp`. Keep it there: CPFS cannot host Unix sockets. A job that needs its own `TMPDIR` gets a short `mktemp -d /tmp/<topic>-XXXXXX`, set before the process starts and removed afterwards; long paths break socket names.
- A file the node needs must reach its `/volume` by `scp` or ssh stdin; a matching local path is a different disk.
- Each run's record names the checkout path, node, full SHA, branch, working-tree state, launch command and configuration.

## Background jobs

- Write `run.sh` in the run directory. Its first lines record the real exit code; an EXIT trap alone records `0` when `run.sh` is killed by SIGTERM:

  ```bash
  trap 'echo $? > <run_dir>/exit.status' EXIT
  trap 'exit 143' TERM; trap 'exit 130' INT; trap 'exit 129' HUP
  ```

  Keep the job in the foreground: `cmd & wait` orphans it, and the orphan keeps holding the GPU. When selecting GPUs by `nvidia-smi` index, export `CUDA_DEVICE_ORDER=PCI_BUS_ID` with `CUDA_VISIBLE_DEVICES`; CUDA's default order can differ.
  ssh passes only configured environment variables, so set what the job needs in `run.sh`.
- Launch it from the checkout:

  ```bash
  printf -v remote_start \
    'cd -- %q && { nohup bash %q > %q 2>&1 </dev/null & printf "%%s\\n" "$!" > %q; }' \
    "$(pwd -P)" "$run_dir/run.sh" "$run_dir/run.log" "$run_dir/run.pid"
  ssh <node> "$remote_start"
  ```

- `exit.status` decides the result; a process gone without it failed. After an ssh error the job may still have started: check the log, status and processes before retrying in a new directory.

## GPUs

- Before launching, confirm the GPUs are free with enough memory: `nvidia-smi --query-gpu=index,uuid,memory.free --format=csv` and `nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv`, then each PID's `/proc/<pid>/cmdline`.
  - `keepalive.py --occupy <GPU UUID>` workers (cwd `/`) hold idle GPUs at 100% utilization and leave by themselves when a job starts (machines.md). They and their memory count as free; never stop them. Time only after warm-up: their teardown overlaps a job's first 0.1–0.2 s.
- Over ssh, `pgrep -f <pattern>` also matches the `bash -c` running it; check each PID's command before stopping it.
- To free GPU memory, use `/volume/cluster-ops/free-gpus.sh`. It ssh-es to the nodes itself, so run it here; on a node it silently does nothing and returns 0. Dry-run first:

  ```bash
  node=<node>    # any reachable node of the job's cluster
  owner=$(ssh "$node" "cd -- $(printf %q "$(pwd -P)") && pwd -P")
  ssh "$node" 'cat /volume/cluster-ops/free-gpus.sh' | DRY_RUN=1 OWNER_CWD="$owner" bash -s -- <node...>
  ```

  - It marks compute processes whose cwd is under `OWNER_CWD` `WOULD kill`, others and keepalive workers `LEAVE`. Check every candidate against the job's PID and command, then rerun without `DRY_RUN=1`.
  - It swallows ssh errors, so an empty dry run proves nothing; cross-check with `nvidia-smi`. It waits on memory across all GPUs and may time out on others' jobs: judge by your processes exiting, never widen the scope.
