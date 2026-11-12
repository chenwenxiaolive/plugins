#!/usr/bin/env python3
"""Record whole-machine allocations for workers on the control machine."""

import argparse
import fcntl
import os
from pathlib import Path
import re
import sys


NODE_ALIAS = re.compile(r"(?:sh|zg|th)-(?:0|[1-9][0-9]*)")
WORKER_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]*")


def read_owner(record):
    owner = record.read_text().strip()
    if not WORKER_ID.fullmatch(owner):
        raise ValueError(f"Invalid owner record: {record}; its allocation was not changed.")
    return owner


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path.home() / ".local/state/gpu-cluster/allocations",
        help="Allocation directory (override only for isolated tests)",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Show registered owners, not live GPU availability")
    for command in ("claim", "release"):
        operation = commands.add_parser(command)
        operation.add_argument("node", help="Canonical node alias, e.g. sh-1")
        operation.add_argument(
            "--worker", default=os.environ.get("HC_TERMINAL_ID"),
            help="Worker session ID (defaults to HC_TERMINAL_ID)",
        )
    args = parser.parse_args()
    if args.command != "list":
        if not NODE_ALIAS.fullmatch(args.node):
            parser.error("Use a canonical GPU node alias: sh-<n>, zg-<n> or th-<n>.")
        if not args.worker or not WORKER_ID.fullmatch(args.worker):
            parser.error("Set HC_TERMINAL_ID or pass --worker with a session ID without spaces.")

    try:
        args.directory.mkdir(parents=True, exist_ok=True)
        with (args.directory / ".lock").open("a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            if args.command == "list":
                rows = [
                    (record.name, read_owner(record))
                    for record in sorted(args.directory.iterdir())
                    if NODE_ALIAS.fullmatch(record.name)
                ]
                output = "NODE\tWORKER\n" + "\n".join(f"{node}\t{worker}" for node, worker in rows)
            else:
                record = args.directory / args.node
                owner = read_owner(record) if record.exists() else None
                if owner is not None and owner != args.worker:
                    raise ValueError(f"{args.node} is registered to {owner}; its allocation was not changed.")
                if args.command == "claim":
                    if owner is None:
                        temporary = args.directory / ".owner.tmp"
                        temporary.write_text(args.worker + "\n")
                        temporary.replace(record)
                    output = f"{args.node} is registered to {args.worker}."
                else:
                    if owner is not None:
                        record.unlink()
                    output = f"{args.node} has no registered owner."
        print(output)
        return 0
    except (OSError, ValueError) as error:
        print(f"Allocation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
