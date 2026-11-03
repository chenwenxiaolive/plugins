"""Exercise implement's issue_record.py against a fake `glab api` backed by a JSON file."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins/dev-workflow/skills/implement/scripts/issue_record.py"
MARKER = "<!-- coder-execution-record -->"

FAKE_GLAB = r"""#!/usr/bin/env python3
import json, os, re, sys
path_state = os.environ["FAKE_GLAB_STATE"]
state = json.load(open(path_state))
args = sys.argv[1:]
assert args[0] == "api", args
path, flags = args[1], args[2:]
method = flags[flags.index("--method") + 1] if "--method" in flags else "GET"
body = next((flags[i + 1][5:] for i, f in enumerate(flags) if f == "--raw-field" and flags[i + 1].startswith("body=")), None)
if method == os.environ.get("FAKE_GLAB_FAIL"):
    sys.exit("glab: 504 Gateway Timeout")
match = re.fullmatch(r"projects/:id/issues/(\d+)/notes(?:/(\d+))?(\?.*)?", path)
notes = state.setdefault(match[1], [])
note_id = int(match[2]) if match[2] else None
find = lambda: next(n for n in notes if n["id"] == note_id)
if method == "GET" and note_id is None:
    assert "--paginate" in flags and flags[flags.index("--output") + 1] == "ndjson", flags
    out = "".join(json.dumps(n) + "\n" for n in notes)
elif method == "GET":
    note = find()
    if os.environ.get("FAKE_GLAB_EDIT_ON_GET"):
        note["body"] += "\nedited by someone else"
    out = json.dumps(note)
elif method == "POST":
    note = {"id": max([n["id"] for n in notes] + [100]) + 1, "body": body, "system": False,
            "author": {"username": "coder"}, "updated_at": "2026-11-03T00:00:00Z"}
    notes.append(note)
    out = json.dumps(note)
elif method == "PUT":
    note = find()
    note["body"] = body
    out = json.dumps(note)
