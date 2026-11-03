#!/usr/bin/env python3
"""Check GPUs on a node and run background jobs there from the local checkout.

Run in the selected local checkout; the job runs in its remote counterpart (same path).

  job.py gpus NODE [--gpus LIST|all] [--min-free-mib N]
        each GPU with the processes holding it. cluster-ops keepalive workers
        (`keepalive.py --occupy`) are ignored: they yield when a job opens a CUDA context.
        Exit 0 when the selected GPUs (default: all) are free.
  job.py start NODE --topic NAME [--gpus LIST|all] -- COMMAND [ARG...]
        refuse busy GPUs; create /volume/tmp/NAME-<node date>-XXXXXX with run.sh (exit-status
        traps, cd to the checkout, PCI-ordered CUDA_VISIBLE_DEVICES for a list) and record.txt (checkout,
        node, branch, commit, tree state, GPUs, command); launch it with nohup from the
        checkout and print the run directory. Use `bash -c '...'` for shell syntax.
  job.py status NODE RUN_DIR
        succeeded (exit 0), failed (exit 1) or running (exit 3), with the log tail.
        NODE must be the launch node, which record.txt names.
  job.py wait NODE RUN_DIR [--timeout S] [--interval S]
        poll status until the job ends; exit 3 if it is still running at the timeout.

Exit 2 means a command failed and the state is unknown. GPU jobs need a node the user named.
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
import time


KEEPALIVE = re.compile(r"keepalive\.py\b.*--occupy")

# Capture the process query before parsing so its failure is not hidden behind the loop.
GPU_QUERY = r"""nvidia-smi --query-gpu=index,uuid,memory.used,memory.total --format=csv,noheader,nounits && echo -- &&
apps=$(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits) &&
printf '%s\n' "$apps" | while IFS=', ' read -r uuid pid mem; do
  printf '%s\t%s\t%s\t%s\t%s\n' "$uuid" "$pid" "$mem" "$(readlink "/proc/$pid/cwd" 2>/dev/null)" \
    "$(tr '\0\n\t' '   ' < "/proc/$pid/cmdline" 2>/dev/null | cut -c1-160)"
done"""

# The job is found by its unique run.sh path, so a missing run.pid does not make it look gone.
STATUS = r"""cd -- %s || exit 1
sed -n 's/^node: //p' record.txt
code=$(cat exit.status 2>/dev/null)
case $code in
  [0-9]*) echo "status $code" ;;
  *) state=gone
     for p in /proc/[0-9]*; do
       c=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null) || continue
       case $c in *"$PWD/run.sh"*) state=running; break ;; esac
     done
     # The trap writes exit.status before the job exits, so reread it if the job ended mid-scan.
     code=$(cat exit.status 2>/dev/null)
     case $state:$code in gone:[0-9]*) state="status $code" ;; esac
     echo "$state" ;;
esac
tail -n 20 run.log 2>/dev/null"""


class Failure(Exception):
    """A command could not run; the state is unknown."""


def ssh(node, script, stdin=None, timeout=120):
    # Without input, give ssh /dev/null so it never reads (or waits on) the caller's stdin.
    try:
        result = subprocess.run(["ssh", "-o", "BatchMode=yes", node, script], capture_output=True, text=True,
                                timeout=timeout,
                                **({"input": stdin} if stdin is not None else {"stdin": subprocess.DEVNULL}))
    except subprocess.TimeoutExpired:
        raise Failure(f"ssh {node}: no answer within {timeout:.0f} s") from None
    if result.returncode:
        raise Failure(f"ssh {node}: {result.stderr.strip() or result.stdout.strip() or f'exit {result.returncode}'}")
    return result.stdout


def gpu_state(node):
    """Return [{index, uuid, total, free, others}] with keepalive workers' memory counted as free."""
    gpu_lines, _, app_lines = ssh(node, GPU_QUERY).partition("--\n")
    gpus = {}
    for line in gpu_lines.splitlines():
        index, uuid, used, total = [field.strip() for field in line.split(",")]
        gpus[uuid] = {"index": index, "uuid": uuid, "total": int(total), "free": int(total) - int(used), "others": []}
    for line in app_lines.splitlines():
        fields = line.split("\t")
        if len(fields) != 5 or fields[0] not in gpus:
            continue
        uuid, pid, mem, cwd, cmdline = fields
        mib = int(mem) if mem.isdigit() else 0
        if KEEPALIVE.search(cmdline):
            gpus[uuid]["free"] += mib
        else:
            gpus[uuid]["others"].append((pid, mib, cwd or "?", cmdline.strip() or "(process not visible)"))
    return sorted(gpus.values(), key=lambda gpu: int(gpu["index"]))


def check_gpus(node, selection, min_free_mib):
    """Print every GPU; return True when the selected ones are free with enough memory."""
    gpus = gpu_state(node)
    wanted = {gpu["index"] for gpu in gpus} if selection == "all" else set(selection.split(","))
    unknown = wanted - {gpu["index"] for gpu in gpus}
    if unknown:
        raise Failure(f"{node} has no GPU {', '.join(sorted(unknown))}")
    ok = True
    for gpu in gpus:
        short = gpu["free"] < min_free_mib
        state = "busy" if gpu["others"] else "low memory" if short else "free"
        mark = "*" if gpu["index"] in wanted else " "
        print(f"{mark} GPU {gpu['index']} {state}: {gpu['free']} of {gpu['total']} MiB free")
        for pid, mib, cwd, cmdline in gpu["others"]:
            print(f"      pid {pid} ({mib} MiB) in {cwd}: {cmdline}")
        if gpu["index"] in wanted and state != "free":
            ok = False
    return ok


