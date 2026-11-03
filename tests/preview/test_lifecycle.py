"""Check the public service commands against real HTTP endpoints."""
import base64
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / 'plugins/preview/skills/preview/scripts/preview.py'
SERVER = REPO / 'plugins/preview/skills/preview/server/server.py'


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('PREVIEW_TEST_TMPDIR'))
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'documents'
        self.root.mkdir()
        self.state = self.base / 'state'
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            self.port = sock.getsockname()[1]
        self.url = f'http://127.0.0.1:{self.port}'
        self.client = build_opener(ProxyHandler({}))
        self.addCleanup(lambda: self.command('stop', check=False))

    def command(self, action, *extra, check=True, state=None):
        result = subprocess.run([
            sys.executable, '-B', str(SCRIPT), action,
            '--directory', str(self.root), '--state-dir', str(state or self.state),
            '--bind', '127.0.0.1', '--port', str(self.port), *extra,
        ], capture_output=True, text=True, timeout=20)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)
        return result

    def test_start_render_status_stop_preserves_documents(self):
        (self.root / 'report.md').write_text('# Lifecycle marker\n', encoding='utf-8')
        started = self.command('start')
        self.assertEqual(started['status'], 'running')
        with self.client.open(self.url + '/report.md', timeout=5) as response:
            self.assertIn(b'<h1 id="lifecycle-marker">', response.read())
        self.assertEqual(self.command('status')['pid'], started['pid'])
        self.assertEqual(self.command('start')['pid'], started['pid'])
        self.assertEqual(self.command('stop')['status'], 'stopped')
        self.assertNotEqual(self.command('status', check=False).returncode, 0)
        self.assertEqual([p.name for p in self.root.iterdir()], ['report.md'])

    def test_token_file_protects_every_page(self):
        (self.root / 'report.md').write_text('# Token marker\n', encoding='utf-8')
        token = self.base / 'token'
        token.write_text('lifecycle token.\n', encoding='utf-8')
        token.chmod(0o644)
        self.assertNotEqual(self.command('start', '--token-file', str(token), check=False).returncode, 0)
        token.chmod(0o600)
        open_service = self.command('start')
        self.assertNotEqual(self.command('start', '--token-file', str(token), check=False).returncode, 0)
        self.assertNotEqual(self.command('start', '--token-file', str(token), state=self.base / 'other-state',
                                         check=False).returncode, 0)
        self.assertEqual(self.command('stop')['status'], 'stopped')
        started = self.command('start', '--token-file', str(token))
        self.assertNotEqual(started['pid'], open_service['pid'])
        self.assertEqual(started['status'], 'running')
        self.assertEqual(self.command('status', '--token-file', str(token))['pid'], started['pid'])
        self.assertNotEqual(self.command('status', check=False).returncode, 0)
        with self.assertRaises(HTTPError) as error:
            self.client.open(self.url + '/report.md', timeout=5)
        self.assertEqual(error.exception.code, 401)
        credentials = base64.b64encode(b'anyone:lifecycle token.').decode()
        request = Request(self.url + '/report.md', headers={'Authorization': 'Basic ' + credentials})
        with self.client.open(request, timeout=5) as response:
            self.assertIn(b'<h1 id="token-marker">', response.read())
        self.assertNotIn('lifecycle token', ' '.join(self.process_argv(started['pid'])))
        self.assertEqual(self.command('stop', '--token-file', str(token))['status'], 'stopped')
        inside = self.root / 'token'
        inside.write_text('lifecycle token.\n', encoding='utf-8')
        inside.chmod(0o600)
        self.assertNotEqual(self.command('start', '--token-file', str(inside), check=False).returncode, 0)

    @staticmethod
    def process_argv(pid):
        return Path(f'/proc/{pid}/cmdline').read_bytes().decode().split('\0')

    def test_reuse_does_not_take_ownership(self):
        started = self.command('start')
        other = self.base / 'other-state'
        self.assertEqual(self.command('start', state=other)['status'], 'reused')
        self.assertEqual(self.command('status', state=other)['status'], 'reused')
        self.assertNotEqual(self.command('stop', state=other, check=False).returncode, 0)
        self.assertEqual(self.command('status')['pid'], started['pid'])

    def test_occupied_port_and_different_root_are_rejected(self):
        self.command('start')
        other_root = self.base / 'other-documents'
        other_root.mkdir()
        result = self.command('start', '--directory', str(other_root),
                              state=self.base / 'other-state', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(other_root.iterdir()), [])
        self.assertEqual(self.command('status')['status'], 'running')

    def test_runtime_files_cannot_be_served(self):
        result = self.command('start', state=self.root / 'state', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_unrelated_pid_is_never_stopped(self):
        self.command('start')
        record_path = self.state / 'service.json'
        saved = record_path.read_text()
        record = json.loads(saved)
        record['pid'] = os.getpid()
        record_path.write_text(json.dumps(record))
        try:
            self.assertNotEqual(self.command('stop', check=False).returncode, 0)
            os.kill(os.getpid(), 0)
        finally:
            record_path.write_text(saved)

    def test_concurrent_starts_share_one_process(self):
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.command('start'), range(2)))
        self.assertEqual(results[0]['pid'], results[1]['pid'])

    def test_environment_configuration_and_flag_precedence(self):
        env = os.environ.copy()
        env.update(PREVIEW_ROOT=str(self.root), PREVIEW_STATE_DIR=str(self.state),
                   PREVIEW_BIND='127.0.0.1', PREVIEW_PORT=str(self.port),
                   PREVIEW_BASE_URL='https://preview.example.test/documents')
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'start'],
                                env=env, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['base_url'],
                         'https://preview.example.test/documents')
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'status',
                                 '--base-url', self.url], env=env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['base_url'], self.url)

    def test_unrelated_http_server_is_not_reused(self):
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
        from functools import partial
        import threading
        httpd = ThreadingHTTPServer(('127.0.0.1', self.port),
                                   partial(SimpleHTTPRequestHandler, directory=str(self.root)))
        worker = threading.Thread(target=httpd.serve_forever, daemon=True)
        worker.start()
        try:
            result = self.command('start', check=False)
            self.assertNotEqual(result.returncode, 0)
            with self.client.open(self.url, timeout=5) as response:
                self.assertEqual(response.status, 200)
        finally:
            httpd.shutdown()
            httpd.server_close()
            worker.join()

    def test_state_inside_skill_is_rejected(self):
        result = self.command('start', state=SCRIPT.parent / 'runtime', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((SCRIPT.parent / 'runtime').exists())