json.dump(state, open(path_state, "w"))
print(out)
"""


def record(worktree, branch="issue-42-fix-cache", status="active"):
    return "\n".join([MARKER, "### Execution record", "", "| Field | Value |", "|---|---|",
                      f"| Worktree | {worktree} |", f"| Branch | {branch} |", "| MR | Not opened |",
                      f"| Status | {status} |", "| Updated | 2026-11-01T00:00:00Z |"]) + "\n"


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


class IssueRecordTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ir-", dir=os.environ.get("DEV_WORKFLOW_TEST_TMPDIR"))).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)
        origin, self.work = self.tmp / "origin.git", self.tmp / "work"
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(origin))
        git(self.tmp, "clone", "-q", str(origin), str(self.work))
        ident = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]
        git(self.work, *ident, "commit", "-q", "--allow-empty", "-m", "a")
        for branch in ["main", "issue-42-fix-cache", "issue-142-other", "custom-name"]:
            git(self.work, "push", "-q", "origin", f"HEAD:refs/heads/{branch}")
        git(self.work, "worktree", "add", "-q", str(self.tmp / "dev-1"), "-b", "issue-42-fix-cache", "origin/issue-42-fix-cache")
        git(self.work, "worktree", "add", "-q", str(self.tmp / "dev-2"), "-b", "issue-42-not-pushed")
        git(self.work, "worktree", "add", "-q", str(self.tmp / "dev-3"), "-b", "issue-142-other-local")
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "glab").write_text(FAKE_GLAB)
        (bin_dir / "glab").chmod(0o755)
        self.state = self.tmp / "notes.json"
        self.save({})
        self.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_GLAB_STATE": str(self.state)}

    def save(self, notes):
        self.state.write_text(json.dumps(notes))

    def notes(self, iid=42):
        return json.loads(self.state.read_text()).get(str(iid), [])

    def seed(self, *bodies, system=()):
        notes = [{"id": 10 + i, "body": b, "system": False, "author": {"username": "x"}, "updated_at": "t"}
                 for i, b in enumerate(bodies)]
        notes += [{"id": 90 + i, "body": b, "system": True} for i, b in enumerate(system)]
        self.save({"42": notes})

    def run_script(self, *args, **env):
        result = subprocess.run(["python3", "-B", str(SCRIPT), *args], cwd=self.work,
                                env={**self.env, **env}, capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout, result.stderr

    def current_fields(self):
        code, out, err = self.run_script("show", "42")
        self.assertEqual(code, 0, err)
        return json.loads(out)["records"][0]["fields"]

    def test_show_lists_records_branches_and_worktrees_only_for_this_issue(self):
        self.seed("plain comment", record("/w/dev-1", branch="custom-name"), system=[MARKER])
        code, out, err = self.run_script("show", "42")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["comments"], 2)
        self.assertEqual([r["note_id"] for r in result["records"]], [11])
        self.assertEqual(result["records"][0]["fields"]["Worktree"], "/w/dev-1")
        self.assertEqual(result["remote_branches"], ["issue-42-fix-cache", "custom-name"])
        self.assertEqual(result["local_worktrees"], [
            {"path": str(self.tmp / "dev-1"), "branch": "issue-42-fix-cache"},
            {"path": str(self.tmp / "dev-2"), "branch": "issue-42-not-pushed"},
        ])

    def test_set_creates_a_record_and_requires_its_fields(self):
        code, _, err = self.run_script("set", "42", "--worktree", "/w/dev-1")
        self.assertEqual(code, 1)
        self.assertIn("--branch, --status", err)
        self.assertEqual(self.notes(), [])
        code, out, err = self.run_script("set", "42", "--worktree", "/w/dev-1", "--branch", "issue-42-fix-cache",
                                         "--status", "active | waiting on sh-0")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["action"], "created")
        [note] = self.notes()
        self.assertTrue(note["body"].startswith(MARKER + "\n### Execution record\n"))
        self.assertIn("| Status | active \\| waiting on sh-0 |", note["body"])
        fields = self.current_fields()
        self.assertEqual(fields["Status"], "active | waiting on sh-0")
        self.assertEqual(fields["MR"], "Not opened")
        self.assertRegex(fields["Updated"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_set_updates_in_place_and_keeps_other_fields(self):
        self.seed("plain comment", record("/w/dev-1"))
        code, out, err = self.run_script("set", "42", "--mr", "!12", "--status", "ready-for-merge")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["action"], "updated")
        self.assertEqual(len(self.notes()), 2)
        fields = self.current_fields()
        self.assertEqual((fields["Worktree"], fields["Branch"], fields["MR"], fields["Status"]),
                         ("/w/dev-1", "issue-42-fix-cache", "!12", "ready-for-merge"))

    def test_set_protects_another_active_owner(self):
        self.seed(record("/w/dev-1"))
        code, _, err = self.run_script("set", "42", "--worktree", "/w/dev-2", "--status", "active")
        self.assertEqual(code, 1)
        self.assertIn("recorded for /w/dev-1", err)
        self.assertEqual(self.current_fields()["Worktree"], "/w/dev-1")
        code, _, err = self.run_script("set", "42", "--worktree", "/w/dev-2", "--status", "active", "--takeover")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.current_fields()["Worktree"], "/w/dev-2")

    def test_release_then_reclaim(self):
        self.seed(record("/w/dev-1"))
        code, _, err = self.run_script("set", "42", "--release", "--status", "paused: tests remain")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.current_fields()["Worktree"], "Released (last used: /w/dev-1)")
        self.assertEqual(self.run_script("set", "42", "--release")[0], 1)
        code, _, err = self.run_script("set", "42", "--worktree", "/w/dev-3", "--status", "active")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.current_fields()["Worktree"], "/w/dev-3")

    def test_set_refuses_duplicates_concurrent_edits_and_failed_writes(self):
        self.seed(record("/w/dev-1"), record("/w/dev-2"))
        code, _, err = self.run_script("set", "42", "--status", "active")
        self.assertEqual(code, 1)
        self.assertIn("2 execution records", err)
        self.seed(record("/w/dev-1"))
        code, _, err = self.run_script("set", "42", "--status", "active", FAKE_GLAB_EDIT_ON_GET="1")
        self.assertEqual(code, 1)
        self.assertIn("changed while editing", err)
        self.seed(record("/w/dev-1"))
        code, _, err = self.run_script("set", "42", "--status", "blocked", FAKE_GLAB_FAIL="PUT")
        self.assertEqual(code, 1)
        self.assertIn("504", err)
        self.assertEqual(self.current_fields()["Status"], "active")


if __name__ == "__main__":
    unittest.main()
