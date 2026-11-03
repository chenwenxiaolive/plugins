"""Exercise gpu-cluster's job.py with a fake ssh (run locally) and a fake nvidia-smi."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins/dev-workflow/skills/gpu-cluster/scripts/job.py"

# Runs the remote script locally, with /volume/tmp mapped to a test directory and back.
FAKE_SSH = r"""#!/usr/bin/env python3
import os, subprocess, sys
args = sys.argv[1:]
while args[0] == "-o":
    args = args[2:]
node, script = args
if os.environ.get("FAKE_SSH_HANG") and "exit.status" in script:
    import time
    time.sleep(60)
local, remote = os.environ["FAKE_SSH_MAP"].split("=", 1)
keep = os.environ["FAKE_SSH_KEEP"]  # the test tree itself may live under /volume/tmp
remap = lambda text: text.replace(keep, "\0").replace(local, remote).replace("\0", keep)
result = subprocess.run(["bash", "-c", remap(script)], cwd="/", input=remap(sys.stdin.read()),
                        capture_output=True, text=True)
sys.stdout.write(result.stdout.replace(remote, local))
sys.stderr.write(result.stderr)
sys.exit(result.returncode)
"""

FAKE_NVIDIA_SMI = """#!/bin/sh
case "$*" in
  *--query-gpu=*) printf '%s\\n' "$FAKE_GPUS" ;;
  *--query-compute-apps=*) test -z "$FAKE_APPS_FAIL" || exit 9; printf '%s\\n' "$FAKE_APPS" ;;
