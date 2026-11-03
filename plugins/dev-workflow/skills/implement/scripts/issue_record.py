#!/usr/bin/env python3
"""Read or update a GitLab issue's coder execution record from the selected checkout.

  issue_record.py show <iid>
  issue_record.py set <iid> [--mr URL] [--status TEXT] [--release | --takeover | --for-owner]

`show` prints the issue's execution records, its comment count, remote branches named
issue-<iid>-* (plus any branch a record names) and local worktrees on such branches, and
changes nothing. `set` records the checkout it runs in and that checkout's branch: it
creates the record when none exists or updates the single existing one in place, keeping
the MR and Status it is not given, stamping Updated, and reading the saved note back.
`--release` marks this checkout's record released. Another active worktree's record is
changed only with `--takeover` (an explicit reassignment to this checkout) or
`--for-owner` (update MR/Status and keep its worktree and branch, e.g. after a merge).
It refuses when several records exist or the note changed while it was being edited.
glab infers the project from the checkout.
"""

import argparse
from datetime import datetime, timezone
import json
import os
import re
import subprocess
import sys


MARKER = "<!-- coder-execution-record -->"
FIELDS = ("Worktree", "Branch", "MR", "Status", "Updated")
RELEASED = "Released (last used: "


class Refusal(Exception):
    pass


def run(*command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise Refusal(f"{' '.join(command[:3])} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def glab_api(path, *args):
    return run("glab", "api", path, *args)


def notes_path(iid):
    return f"projects/:id/issues/{iid}/notes"


def list_notes(iid):
    output = glab_api(f"{notes_path(iid)}?per_page=100&sort=asc", "--paginate", "--output", "ndjson")
    return [json.loads(line) for line in output.splitlines() if line.strip()]


def get_note(iid, note_id):
    return json.loads(glab_api(f"{notes_path(iid)}/{note_id}"))


def parse_fields(body):
    fields = {}
    for line in body.splitlines():
        match = re.fullmatch(r"\|\s*(\w+)\s*\|\s*(.*?)\s*\|", line.strip())
        if match and match[1] in FIELDS:
            fields[match[1]] = match[2].replace("\\|", "|")
    return fields


def render(fields):
    rows = [f"| {name} | {' '.join(fields.get(name, '').split()).replace('|', chr(92) + '|')} |" for name in FIELDS]
    return "\n".join([MARKER, "### Execution record", "", "| Field | Value |", "|---|---|", *rows]) + "\n"


def records(notes):
    return [note for note in notes if not note.get("system") and MARKER in note.get("body", "")]


def summary(note):
    return {
        "note_id": note["id"],
        "author": (note.get("author") or {}).get("username"),
        "updated_at": note.get("updated_at"),
        "fields": parse_fields(note["body"]),
    }


def show(iid):
    notes = list_notes(iid)
    found = records(notes)
    heads = run("git", "ls-remote", "--heads", "origin", f"refs/heads/issue-{iid}-*")
    branches = sorted(line.split("refs/heads/", 1)[1] for line in heads.splitlines() if line.strip())
    named = {parse_fields(record["body"]).get("Branch", "") for record in found} - {""}
    for branch in sorted(named - set(branches)):
        if run("git", "ls-remote", "--heads", "origin", f"refs/heads/{branch}").strip():
            branches.append(branch)
    # Local worktrees count even when their branch was never pushed or is already deleted.
    worktrees, path = [], None
    for line in run("git", "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path = line.split(" ", 1)[1]
        elif line.startswith("branch refs/heads/"):
            branch = line.split("refs/heads/", 1)[1]
            if branch.startswith(f"issue-{iid}-") or branch in named:
                worktrees.append({"path": path, "branch": branch})
    return {
        "issue": iid,
        "comments": sum(1 for note in notes if not note.get("system")),
        "records": [summary(record) for record in found],
        "remote_branches": branches,
        "local_worktrees": worktrees,
    }


def set_record(iid, args):
    found = records(list_notes(iid))
    if len(found) > 1:
        raise Refusal(f"{len(found)} execution records on #{iid} (notes {[n['id'] for n in found]}); resolve ownership first")
    current = parse_fields(found[0]["body"]) if found else {}
    owner = current.get("Worktree", "")
    active = bool(owner) and not owner.startswith(RELEASED)
    checkout = os.path.realpath(run("git", "rev-parse", "--show-toplevel").strip())
    mine = active and os.path.realpath(owner) == checkout  # records may name a linked path
    if args.for_owner:
        if not found:
            raise Refusal(f"#{iid} has no record to update")
        worktree, branch = owner, current.get("Branch", "")
    elif args.release:
        if not active:
            raise Refusal(f"#{iid} has no active worktree to release")
        if not mine:
            raise Refusal(f"#{iid} is recorded for {owner}; release it from that checkout")
        worktree, branch = f"{RELEASED}{checkout})", current.get("Branch", "")
    else:
        if active and not mine and not args.takeover:
            raise Refusal(f"#{iid} is recorded for {owner}; pass --takeover only for an explicit reassignment, "
                          "or --for-owner to update that record without taking it")
        branch = subprocess.run(["git", "symbolic-ref", "--short", "-q", "HEAD"], capture_output=True, text=True).stdout.strip()
        if not branch:
            raise Refusal("detached HEAD; check out the issue's branch first")
        worktree = checkout
    fields = {
        "Worktree": worktree,
        "Branch": branch,
        "MR": args.mr or current.get("MR", "Not opened"),
        "Status": args.status or current.get("Status", ""),
        "Updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if not fields["Status"]:
        raise Refusal("a new record needs --status")
    body = render(fields)
    if found:
        note_id = found[0]["id"]
        if get_note(iid, note_id)["body"] != found[0]["body"]:
            raise Refusal(f"note {note_id} changed while editing; run show and retry")
        saved = json.loads(glab_api(f"{notes_path(iid)}/{note_id}", "--method", "PUT", "--raw-field", f"body={body}"))
    else:
        saved = json.loads(glab_api(notes_path(iid), "--method", "POST", "--raw-field", f"body={body}"))
    if get_note(iid, saved["id"])["body"].strip() != body.strip():
        raise Refusal(f"note {saved['id']} does not hold the written record; run show")
    return {"issue": iid, "action": "updated" if found else "created", **summary({**saved, "body": body})}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("show").add_argument("iid", type=int)
    setter = commands.add_parser("set")
    setter.add_argument("iid", type=int)
    setter.add_argument("--mr")
    setter.add_argument("--status")
    mode = setter.add_mutually_exclusive_group()
    mode.add_argument("--release", action="store_true", help="mark this checkout's record released")
    mode.add_argument("--takeover", action="store_true", help="reassign another active worktree's record to this checkout")
    mode.add_argument("--for-owner", action="store_true", help="update MR/Status of another worktree's record without taking it")
    args = parser.parse_args()
    try:
        result = show(args.iid) if args.command == "show" else set_record(args.iid, args)
    except Refusal as error:
        print(f"issue_record: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
