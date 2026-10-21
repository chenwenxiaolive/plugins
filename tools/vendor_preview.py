#!/usr/bin/env python3
"""Export a pinned preview-server commit into the preview plugin."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

FILES = (
    'server.py', 'renderer.cjs', 'assets/style.css', 'assets/theme.js',
    'assets/markdown-it.min.cjs', 'assets/markdown-it.LICENSE', 'assets/sources.json',
    'tests/test_preview.py', 'tests/theme.test.cjs',
)
DESTINATION = Path(__file__).resolve().parents[1] / 'plugins/preview/skills/preview/server'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--commit', required=True, help='Full 40-character Git commit SHA')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.commit):
        parser.error('--commit must be a full lowercase Git commit SHA')
    # Read every file before writing so an incomplete source does not partly update the bundle.
    files = {name: subprocess.check_output([
        'git', '-C', str(args.source), 'show', f'{args.commit}:{name}',
    ]) for name in FILES}
    for name, data in files.items():
        target = DESTINATION / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest = {
        'repository': 'https://github.com/chenwenxiaolive/preview-server',
        'commit': args.commit,
        'sha256': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
    }
    (DESTINATION / 'upstream.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Exported {len(files)} files from {args.commit}')


if __name__ == '__main__':
    main()
