#!/usr/bin/env python3
"""Check, or fast-forward, a checkout's remote counterpart from the local checkout.

Run in the selected local checkout; the remote counterpart has the same physical path.

  checkout.py busy [NODE]       processes working in the checkout, locally and, with NODE,
                                on every machine sharing NODE's /volume
  checkout.py check NODE [--sha SHA]
                                read-only: same origin and branch, HEAD at SHA (default:
                                local HEAD), clean, idle on the cluster; print the uv lock check
  checkout.py sync NODE [--sha SHA]
                                the same preconditions, then fetch and fast-forward to SHA,
                                verify, and print the uv lock check

Exit codes: 0 ok or idle, 1 a check failed or the checkout is busy, 2 a command failed.
Nothing here resets, cleans, stashes or switches branches.
"""

import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys


# Machines sharing one /volume, by cluster (see machines.md).
CLUSTERS = {
    "sh": ["sh-0", "sh-1", "sh-2", "sh-gate"],
    "zg": ["zg-0", "zg-1", "zg-gate"],
    "th": ["th-0", "th-1"],
}

SCAN = r"""W=%s
for p in /proc/[0-9]*; do
  c=$(readlink "$p/cwd" 2>/dev/null) || continue
  case $c in "$W"|"$W"/*)
    printf '%%s\t%%s\t%%s\n' "${p#/proc/}" "$c" "$(tr '\0\n\t' '   ' < "$p/cmdline" 2>/dev/null | cut -c1-160)";;
  esac
done"""


class Failure(Exception):
    """A command could not run; the state is unknown."""


