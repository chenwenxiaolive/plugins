"""Exercise browser-env.sh against fake uv, apt-get, dpkg and ldd; nothing is downloaded or installed."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / 'plugins/preview/skills/preview/scripts/browser-env.sh'

LOG = r'''import json, os, sys
with open(os.environ["FAKE_CALLS"], "a") as log:
    log.write(json.dumps({"tool": os.path.basename(sys.argv[0]), "args": sys.argv[1:], "cwd": os.getcwd(),
                          "env": {k: os.environ.get(k) for k in ("PLAYWRIGHT_BROWSERS_PATH", "LD_LIBRARY_PATH", "FONTCONFIG_FILE")}}) + "\n")
'''
FAKE_VENV_PYTHON = '#!/usr/bin/env python3\n' + LOG + r'''
args = sys.argv[1:]
if args[:3] == ["-m", "playwright", "install"]:
    shell = os.path.join(os.environ["PLAYWRIGHT_BROWSERS_PATH"], "chromium_headless_shell-1",
                         "chrome-headless-shell-linux64", "chrome-headless-shell")
    os.makedirs(os.path.dirname(shell), exist_ok=True)
    open(shell, "w").close()
'''
FAKES = {
    'uv': '#!/usr/bin/env python3\n' + LOG + r'''
args = sys.argv[1:]
if args[0] == "venv":
    target = os.path.join(args[-1], "bin", "python")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w") as out:
        out.write(open(os.environ["FAKE_VENV_PYTHON"]).read())
    os.chmod(target, 0o755)
''',
    'apt-get': '#!/usr/bin/env python3\n' + LOG + r'''
args = sys.argv[1:]
if "download" in args:
    for package in args[args.index("download") + 1:]:
        open(f"{package}_1_amd64.deb", "w").close()
''',
    'dpkg': '#!/usr/bin/env python3\n' + LOG + r'''
args = sys.argv[1:]
if args[0] == "-x":
    deb, root = os.path.basename(args[1]), args[2]
    lib = os.path.join(root, "usr/lib/x86_64-linux-gnu")
    os.makedirs(lib, exist_ok=True)
    open(os.path.join(lib, deb + ".so"), "w").close()
    if deb.startswith("fonts-") and not os.environ.get("FAKE_NO_FONTS"):
        fonts = os.path.join(root, "usr/share/fonts/truetype")
        os.makedirs(fonts, exist_ok=True)
        open(os.path.join(fonts, deb + ".ttf"), "w").close()
''',
    'ldd': '#!/usr/bin/env python3\n' + LOG + r'''
if os.environ.get("FAKE_LDD_MISSING"):
    print("\tlibnss3.so => not found")
print("\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6")
''',
}


class BrowserEnvTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='browser-env-', dir=os.environ.get('PREVIEW_TEST_TMPDIR')))
        self.addCleanup(shutil.rmtree, self.tmp)
        bin_dir = self.tmp / 'bin'
        bin_dir.mkdir()
        for name, body in FAKES.items():
            (bin_dir / name).write_text(body)
            (bin_dir / name).chmod(0o755)
        venv_python = self.tmp / 'venv-python'
        venv_python.write_text(FAKE_VENV_PYTHON)
        self.calls = self.tmp / 'calls.log'
        self.env_dir = self.tmp / 'env'
        self.env = {**os.environ, 'PATH': f"{bin_dir}:{os.environ['PATH']}", 'FAKE_CALLS': str(self.calls),
                    'FAKE_VENV_PYTHON': str(venv_python)}

    def run_script(self, **extra):
        return subprocess.run(['bash', str(SCRIPT), str(self.env_dir)], env={**self.env, **extra},
                              capture_output=True, text=True, timeout=60)

    def calls_of(self, tool):
        lines = self.calls.read_text().splitlines() if self.calls.exists() else []
        return [call for call in map(json.loads, lines) if call['tool'] == tool]

    def test_builds_in_user_space_without_touching_system_apt_state(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        apt = self.calls_of('apt-get')
        self.assertTrue(any('update' in c['args'] for c in apt) and any('download' in c['args'] for c in apt))
        for call in apt:
            options = call['args']
            self.assertIn(f'Dir::State::Lists={self.env_dir}/apt/lists', options)
            self.assertIn(f'Dir::Cache={self.env_dir}/apt/cache', options)
            self.assertIn(f'Dir::Etc::sourcelist={self.env_dir}/apt/sources.list', options)
            self.assertIn('Dir::Etc::sourceparts=-', options)
        dpkg = self.calls_of('dpkg')
        self.assertTrue(dpkg)
        for call in dpkg:
            self.assertEqual(call['args'][0], '-x')
            self.assertEqual(call['args'][2], f'{self.env_dir}/root')
        self.assertIn(f'<dir>{self.env_dir}/root/usr/share/fonts</dir>', (self.env_dir / 'fonts.conf').read_text())

    def test_wrapper_runs_python_with_the_browser_environment(self):
        self.assertEqual(self.run_script().returncode, 0)
        wrapper = self.env_dir / 'python'
        self.assertTrue(os.access(wrapper, os.X_OK))
        subprocess.run([str(wrapper), '-c', 'pass'], env=self.env, check=True, timeout=30)
        seen = [c for c in self.calls_of('python') if c['args'] == ['-c', 'pass']][-1]['env']
        self.assertEqual(seen, {
            'PLAYWRIGHT_BROWSERS_PATH': f'{self.env_dir}/browsers',
            'LD_LIBRARY_PATH': f'{self.env_dir}/root/usr/lib/x86_64-linux-gnu',
            'FONTCONFIG_FILE': f'{self.env_dir}/fonts.conf',
        })

    def test_a_missing_shared_library_fails_the_build(self):
        result = self.run_script(FAKE_LDD_MISSING='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('libnss3.so', result.stderr)

    def test_missing_fonts_fail_the_build(self):
        result = self.run_script(FAKE_NO_FONTS='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('font', result.stderr.lower())


if __name__ == '__main__':
    unittest.main()
