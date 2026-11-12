"""Exercise the allocation CLI against isolated files, without GPU or SSH access."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "plugins/dev-workflow/skills/gpu-cluster/scripts/allocations.py"


class AllocationsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=os.environ["GPU_ALLOCATION_TEST_TMPDIR"])
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.command = [sys.executable, str(SCRIPT), "--database", str(self.root / "allocations.sqlite3")]
        self.env = dict(os.environ, HC_TERMINAL_ID="worker-a")

    def run_cli(self, *args):
        return subprocess.run(self.command + list(args), cwd=self.root, env=self.env, text=True, capture_output=True)

    def test_owner_persists_across_processes_and_repeated_claims(self):
        self.assertEqual(self.run_cli("list").stdout.strip(), "NODE\tWORKER")
        for _ in range(2):
            self.assertEqual(self.run_cli("claim", "sh-1").returncode, 0)
        conflict = self.run_cli("claim", "sh-1", "--worker", "worker-b")
        self.assertEqual(conflict.returncode, 1)
        self.assertIn("registered to worker-a", conflict.stderr)
        self.assertEqual(self.run_cli("list").stdout.splitlines(), ["NODE\tWORKER", "sh-1\tworker-a"])

    def test_release_matches_owner_and_does_not_remove_a_replacement(self):
        self.assertEqual(self.run_cli("claim", "sh-1").returncode, 0)
        self.assertEqual(self.run_cli("release", "sh-1", "--worker", "worker-b").returncode, 1)
        self.assertEqual(self.run_cli("release", "sh-1").returncode, 0)
        self.assertEqual(self.run_cli("release", "sh-1").returncode, 0)
        self.assertEqual(self.run_cli("claim", "sh-1", "--worker", "worker-b").returncode, 0)
        self.assertEqual(self.run_cli("release", "sh-1").returncode, 1)
        self.assertIn("sh-1\tworker-b", self.run_cli("list").stdout)

    def test_simultaneous_claims_have_one_winner(self):
        processes = [
            subprocess.Popen(
                self.command + ["claim", "th-1", "--worker", f"worker-{i}"],
                cwd=self.root, env=self.env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for i in range(8)
        ]
        outputs = [process.communicate(timeout=20) for process in processes]
        winners = [i for i, process in enumerate(processes) if process.returncode == 0]
        self.assertEqual(len(winners), 1, outputs)
        self.assertEqual(self.run_cli("list").stdout.splitlines(), ["NODE\tWORKER", f"th-1\tworker-{winners[0]}"])
        for i, process in enumerate(processes):
            if i != winners[0]:
                self.assertEqual(process.returncode, 1, outputs[i])
                self.assertIn(f"registered to worker-{winners[0]}", outputs[i][1])

    def test_simultaneous_different_machines_keep_all_owners(self):
        processes = [
            subprocess.Popen(
                self.command + ["claim", f"zg-{i}", "--worker", f"worker-{i}"],
                cwd=self.root, env=self.env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for i in range(4)
        ]
        for process in processes:
            output = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, output)
        self.assertEqual(
            self.run_cli("list").stdout.splitlines(),
            ["NODE\tWORKER"] + [f"zg-{i}\tworker-{i}" for i in range(4)],
        )

    def test_requires_a_worker_and_canonical_node_alias(self):
        self.env.pop("HC_TERMINAL_ID")
        self.assertEqual(self.run_cli("claim", "sh-1").returncode, 2)
        invalid = self.run_cli("claim", "sh-01", "--worker", "worker-a")
        self.assertEqual(invalid.returncode, 2)
        self.assertFalse((self.root / "allocations.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
