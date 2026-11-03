#!/usr/bin/env python3
"""Read or update a GitLab issue's coder execution record from the selected checkout.

  issue_record.py show <iid>
  issue_record.py set <iid> [--worktree PATH] [--branch NAME] [--mr URL] [--status TEXT]
                            [--release] [--takeover]

`show` prints the issue's execution records, its comment count, remote branches named
issue-<iid>-* and local worktrees on them, and changes nothing. `set` creates the record
when none exists or updates the single existing one in place, keeping fields it is not
given, stamping Updated, and reading the saved note back. It refuses when several records
exist, when another active worktree owns the record (unless --takeover), or when the note
changed while it was being edited. glab infers the project from the checkout.
"""

import argparse
from datetime import datetime, timezone
import json
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
    if args.release:
        if not owner or owner.startswith(RELEASED):
            raise Refusal(f"#{iid} has no active worktree to release")
        worktree = f"{RELEASED}{owner})"
    else:
        worktree = args.worktree or owner
        if args.worktree and owner and not owner.startswith(RELEASED) and owner != args.worktree and not args.takeover:
            raise Refusal(f"#{iid} is recorded for {owner}; pass --takeover only for an explicit reassignment")
    fields = {
        "Worktree": worktree,
        "Branch": args.branch or current.get("Branch", ""),
        "MR": args.mr or current.get("MR", "Not opened"),
        "Status": args.status or current.get("Status", ""),
        "Updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    missing = [name for name in ("Worktree", "Branch", "Status") if not fields[name]]
    if missing:
        raise Refusal(f"a new record needs {', '.join('--' + name.lower() for name in missing)}")
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
    setter.add_argument("--worktree")
    setter.add_argument("--branch")
    setter.add_argument("--mr")
    setter.add_argument("--status")
    setter.add_argument("--release", action="store_true", help="mark the recorded worktree as released")
    setter.add_argument("--takeover", action="store_true", help="replace another active worktree's record")
    args = parser.parse_args()
    if args.command == "set" and args.release and args.worktree:
        parser.error("--release keeps the recorded worktree; do not pass --worktree")
    try:
        result = show(args.iid) if args.command == "show" else set_record(args.iid, args)
    except Refusal as error:
        print(f"issue_record: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