def run(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise Failure(f"{shlex.join(command[:4])}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def ssh(node, script):
    return run(["ssh", "-o", "BatchMode=yes", node, script])


def git(checkout, *args):
    return run(["git", *args], cwd=checkout).strip()


def normalize(url):
    url = re.sub(r"^http://", "https://", url.strip())
    url = re.sub(r"//[^/@]*@", "//", url)
    return re.sub(r"(\.git)?/*$", "", url).lower()


def cluster_of(node):
    name = node.split("-", 1)[0]
    if name not in CLUSTERS:
        raise Failure(f"unknown cluster for {node}; expected one of {', '.join(sorted(CLUSTERS))}")
    return CLUSTERS[name]


def parse_scan(output):
    records = (line.split("\t", 2) for line in output.splitlines())
    return [tuple(fields) for fields in records if len(fields) == 3]


def own_processes():
    pids, pid = set(), os.getpid()
    while pid > 1:
        pids.add(str(pid))
        try:
            stat = Path(f"/proc/{pid}/stat").read_text()
        except OSError:
            break
        pid = int(stat.rsplit(")", 1)[1].split()[1])
    return pids


def busy(checkout, node=None):
    """Return {machine: [(pid, cwd, cmdline), ...]} for processes other than this one's ancestors."""
    script = SCAN % shlex.quote(checkout)
    mine = own_processes()
    # Scan from / so the scanning shell itself is not in the checkout.
    found = {"local": [p for p in parse_scan(run(["sh", "-c", script], cwd="/")) if p[0] not in mine]}
    for machine in cluster_of(node) if node else []:
        found[machine] = parse_scan(ssh(machine, script))
    return found


def report_busy(found):
    users = [(machine, process) for machine, processes in found.items() for process in processes]
    for machine, (pid, cwd, cmdline) in users:
        print(f"busy: {machine} pid {pid} in {cwd}: {cmdline}")
    return bool(users)


def remote_state(node, checkout):
    script = (
        f"cd -- {shlex.quote(checkout)} && pwd -P && git remote get-url origin && "
        "(git symbolic-ref --short -q HEAD || echo '(detached)') && git rev-parse HEAD && "
        "git status --porcelain --untracked-files=all"
    )
    lines = ssh(node, script).split("\n")
    return {"path": lines[0], "origin": lines[1], "branch": lines[2], "head": lines[3],
            "dirty": [line for line in lines[4:] if line.strip()]}


def environment(node, checkout):
    """Print the uv lock dry run; return False when it fails."""
    script = (
        f"cd -- {shlex.quote(checkout)} && if test -f uv.lock; then "
        "out=$(uv sync --locked --dry-run 2>&1); rc=$?; printf '%s\\n' \"$out\" | tail -n 15; exit $rc; "
        "else echo 'no uv.lock'; fi"
    )
    result = subprocess.run(["ssh", "-o", "BatchMode=yes", node, script], capture_output=True, text=True)
    if result.returncode == 255:
        raise Failure(f"ssh {node}: {result.stderr.strip()}")
    print("environment (uv sync --locked --dry-run; dependency changes mean the environment does not match the lock):")
    print("  " + (result.stdout + result.stderr).strip().replace("\n", "\n  "))
    if result.returncode:
        print(f"FAIL: the environment check exited with {result.returncode}")
        return False
    return True


def preconditions(node, checkout, sha, local_branch, allow_behind):
    """Print each check; return the remote state when all pass, else None."""
    state = remote_state(node, checkout)
    problems = []
    if state["path"] != checkout:
        problems.append(f"remote physical path is {state['path']}, not {checkout}")
    if normalize(state["origin"]) != normalize(git(checkout, "remote", "get-url", "origin")):
        problems.append(f"remote origin {state['origin']} differs from the local origin")
    if state["branch"] != local_branch:
        problems.append(f"remote is on {state['branch']}, local on {local_branch}; switch under the worktree reuse rules")
    if state["dirty"]:
        problems.append("remote working tree is not clean:\n    " + "\n    ".join(state["dirty"][:20]))
    if state["head"] != sha and not allow_behind:
        problems.append(f"remote HEAD {state['head']} is not {sha}")
    print(f"remote: {node}:{checkout} on {state['branch']} at {state['head']}", flush=True)
    if report_busy({k: v for k, v in busy(checkout, node).items() if k != "local"}):
        problems.append("remote checkout is in use; do not change it while a job uses it")
    for problem in problems:
        print(f"FAIL: {problem}")
    return None if problems else state


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("busy").add_argument("node", nargs="?")
    for name in ("check", "sync"):
        command = commands.add_parser(name)
        command.add_argument("node")
        command.add_argument("--sha", help="commit to require (default: local HEAD)")
    args = parser.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    try:
        checkout = os.path.realpath(git(os.getcwd(), "rev-parse", "--show-toplevel"))
        if args.command == "busy":
            in_use = report_busy(busy(checkout, args.node))
            print("busy" if in_use else f"idle: no other process works in {checkout}")
            return 1 if in_use else 0
        sha = git(checkout, "rev-parse", "--verify", f"{args.sha or 'HEAD'}^{{commit}}")
        branch = run(["sh", "-c", "git symbolic-ref --short -q HEAD || echo '(detached)'"], cwd=checkout).strip()
        print(f"local: {checkout} on {branch} at {sha}")
        state = preconditions(args.node, checkout, sha, branch, allow_behind=args.command == "sync")
        if state is None:
            return 1
        if args.command == "sync" and state["head"] != sha:
            q = shlex.quote
            fetch = "git fetch --quiet origin" + ("" if branch == "(detached)" else f" {q(branch)}")
            move = f"git checkout --quiet --detach {sha}" if branch == "(detached)" else f"git merge --quiet --ff-only {sha}"
            script = (
                f"cd -- {q(checkout)} && {fetch} && "
                f"{{ git cat-file -e {sha}^{{commit}} 2>/dev/null || {{ echo 'not on origin; push it first' >&2; exit 1; }}; }} && "
                f"{{ git merge-base --is-ancestor HEAD {sha} || {{ echo 'remote HEAD is not an ancestor; investigate the divergence' >&2; exit 1; }}; }} && "
                f"{move}"
            )
            try:
                ssh(args.node, script)
            except Failure as error:
                print(f"FAIL: {error}")
                return 1
            state = remote_state(args.node, checkout)
            if state["head"] != sha or state["dirty"]:
                print(f"FAIL: after sync the remote is at {state['head']} with {len(state['dirty'])} changed paths")
                return 1
            print(f"synced: remote HEAD is {sha} and clean")
        else:
            print(f"ok: remote HEAD is {sha}, clean and idle")
        return 0 if environment(args.node, checkout) else 1
    except Failure as error:
        print(f"checkout: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