esac
"""


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class JobTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="job-", dir=os.environ.get("DEV_WORKFLOW_TEST_TMPDIR"))).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.work, self.volume_tmp = self.tmp / "work", self.tmp / "volume-tmp"
        self.volume_tmp.mkdir()
        git(self.tmp, "init", "-q", "-b", "main", str(self.work))
        git(self.work, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "a")
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        for name, body in (("ssh", FAKE_SSH), ("nvidia-smi", FAKE_NVIDIA_SMI)):
            (bin_dir / name).write_text(body)
            (bin_dir / name).chmod(0o755)
        self.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}",
                    "FAKE_SSH_MAP": f"/volume/tmp={self.volume_tmp}", "FAKE_SSH_KEEP": str(self.tmp),
                    "FAKE_GPUS": "0, GPU-a, 700, 1000\n1, GPU-b, 100, 1000", "FAKE_APPS": ""}

    def job(self, *args, **env):
        result = subprocess.run(["python3", "-B", str(SCRIPT), *args], cwd=self.work,
                                env={**self.env, **env}, capture_output=True, text=True, timeout=120)
        return result.returncode, result.stdout + result.stderr

    def sleeper(self, *argv, cwd):
        process = subprocess.Popen(["python3", "-c", "import time; time.sleep(60)", *argv], cwd=cwd)
        self.addCleanup(process.wait)
        self.addCleanup(process.kill)
        return process

    def local(self, run_dir):
        return self.volume_tmp / Path(run_dir).relative_to("/volume/tmp")

    def started(self, out):
        line = next(line for line in out.splitlines() if line.startswith("run directory: "))
        return line.split(": ", 1)[1]

    def test_gpus_ignores_keepalive_workers_and_reports_other_processes(self):
        keepalive = self.sleeper("/volume/cluster-ops/keepalive.py", "--occupy", "GPU-a", "1.0", cwd="/")
        other = self.sleeper("train.py", cwd=self.work)
        apps = f"GPU-a, {keepalive.pid}, 600\nGPU-b, {other.pid}, 50"
        code, out = self.job("gpus", "sh-0", "--gpus", "0", FAKE_APPS=apps)
        self.assertEqual(code, 0, out)
        self.assertIn("* GPU 0 free: 900 of 1000 MiB free", out)
        self.assertIn(f"pid {other.pid} (50 MiB) in {self.work}:", out)
        self.assertNotIn(f"pid {keepalive.pid}", out)
        self.assertEqual(self.job("gpus", "sh-0", FAKE_APPS=apps)[0], 1)
        self.assertEqual(self.job("gpus", "sh-0", "--gpus", "0", "--min-free-mib", "950", FAKE_APPS=apps)[0], 1)
        code, out = self.job("gpus", "sh-0", "--gpus", "0,7")
        self.assertEqual(code, 2, out)
        self.assertIn("has no GPU 7", out)

    def test_a_failed_process_query_is_not_an_idle_gpu(self):
        code, out = self.job("gpus", "sh-0", FAKE_APPS_FAIL="1")
        self.assertEqual(code, 2, out)
        self.assertNotIn("free:", out)
        code, out = self.job("start", "sh-0", "--topic", "t", "--gpus", "0", "--", "true", FAKE_APPS_FAIL="1")
        self.assertEqual(code, 2, out)
        self.assertEqual(list(self.volume_tmp.iterdir()), [])

    def test_start_refuses_busy_gpus_and_creates_nothing(self):
        other = self.sleeper("train.py", cwd=self.work)
        code, out = self.job("start", "sh-0", "--topic", "t", "--gpus", "1", "--", "true",
                             FAKE_APPS=f"GPU-b, {other.pid}, 50")
        self.assertEqual(code, 1, out)
        self.assertIn("nothing was started", out)
        self.assertEqual(list(self.volume_tmp.iterdir()), [])

    def test_a_job_runs_in_the_checkout_and_records_its_inputs(self):
        code, out = self.job("start", "sh-0", "--topic", "smoke", "--gpus", "0", "--",
                             "bash", "-c", 'echo "cwd=$PWD gpus=$CUDA_VISIBLE_DEVICES order=$CUDA_DEVICE_ORDER"')
        self.assertEqual(code, 0, out)
        run_dir = self.started(out)
        self.assertRegex(run_dir, r"^/volume/tmp/smoke-\d{8}-\w{6}$")
        code, out = self.job("wait", "sh-0", run_dir, "--interval", "1")
        self.assertEqual(code, 0, out)
        self.assertIn(f"succeeded: {run_dir}", out)
        self.assertIn(f"cwd={self.work} gpus=0 order=PCI_BUS_ID", out)
        record = (self.local(run_dir) / "record.txt").read_text()
        for line in (f"checkout: {self.work}", "node: sh-0", "branch: main",
                     f"commit: {git(self.work, 'rev-parse', 'HEAD')}", "working tree: 0 changed paths", "gpus: 0"):
            self.assertIn(line, record)
        self.assertIn("command: bash -c", record)

    def test_failures_are_reported_from_exit_status_or_its_absence(self):
        code, out = self.job("start", "th-0", "--topic", "fail", "--", "bash", "-c", "exit 3")
        run_dir = self.started(out)
        self.assertEqual(self.job("wait", "th-0", run_dir, "--interval", "1")[1].count("exited with 3"), 1)
        code, out = self.job("start", "th-0", "--topic", "term", "--", "sleep", "2")
        run_dir = self.started(out)
        os.kill(int((self.local(run_dir) / "run.pid").read_text()), signal.SIGTERM)
        code, out = self.job("wait", "th-0", run_dir, "--interval", "1")
        self.assertEqual(code, 1, out)
        self.assertIn("exited with 143", out)
        code, out = self.job("start", "th-0", "--topic", "gone", "--", "sleep", "1")
        run_dir = self.started(out)
        os.kill(int((self.local(run_dir) / "run.pid").read_text()), signal.SIGKILL)
        time.sleep(1.5)
        code, out = self.job("status", "th-0", run_dir)
        self.assertEqual(code, 1, out)
        self.assertIn("gone without exit.status", out)

    def test_running_jobs_time_out_and_need_the_launch_node(self):
        code, out = self.job("start", "sh-0", "--topic", "long", "--", "bash", "-c", "echo step-1; sleep 20")
        run_dir = self.started(out)
        time.sleep(0.5)
        (self.local(run_dir) / "run.pid").unlink()
        code, out = self.job("status", "sh-0", run_dir)
        self.assertEqual(code, 3, out)
        self.assertIn("step-1", out)
        (self.local(run_dir) / "exit.status").write_text("")
        code, out = self.job("status", "sh-0", run_dir)
        self.assertEqual(code, 3, out)
        self.assertNotIn("Traceback", out)
        began = time.monotonic()
        code, out = self.job("wait", "sh-0", run_dir, "--timeout", "1")
        self.assertEqual(code, 3, out)
        self.assertIn("still running", out)
        self.assertLess(time.monotonic() - began, 10)
        code, out = self.job("status", "sh-1", run_dir)
        self.assertEqual(code, 2, out)
        self.assertIn("launched on sh-0", out)
        began = time.monotonic()
        code, out = self.job("wait", "sh-0", run_dir, "--timeout", "1", FAKE_SSH_HANG="1")
        self.assertEqual(code, 2, out)
        self.assertIn("no answer", out)
        self.assertLess(time.monotonic() - began, 30)
        code, out = self.job("wait", "sh-0", run_dir, "--interval", "1")
        self.assertEqual(code, 0, out)
        self.assertEqual((self.local(run_dir) / "exit.status").read_text().strip(), "0")

    def test_start_validates_its_arguments(self):
        self.assertIn("--topic must be", self.job("start", "sh-0", "--topic", "a/b", "--", "true")[1])
        self.assertIn("job command after --", self.job("start", "sh-0", "--topic", "t")[1])


if __name__ == "__main__":
    unittest.main()
