"""Verify the bundled third-party renderer and license against their sources."""
import hashlib
import json
from pathlib import Path
import unittest

SERVER = Path(__file__).resolve().parents[2] / 'plugins/preview/skills/preview/server'


class AssetTests(unittest.TestCase):
    def test_renderer_integrity(self):
        for source in json.loads((SERVER / 'assets/sources.json').read_text()):
            self.assertEqual(hashlib.sha256((SERVER / 'assets' / source['file']).read_bytes()).hexdigest(),
                             source['sha256'])
