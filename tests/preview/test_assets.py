"""Verify the bundled third-party renderers and licenses against their sources."""
import hashlib
import json
from pathlib import Path
import unittest

SERVER = Path(__file__).resolve().parents[2] / 'plugins/preview/skills/preview/server'


class AssetTests(unittest.TestCase):
    def test_renderer_integrity(self):
        for directory in (SERVER / 'assets', SERVER / 'prototypes/react-flow/vendor'):
            for source in json.loads((directory / 'sources.json').read_text()):
                with self.subTest(file=source['file']):
                    self.assertEqual(hashlib.sha256((directory / source['file']).read_bytes()).hexdigest(),
                                     source['sha256'])