def start(args, checkout):
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,40}", args.topic):
        raise Failure("--topic must be 1-40 letters, digits, dots, dashes or underscores")
    if not args.command:
        raise Failure("give the job command after --")
    if args.gpus and not check_gpus(args.node, args.gpus, 0):
        print("FAIL: the selected GPUs are not free; nothing was started")
        return 1
    q, command = shlex.quote, shlex.join(args.command)
    run_dir = ssh(args.node, f'mktemp -d "/volume/tmp/{args.topic}-$(date +%Y%m%d)-XXXXXX"').strip()
    # PCI bus order makes CUDA number the GPUs as nvidia-smi does, so the checked GPUs are the ones used.
    visible = (f"export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES={q(args.gpus)}\n"
               if args.gpus and args.gpus != "all" else "")
    status_file = q(run_dir + "/exit.status")
    run_sh = (
        "#!/usr/bin/env bash\n"
        f"trap 'echo $? > {status_file}.tmp && mv {status_file}.tmp {status_file}' EXIT\n"
        "trap 'exit 143' TERM; trap 'exit 130' INT; trap 'exit 129' HUP\n"
        f"cd -- {q(checkout)} || exit 1\n{visible}{command}\n"
    )
    ssh(args.node, f"cat > {q(run_dir + '/run.sh')}", stdin=run_sh)
    record = (
        f"cd -- {q(checkout)} && {{ printf 'checkout: %s\\n' \"$(pwd -P)\"; printf 'node: %s\\n' {q(args.node)}; "
        "printf 'branch: %s\\n' \"$(git symbolic-ref --short -q HEAD || echo '(detached)')\"; "
        "printf 'commit: %s\\n' \"$(git rev-parse HEAD)\"; "
        "printf 'working tree: %s changed paths\\n' \"$(git status --porcelain --untracked-files=all | wc -l)\"; "
        f"printf 'gpus: %s\\n' {q(args.gpus or 'none')}; printf 'command: %s\\n' {q(command)}; "
        f"printf 'started: %s\\n' \"$(date -Is)\"; }} > {q(run_dir + '/record.txt')}"
    )
    ssh(args.node, record)
    launch = (
        f"cd -- {q(checkout)} && {{ nohup bash {q(run_dir + '/run.sh')} > {q(run_dir + '/run.log')} 2>&1 </dev/null & "
        f"printf '%s\\n' \"$!\" > {q(run_dir + '/run.pid')}; cat {q(run_dir + '/run.pid')}; }}"
    )
    try:
        pid = ssh(args.node, launch).strip()
    except Failure as error:
        print(f"FAIL: {error}\nThe job may have started: run `job.py status {args.node} {run_dir}` before retrying in a new directory.")
        return 2
    print(f"started: {args.node} pid {pid}\nrun directory: {run_dir}\nrecord: {run_dir}/record.txt\n"
          f"next: job.py wait {args.node} {run_dir}")
    return 0


def status(node, run_dir, quiet=False, timeout=120):
    """Return 0 succeeded, 1 failed, 3 running; print the outcome and log tail."""
    lines = ssh(node, STATUS % shlex.quote(run_dir), timeout=timeout).split("\n")
    launch_node, state, log = lines[0], lines[1], "\n".join(lines[2:]).rstrip()
    if (state == "running" or state == "gone") and launch_node != node:
        raise Failure(f"{run_dir} was launched on {launch_node}; query that node")
    if state == "running" and quiet:
        return 3
    print(f"log tail ({run_dir}/run.log):\n  " + log.replace("\n", "\n  ") if log else "log is empty")
    if state == "running":
        print(f"running: {run_dir}")
        return 3
    finished = re.fullmatch(r"status (\d+)", state)
    if finished and finished[1] == "0":
        print(f"succeeded: {run_dir}")
        return 0
    print(f"failed: {run_dir} " + (f"exited with {finished[1]}" if finished else "is gone without exit.status"))
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command_name", required=True)
    gpus = commands.add_parser("gpus")
    gpus.add_argument("node")
    gpus.add_argument("--gpus", default="all", help="comma-separated indices or all (default)")
    gpus.add_argument("--min-free-mib", type=int, default=0)
    starter = commands.add_parser("start")
    starter.add_argument("node")
    starter.add_argument("--topic", required=True)
    starter.add_argument("--gpus", help="comma-separated indices or all; omit for a CPU job")
    for name in ("status", "wait"):
        command = commands.add_parser(name)
        command.add_argument("node")
        command.add_argument("run_dir")
    commands.choices["wait"].add_argument("--timeout", type=int, default=540)
    commands.choices["wait"].add_argument("--interval", type=int, default=30)
    # The job command follows the first `--`; argparse would otherwise read its options.
    argv, job_command = sys.argv[1:], []
    if argv[:1] == ["start"] and "--" in argv:
        split = argv.index("--")
        argv, job_command = argv[:split], argv[split + 1:]
    args = parser.parse_args(argv)
    args.command = job_command
    sys.stdout.reconfigure(line_buffering=True)
    try:
        if args.command_name == "gpus":
            return 0 if check_gpus(args.node, args.gpus, args.min_free_mib) else 1
        if args.command_name == "start":
            checkout = os.path.realpath(subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
                                                       capture_output=True, text=True).stdout.strip())
            return start(args, checkout)
        if args.command_name == "status":
            return status(args.node, args.run_dir)
        deadline = time.monotonic() + args.timeout
        while (code := status(args.node, args.run_dir, quiet=True,
                              timeout=max(10, deadline - time.monotonic()))) == 3:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(args.interval, remaining))
        if code == 3:
            print(f"still running after {args.timeout} s: {args.run_dir}; wait again or read run.log")
        return code
    except (Failure, subprocess.CalledProcessError) as error:
        print(f"job: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
