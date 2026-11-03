"""Exercise gpu-cluster's checkout.py with a fake ssh that maps the remote path to a second clone."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins/dev-workflow/skills/gpu-cluster/scripts/checkout.py"

# Runs the remote script locally with the checkout path replaced by the "node" clone,
# and maps that path back in the output, as if both machines used the same path.
FAKE_SSH = r"""#!/usr/bin/env python3
import os, subprocess, sys
args = sys.argv[1:]
while args[0] == "-o":
    args = args[2:]
node, script = args
with open(os.environ["FAKE_SSH_LOG"], "a") as log:
    log.write(node + "\n")
if node in os.environ.get("FAKE_SSH_DOWN", "").split(","):
    sys.exit("ssh: connect to host " + node + ": Connection refused")
local, remote = os.environ["FAKE_SSH_MAP"].split("=", 1)
result = subprocess.run(["bash", "-c", script.replace(local, remote)], cwd="/", capture_output=True, text=True)
sys.stdout.write(result.stdout.replace(remote, local))
sys.stderr.write(result.stderr)
sys.exit(result.returncode)
"""


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class CheckoutTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="co-", dir=os.environ.get("DEV_WORKFLOW_TEST_TMPDIR"))).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)
        origin, self.work, self.node = self.tmp / "origin.git", self.tmp / "work", self.tmp / "node"
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(origin))
        git(self.tmp, "clone", "-q", str(origin), str(self.work))
        self.commit(self.work, "a")
        git(self.work, "push", "-q", "origin", "main")
        git(self.tmp, "clone", "-q", str(origin), str(self.node))
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "ssh").write_text(FAKE_SSH)
        (bin_dir / "ssh").chmod(0o755)
        self.ssh_log = self.tmp / "ssh.log"
        self.env = {
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "FAKE_SSH_MAP": f"{self.work}={self.node}",
            "FAKE_SSH_LOG": str(self.ssh_log),
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
        }

    def commit(self, repo, name):
        (repo / name).write_text(name)
        git(repo, "add", name)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", name],
                       cwd=repo, check=True)
        return git(repo, "rev-parse", "HEAD")

    def checkout(self, *args, **env):
        result = subprocess.run(["python3", "-B", str(SCRIPT), *args], cwd=self.work,
                                env={**self.env, **env}, capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout + result.stderr

    def sleeper(self, cwd):
        process = subprocess.Popen(["sleep", "60"], cwd=cwd)
        self.addCleanup(process.wait)
        self.addCleanup(process.kill)
        return process

    def test_sync_fast_forwards_to_the_pushed_head_and_check_then_passes(self):
        code, out = self.checkout("check", "sh-0")
        self.assertEqual(code, 0, out)
        sha = self.commit(self.work, "b")
        git(self.work, "push", "-q", "origin", "main")
        code, out = self.checkout("check", "sh-0")
        self.assertEqual(code, 1, out)
        self.assertIn("is not " + sha, out)
        code, out = self.checkout("sync", "sh-0")
        self.assertEqual(code, 0, out)
        self.assertIn(f"synced: remote HEAD is {sha} and clean", out)
        self.assertIn("no uv.lock", out)
        self.assertEqual(git(self.node, "rev-parse", "HEAD"), sha)
        self.assertEqual(self.checkout("check", "sh-0")[0], 0)
        self.assertEqual(sorted(set(self.ssh_log.read_text().split())), ["sh-0", "sh-1", "sh-2", "sh-gate"])

    def test_sync_refuses_an_unpushed_commit(self):
        self.commit(self.work, "b")
        code, out = self.checkout("sync", "sh-0")
        self.assertEqual(code, 1, out)
        self.assertIn("not on origin", out)

    def test_sync_refuses_a_dirty_remote(self):
        self.commit(self.work, "b")
        git(self.work, "push", "-q", "origin", "main")
        (self.node / "scratch.log").write_text("x")
        code, out = self.checkout("sync", "th-0")
        self.assertEqual(code, 1, out)
        self.assertIn("not clean", out)
        self.assertIn("scratch.log", out)
        self.assertTrue((self.node / "scratch.log").exists())

    def test_sync_refuses_another_branch_and_divergence(self):
        git(self.node, "switch", "-q", "-c", "other")
        code, out = self.checkout("sync", "sh-0")
        self.assertEqual(code, 1, out)
        self.assertIn("remote is on other, local on main", out)
        git(self.node, "switch", "-q", "main")
        diverged = self.commit(self.node, "remote-only")
        self.commit(self.work, "b")
        git(self.work, "push", "-q", "origin", "main")
        code, out = self.checkout("sync", "sh-0")
        self.assertEqual(code, 1, out)
        self.assertIn("investigate the divergence", out)
        self.assertEqual(git(self.node, "rev-parse", "HEAD"), diverged)

    def test_a_job_in_the_remote_checkout_blocks_sync(self):
        self.commit(self.work, "b")
        git(self.work, "push", "-q", "origin", "main")
        job = self.sleeper(self.node / ".")
        code, out = self.checkout("sync", "zg-0")
        self.assertEqual(code, 1, out)
        self.assertIn(f"pid {job.pid}", out)
        self.assertIn("in use", out)

    def test_an_unreachable_cluster_machine_is_not_idle(self):
        code, out = self.checkout("check", "sh-0", FAKE_SSH_DOWN="sh-2")
        self.assertEqual(code, 2, out)
        self.assertIn("Connection refused", out)
        self.assertEqual(self.checkout("check", "xx-0")[0], 2)

    def test_a_failing_lock_check_fails_check(self):
        (self.work / "uv.lock").write_text("version = 1\n")
        self.commit(self.work, "pyproject.toml")
        git(self.work, "add", "uv.lock")
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "lock"],
                       cwd=self.work, check=True)
        git(self.work, "push", "-q", "origin", "main")
        git(self.node, "pull", "-q", "--ff-only")
        uv = self.tmp / "bin" / "uv"
        uv.write_text('#!/bin/sh\necho "${FAKE_UV_OUTPUT:-Would make no changes}"\nexit "${FAKE_UV_EXIT:-0}"\n')
        uv.chmod(0o755)
        code, out = self.checkout("check", "sh-0")
        self.assertEqual(code, 0, out)
        self.assertIn("Would make no changes", out)
        code, out = self.checkout("check", "sh-0", FAKE_UV_EXIT="2", FAKE_UV_OUTPUT="error: lock out of date")
        self.assertEqual(code, 1, out)
        self.assertIn("error: lock out of date", out)
        self.assertIn("FAIL: the environment check exited with 2", out)

    def test_busy_reports_a_multiline_command_line(self):
        process = subprocess.Popen(["python3", "-c", "import time\ntime.sleep(60)"], cwd=self.work)
        self.addCleanup(process.wait)
        self.addCleanup(process.kill)
        code, out = self.checkout("busy")
        self.assertEqual(code, 1, out)
        self.assertIn(f"busy: local pid {process.pid}", out)
        self.assertIn("import time time.sleep(60)", out)
        self.assertNotIn("Traceback", out)

    def test_busy_reports_other_local_processes_but_not_its_own(self):
        code, out = self.checkout("busy")
        self.assertEqual(code, 0, out)
        self.assertIn("idle", out)
        process = self.sleeper(self.work)
        code, out = self.checkout("busy")
        self.assertEqual(code, 1, out)
        self.assertIn(f"busy: local pid {process.pid}", out)


if __name__ == "__main__":
    unittest.main()
