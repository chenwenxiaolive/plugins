# /volume, temporary files, background jobs and GPUs

## /volume directories

- `/volume/.cache` on sh and th is `HF_HOME`, the shared Hugging Face cache: read-only except for HF downloads.

## Temporary files

- Each run gets a new directory: `mktemp -d /volume/tmp/<topic>-$(date +%Y%m%d)-XXXXXX` on the node (CST date); a retry gets another. It holds the run's scripts, logs, PIDs, exit statuses and evidence, never repository copies.
- A node's `/tmp` is not shared and fills the pod's overlay disk; it is only the programs' `TMPDIR` (library temp files, Unix sockets), which `/volume/.bashrc` sets to `/tmp`. Keep it there: zg's CPFS runs on FUSE and can't host Unix sockets. A job that needs its own `TMPDIR` gets a short `mktemp -d /tmp/<topic>-XXXXXX`, set before the process starts and removed afterwards; long paths break socket names.
- A file the node needs must reach its `/volume` by `scp` or ssh stdin.

## Background jobs

- Write `run.sh` in the run directory. Its first lines record the real exit code; an EXIT trap alone records `0` when `run.sh` is killed by SIGTERM:

  ```bash
  trap 'echo $? > <run_dir>/exit.status' EXIT
  trap 'exit 143' TERM; trap 'exit 130' INT; trap 'exit 129' HUP
  ```

  Keep the job in the foreground: `cmd & wait` orphans it, and the orphan keeps holding the GPU. When selecting GPUs by `nvidia-smi` index, export `CUDA_DEVICE_ORDER=PCI_BUS_ID` with `CUDA_VISIBLE_DEVICES`; CUDA's default order can differ.
  ssh passes only configured environment variables, so set what the job needs in `run.sh`.
- OSS credentials for jobs: `source /volume/.config/oss/<account>.env` in `run.sh` (`qr` for bucket skyinfer-qr, `zg` for skyinfer-zg); each file sets `OSS_ACCESS_KEY_ID`, `OSS_ACCESS_KEY_SECRET`, `OSS_ENDPOINT` and `OSS_REGION`. The control machine's copy is the source, deployed with `profile.sh push <gate>` ([gate.md](gate.md)).
- Launch it from the checkout:

  ```bash
  printf -v remote_start \
    'cd -- %q && { nohup bash %q > %q 2>&1 </dev/null & printf "%%s\\n" "$!" > %q; }' \
    "$(pwd -P)" "$run_dir/run.sh" "$run_dir/run.log" "$run_dir/run.pid"
  ssh <node> "$remote_start"
  ```

- `exit.status` decides the result; a process gone without it failed. After an ssh error the job may still have started: check the log, status and processes before retrying in a new directory.

## GPUs

### Machine allocation

Workers on the control machine share a whole-machine table: node alias → worker
session ID. Run [scripts/allocations.py](scripts/allocations.py) there, from the
installed skill, so every checkout uses the same file:

```sh
python3 ~/.agents/skills/gpu-cluster/scripts/allocations.py list
python3 ~/.agents/skills/gpu-cluster/scripts/allocations.py claim sh-1
python3 ~/.agents/skills/gpu-cluster/scripts/allocations.py release sh-1
```

- Before asking for GPUs, read the table, check an unregistered candidate's GPU
  processes below, and recommend a specific machine. Claim only after the user
  confirms it. A listed machine belongs to that worker even between GPU runs.
- Claims cover the whole machine and refuse an existing different owner. If
  another worker claims it first, recommend another machine for confirmation.
  Existing allocation and further runs on that machine need no repeated approval.
- `claim` and `release` use `HC_TERMINAL_ID`. Outside Herdr, pass
  `--worker <session-id>` consistently. Normal release uses your own identity.
- Once the task no longer needs GPUs and its jobs have ended, release the machine
  without another confirmation. Pausing, finishing one run or ending one answer
  does not release it. Later GPU work after release needs a new confirmed claim.
- An exited worker leaves its record intact. After checking for leftover jobs and
  obtaining the user's confirmation, release with `--worker <recorded-owner>`.
  This removes only that owner's record, not a later replacement's.
- The table records allocation, not authorization or live GPU use. The worker
  checks confirmation and job completion; the script neither probes nor stops
  processes. Enter existing assignments with their owners when first adopting it.

The control-machine directory is `~/.local/state/gpu-cluster/allocations/`.
Each machine has a plain file named after its canonical alias, containing its
worker ID. The script holds `flock` on the fixed `.lock` file only while reading
or changing records; it publishes complete owner files by rename. Keep `.lock`
in place. An available file lock does not mean a machine is unallocated: its
owner file persists until release. `--directory <path>` isolates tests; normal
workers use the default. An absent entry never establishes that GPUs are idle.
Use canonical `sh-<n>`, `zg-<n>` and `th-<n>` aliases from [machines.md](machines.md).

### GPU checks

- Before launching, confirm the GPUs are free with enough memory: `nvidia-smi --query-gpu=index,uuid,memory.free --format=csv` and `nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv`, then each PID's `/proc/<pid>/cmdline`.
  - The nodes run cluster-ops `keepalive.py` so pods aren't reclaimed as idle: while no other process holds a GPU, each GPU carries a `keepalive.py --occupy <GPU UUID>` worker (cwd `/`) at 100% utilization. The workers leave within about 0.25 s of a CUDA context opening, so time a job only after warm-up, and return after 10 idle minutes. They and their memory count as free; never stop them.
- Over ssh, `pgrep -f <pattern>` also matches the `bash -c` running it; check each PID's command before stopping it.
- To free GPU memory, use `/volume/cluster-ops/free-gpus.sh`. It ssh-es to the nodes itself, so run it here; on a node it silently does nothing and returns 0. Dry-run first:

  ```bash
  node=<node>    # any reachable node of the job's cluster
  owner=$(ssh "$node" "cd -- $(printf %q "$(pwd -P)") && pwd -P")
  ssh "$node" 'cat /volume/cluster-ops/free-gpus.sh' | DRY_RUN=1 OWNER_CWD="$owner" bash -s -- <node...>
  ```

  - It marks compute processes whose cwd is under `OWNER_CWD` `WOULD kill`, others and keepalive workers `LEAVE`. Check every candidate against the job's PID and command, then rerun without `DRY_RUN=1`.
  - It swallows ssh errors, so an empty dry run proves nothing; cross-check with `nvidia-smi`. It waits on memory across all GPUs and may time out on others' jobs: judge by your processes exiting, never widen the scope.
