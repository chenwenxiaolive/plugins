"""Run sync_installation.sh in a temporary checkout with a fake npx and a stub installation check."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CHECK_PASSES = "import sys\nsys.exit(0)\n"
CHECK_FAILS = "import sys\nsys.exit(1)\n"


class SyncInstallationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sync-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.origin = self.tmp / "origin.git"
        self.upstream = self.tmp / "upstream"
        self.checkout = self.tmp / "checkout"
        self.npx_log = self.tmp / "npx.log"

        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "npx").write_text(f'#!/bin/sh\necho "$@" >> "{self.npx_log}"\n')
        (bin_dir / "npx").chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
        }

        self.git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.origin))
        self.git(self.tmp, "clone", "-q", str(self.origin), str(self.upstream))
        self.git(self.upstream, "checkout", "-q", "-b", "main")
        (self.upstream / "scripts").mkdir()
        shutil.copy(ROOT / "scripts/sync_installation.sh", self.upstream / "scripts/sync_installation.sh")
        (self.upstream / "scripts/check_installation.py").write_text(CHECK_PASSES)
        (self.upstream / "plugins").mkdir()
        self.push("plugins/skill.md", "one\n")
        self.git(self.tmp, "clone", "-q", str(self.origin), str(self.checkout))

    def git(self, cwd, *args):
        return subprocess.run(
            ["git", *args], cwd=cwd, env=self.env, check=True, capture_output=True, text=True
        ).stdout.strip()

    def push(self, name, content):
        (self.upstream / name).write_text(content)
        self.git(self.upstream, "add", "-A")
        self.git(self.upstream, "commit", "-q", "-m", name)
        self.git(self.upstream, "push", "-q", "origin", "main")

    def sync(self):
        return subprocess.run(
            [str(self.checkout / "scripts/sync_installation.sh")],
            cwd=self.tmp, env=self.env, capture_output=True, text=True,
        )

    def test_a_checkout_behind_origin_is_fast_forwarded_and_installed(self):
        self.push("plugins/skill.md", "two\n")
        result = self.sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(self.checkout, "rev-parse", "HEAD"), self.git(self.upstream, "rev-parse", "HEAD"))
        self.assertIn(f"skills add {self.checkout} ", self.npx_log.read_text())

    def test_a_checkout_at_origin_is_left_alone(self):
        result = self.sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.npx_log.exists())

    def assert_stops_before_installing(self):
        before = self.git(self.checkout, "rev-parse", "HEAD")
        self.assertNotEqual(self.sync().returncode, 0)
        self.assertEqual(self.git(self.checkout, "rev-parse", "HEAD"), before)
        self.assertFalse(self.npx_log.exists())

    def test_it_stops_on_another_branch(self):
        self.git(self.checkout, "checkout", "-q", "-b", "topic")
        self.push("plugins/skill.md", "two\n")
        self.assert_stops_before_installing()

    def test_it_stops_on_an_uncommitted_skill_file(self):
        (self.checkout / "plugins/draft.md").write_text("draft\n")
        self.push("plugins/skill.md", "two\n")
        self.assert_stops_before_installing()

    def test_it_stops_on_an_unpushed_commit(self):
        (self.checkout / "plugins/skill.md").write_text("local\n")
        self.git(self.checkout, "commit", "-q", "-am", "local")
        self.assert_stops_before_installing()

    def test_it_stops_when_the_installation_differs(self):
        (self.upstream / "scripts/check_installation.py").write_text(CHECK_FAILS)
        self.push("plugins/skill.md", "two\n")
        self.git(self.checkout, "pull", "-q")
        self.push("plugins/skill.md", "three\n")
        self.assert_stops_before_installing()


if __name__ == "__main__":
    unittest.main()
