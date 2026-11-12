#!/usr/bin/env python3
"""Record whole-machine allocations for workers on the control machine."""

import argparse
from contextlib import closing
import os
from pathlib import Path
import re
import sqlite3
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        type=Path,
        default=Path.home() / ".local/state/gpu-cluster/allocations.sqlite3",
        help="Allocation file (override only for isolated tests)",
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
        if not re.fullmatch(r"(?:sh|zg|th)-(?:0|[1-9][0-9]*)", args.node):
            parser.error("Use a canonical GPU node alias: sh-<n>, zg-<n> or th-<n>.")
        if not args.worker or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/-]*", args.worker):
            parser.error("Set HC_TERMINAL_ID or pass --worker with a session ID without spaces.")

    try:
        args.database.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(args.database)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS allocations (node TEXT PRIMARY KEY, worker TEXT NOT NULL)")
            if args.command == "list":
                rows = db.execute("SELECT node, worker FROM allocations ORDER BY node").fetchall()
                output = "NODE\tWORKER\n" + "\n".join(f"{node}\t{worker}" for node, worker in rows)
            elif args.command == "claim":
                db.execute(
                    "INSERT INTO allocations VALUES (?, ?) ON CONFLICT(node) DO NOTHING",
                    (args.node, args.worker),
                )
                owner = db.execute("SELECT worker FROM allocations WHERE node = ?", (args.node,)).fetchone()[0]
                if owner != args.worker:
                    raise ValueError(f"{args.node} is registered to {owner}; its allocation was not changed.")
                output = f"{args.node} is registered to {args.worker}."
            else:
                db.execute("DELETE FROM allocations WHERE node = ? AND worker = ?", (args.node, args.worker))
                owner = db.execute("SELECT worker FROM allocations WHERE node = ?", (args.node,)).fetchone()
                if owner is not None:
                    raise ValueError(f"{args.node} is registered to {owner[0]}, not {args.worker}; it was not released.")
                output = f"{args.node} has no registered owner."
        print(output)
        return 0
    except (OSError, sqlite3.Error, ValueError) as error:
        print(f"Allocation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
