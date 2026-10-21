"""Verify the installed bundle can be traced back to its pinned source."""
import hashlib
import json
from pathlib import Path
import unittest

SERVER = Path(__file__).resolve().parents[2] / 'plugins/preview/skills/preview/server'


class BundleTests(unittest.TestCase):
    def test_pinned_files_and_renderer_integrity(self):
        manifest = json.loads((SERVER / 'upstream.json').read_text())
        self.assertRegex(manifest['commit'], r'^[0-9a-f]{40}$')
        for name, digest in manifest['sha256'].items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((SERVER / name).read_bytes()).hexdigest(), digest)
        for source in json.loads((SERVER / 'assets/sources.json').read_text()):
            self.assertEqual(hashlib.sha256((SERVER / 'assets' / source['file']).read_bytes()).hexdigest(),
                             source['sha256'])
