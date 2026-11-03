"""Exercise run-build.sh against fake sudo and docker commands; nothing is built or pushed."""

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins/docker-build/skills/docker-build/scripts/run-build.sh"
IMAGE = "registry-cn-shanghai.siflow.cn/skyinfer/demo:20261103-abc1234"
DIGEST = "sha256:" + "a" * 64

FAKE_DOCKER = r"""#!/usr/bin/env python3
import json, os, sys, time
args = sys.argv[1:]
with open(os.environ["FAKE_CALLS"], "a") as log:
    log.write(json.dumps(args) + "\n")
digest = "sha256:" + "a" * 64
if args[:2] == ["buildx", "build"]:
    time.sleep(float(os.environ.get("FAKE_BUILD_SECONDS", "0")))
    with open(args[args.index("--metadata-file") + 1], "w") as meta:
        json.dump({"containerimage.digest": digest}, meta)
elif args[:3] == ["buildx", "imagetools", "inspect"]:
    if "--raw" in args:
        manifest = json.loads(os.environ.get("FAKE_MANIFEST", "{}")) or {
            "mediaType": "application/vnd.oci.image.manifest.v1+json"}
        print(json.dumps(manifest))
    elif "--format" in args:
        print(json.dumps({"digest": os.environ.get("FAKE_REGISTRY_DIGEST", digest)}))
    else:
        print("Name: " + args[-1])
else:
    sys.exit("unexpected docker call")
"""


class RunBuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="run-build-", dir=os.environ.get("RUN_BUILD_TEST_TMPDIR")))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.task = self.tmp / "task"
        (self.task / "ctx").mkdir(parents=True)
        (self.task / "ctx/Dockerfile").write_text("FROM scratch\n")
        shutil.copy(SCRIPT, self.task / "run-build.sh")
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "sudo").write_text('#!/bin/sh\nexec "$@"\n')
        (bin_dir / "docker").write_text(FAKE_DOCKER)
        for tool in bin_dir.iterdir():
            tool.chmod(0o755)
        self.calls = self.tmp / "calls.log"
        self.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_CALLS": str(self.calls)}

    def start(self, *args, **env):
        return subprocess.Popen(
            ["bash", str(self.task / "run-build.sh"), *args],
            cwd=self.tmp, env={**self.env, **env},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )

    def run_build(self, *args, **env):
        process = self.start(*args, **env)
        out, err = process.communicate(timeout=30)
        return process.returncode, out, err

    def docker_calls(self):
        if not self.calls.exists():
            return []
        return [json.loads(line) for line in self.calls.read_text().splitlines()]

    def status(self):
        return (self.task / "build.status").read_text().strip()

    def test_publishes_and_verifies_one_manifest(self):
        code, out, err = self.run_build(IMAGE, "--build-arg", "PIP_INDEX_URL=https://example.invalid/simple")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.status(), "0")
        self.assertIn(f"Verified {IMAGE}@{DIGEST}", out)
        build = self.docker_calls()[0]
        for flag in ["--builder", "default", "--provenance=false", "--sbom=false", "--push"]:
            self.assertIn(flag, build)
        self.assertEqual(build[-3:], ["--build-arg", "PIP_INDEX_URL=https://example.invalid/simple", "ctx"])
        for name in ["build-metadata.json", "image-inspect.txt", "image-inspect.json", "image-manifest.json"]:
            self.assertTrue((self.task / name).is_file(), name)

    def test_rejects_other_registries_and_missing_tags(self):
        for image in ["", "docker.io/library/demo:1", "registry-cn-shanghai.siflow.cn/skyinfer/demo"]:
            code, _, err = self.run_build(image)
            self.assertEqual(code, 2, image)
            self.assertIn("usage:", err)
            self.assertEqual(self.status(), "2")
        self.assertEqual(self.docker_calls(), [])

    def test_requires_a_dockerfile(self):
        (self.task / "ctx/Dockerfile").unlink()
        code, _, err = self.run_build(IMAGE)
        self.assertEqual(code, 1)
        self.assertIn("ctx/Dockerfile is missing", err)
        self.assertEqual(self.docker_calls(), [])

    def test_fails_on_registry_digest_mismatch(self):
        code, _, err = self.run_build(IMAGE, FAKE_REGISTRY_DIGEST="sha256:" + "b" * 64)
        self.assertEqual(code, 1)
        self.assertIn("digest mismatch", err)
        self.assertEqual(self.status(), "1")

    def test_fails_on_an_image_index(self):
        index = {"mediaType": "application/vnd.oci.image.index.v1+json", "manifests": []}
        code, _, err = self.run_build(IMAGE, FAKE_MANIFEST=json.dumps(index))
        self.assertEqual(code, 1)
        self.assertIn("found an index", err)
        self.assertEqual(self.status(), "1")

    def test_records_a_terminated_build_as_143(self):
        process = self.start(IMAGE, FAKE_BUILD_SECONDS="2")
        deadline = time.monotonic() + 10
        while not self.docker_calls() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(self.docker_calls(), "build did not start")
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=30)
        self.assertEqual(process.returncode, 143)
        self.assertEqual(self.status(), "143")


if __name__ == "__main__":
    unittest.main()
