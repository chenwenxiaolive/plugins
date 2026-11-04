"""Exercise check_installation.compare_files on a copy of a committed skill."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("check_installation", ROOT / "scripts/check_installation.py")
check_installation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_installation)


class CompareFilesTest(unittest.TestCase):
    def setUp(self):
        _, skills = check_installation.source_skills("HEAD")
        self.expected = skills["gpu-cluster"]
        self.tmp = Path(tempfile.mkdtemp(prefix="install-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.installed = self.tmp / "gpu-cluster"
        for name, (mode, _, oid) in self.expected.items():
            path = self.installed / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(subprocess.check_output(["git", "cat-file", "blob", oid], cwd=ROOT))
            path.chmod(int(mode, 8) & 0o777)

    def test_a_faithful_copy_matches(self):
        self.assertEqual(check_installation.compare_files(self.installed, self.expected), [])

    def test_python_bytecode_caches_are_ignored(self):
        cache = self.installed / "scripts/__pycache__"
        cache.mkdir(parents=True)
        (cache / "checkout.cpython-310.pyc").write_bytes(b"\0")
        self.assertEqual(check_installation.compare_files(self.installed, self.expected), [])

    def test_other_extra_and_changed_files_are_reported(self):
        (self.installed / "notes.txt").write_text("local edit")
        with (self.installed / "SKILL.md").open("a") as skill:
            skill.write("\nlocal edit\n")
        self.assertEqual(check_installation.compare_files(self.installed, self.expected),
                         ["extra file: notes.txt", "file contents differ: SKILL.md"])


if __name__ == "__main__":
    unittest.main()
