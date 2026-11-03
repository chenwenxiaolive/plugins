#!/usr/bin/env python3
"""Start, inspect, or stop the bundled Linux preview service."""
import argparse
import base64
import fcntl
import json
import os
from pathlib import Path
import select
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener
import uuid

SKILL = Path(__file__).resolve().parents[1]
SERVER = SKILL / 'server/server.py'
BOOT_ID = Path('/proc/sys/kernel/random/boot_id')


def overlap(left, right):
    return left.is_relative_to(right) or right.is_relative_to(left)


def configuration():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('start', 'status', 'stop'))
    for flag, variable, default in (
        ('directory', 'PREVIEW_ROOT', '/preview'),
        ('bind', 'PREVIEW_BIND', '127.0.0.1'),
        ('port', 'PREVIEW_PORT', '8000'),
        ('base-url', 'PREVIEW_BASE_URL', None),
        ('state-dir', 'PREVIEW_STATE_DIR', None),
        ('token-file', 'PREVIEW_TOKEN_FILE', None),
    ):
        parser.add_argument('--' + flag, default=os.environ.get(variable, default))
    args = parser.parse_args()
    try:
        args.port = int(args.port)
        if not 1 <= args.port <= 65535:
            raise ValueError()
    except ValueError:
        parser.error('Port must be an integer from 1 to 65535')
    try:
        socket.getaddrinfo(args.bind, args.port, socket.AF_INET, socket.SOCK_STREAM)
    except socket.gaierror:
        parser.error('Bind must be an IPv4 address or a resolvable IPv4 hostname')
    args.directory = Path(args.directory).expanduser().resolve()
    args.token_file = Path(args.token_file).expanduser().resolve() if args.token_file else None
    args.state_dir = Path(args.state_dir).expanduser().resolve() if args.state_dir else (
        Path.home() / '.local/state/preview' / socket.gethostname() / str(args.port)
    ).resolve()
    if overlap(args.state_dir, args.directory) or overlap(args.state_dir, SKILL):
        parser.error('State directory must be outside the document root and skill directory')
    if overlap(args.directory, SKILL):
        parser.error('Document root must be outside the skill directory')
    args.local_url = f'http://{"127.0.0.1" if args.bind == "0.0.0.0" else args.bind}:{args.port}'
    args.base_url = (args.base_url or args.local_url).rstrip('/')
    try:
        url = urlsplit(args.base_url)
        valid = (url.scheme in ('http', 'https') and url.hostname and not url.username
                 and not url.password and not url.query and not url.fragment)
        url.port
    except ValueError:
        valid = False
    if not valid:
        parser.error('Base URL must be an HTTP(S) URL without credentials, query, or fragment')
    if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
        parser.error('Linux with Python 3.10+ and pidfd support is required')
    return args


def process_identity(pid):
    """Use the kernel start time to distinguish a recorded PID from a reused PID."""
    try:
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        if fields[0] == 'Z':
            return None
        command = Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')[:-1]
        return {'start_ticks': fields[19], 'argv': [os.fsdecode(arg) for arg in command]}
    except FileNotFoundError:
        return None


def read_record(args):
    path = args.state_dir / 'service.json'
    if not path.exists():
        return None
    record = json.loads(path.read_text(encoding='utf-8'))
    if record.get('hostname') != socket.gethostname():
        raise RuntimeError('State belongs to another host; use a separate state directory')
    if record.get('boot_id') != BOOT_ID.read_text().strip():
        return None
    pid = record.get('pid')
    if not isinstance(pid, int) or pid <= 0:
        raise RuntimeError('Invalid process record; refusing to signal any process')
    identity = process_identity(pid)
    if identity is None:
        return None
    if identity != record.get('identity'):
        raise RuntimeError('Recorded process identity changed; refusing to adopt or stop it')
    return record


def check_configuration(args, record):
    if any(record[key] != value for key, value in (
        ('directory', str(args.directory)), ('bind', args.bind), ('port', args.port),
    )):
        raise RuntimeError('Managed service uses different settings; use its original configuration to stop it')


def occupied(args):
    try:
        with socket.create_connection((urlsplit(args.local_url).hostname, args.port), timeout=0.5):
            return True
    except ConnectionRefusedError:
        return False


def healthy(args):
    """Check actual rendering and the selected root, including legacy servers."""
    marker = 'preview-health-' + uuid.uuid4().hex
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.md',
                                     prefix='preview-probe-', dir=args.directory) as probe:
        probe.write('# ' + marker + '\n')
        probe.flush()
        client = build_opener(ProxyHandler({}))
        headers = {}
        if args.token_file:
            token = args.token_file.read_text(encoding='utf-8').rstrip('\r\n')
            headers['Authorization'] = 'Basic ' + base64.b64encode(f'preview:{token}'.encode()).decode()
        try:
            request = Request(args.local_url + '/' + Path(probe.name).name, headers=headers)
            with client.open(request, timeout=2) as response:
                return (response.headers.get_content_type() == 'text/html'
                        and f'<h1 id="{marker}">{marker}</h1>'.encode() in response.read(65536))
        except (URLError, TimeoutError, ConnectionError):
            return False


def output(args, status, record=None):
    result = {'status': status, 'directory': str(args.directory), 'bind': args.bind,
              'port': args.port, 'base_url': args.base_url, 'state_dir': str(args.state_dir)}
    if record:
        result.update(pid=record['pid'], log=record['log'])
    print(json.dumps(result))


def stop(args, record):
    if not record:
        if occupied(args):
            raise RuntimeError('Endpoint is externally managed; this helper will not stop it')
        output(args, 'stopped')
        return 0
    check_configuration(args, record)
    # Open before checking identity again: signals then target this process even if the PID is reused.
    try:
        descriptor = os.pidfd_open(record['pid'])
    except ProcessLookupError:
        output(args, 'stopped')
        return 0
    try:
        if process_identity(record['pid']) != record['identity']:
            raise RuntimeError('Process identity changed before stop; no signal sent')
        signal.pidfd_send_signal(descriptor, signal.SIGTERM)
        if not select.select([descriptor], [], [], 5)[0]:
            raise RuntimeError('Service did not stop within 5 seconds; process record retained')
    finally:
        os.close(descriptor)
    (args.state_dir / 'service.json').unlink(missing_ok=True)
    output(args, 'stopped')
    return 0


def start(args):
    node = shutil.which('node')
    if not node:
        raise RuntimeError('Node.js 18+ must be available on PATH')
    version = subprocess.run([node, '-p', 'process.versions.node.split(".")[0]'],
                             capture_output=True, text=True, timeout=5, check=True)
    if int(version.stdout.strip()) < 18:
        raise RuntimeError('Node.js 18+ is required')
    run = Path(tempfile.mkdtemp(prefix=time.strftime('run-%Y%m%d-%H%M%S-'), dir=args.state_dir))
    log_path = run / 'server.log'
    argv = [sys.executable, '-B', '-u', str(SERVER), '--directory', str(args.directory),
            '--bind', args.bind, '--port', str(args.port)]
    if args.token_file:
        argv += ['--token-file', str(args.token_file)]
    process = None
    try:
        with log_path.open('ab') as log:
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       cwd=run, start_new_session=True, close_fds=True)
        record = {'pid': process.pid, 'identity': process_identity(process.pid),
                  'hostname': socket.gethostname(), 'boot_id': BOOT_ID.read_text().strip(),
                  'directory': str(args.directory), 'bind': args.bind, 'port': args.port,
                  'log': str(log_path)}
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'Service exited during startup; inspect {log_path}')
            if occupied(args) and healthy(args) and process.poll() is None:
                # Refresh after exec has completed, then atomically publish the ownership record.
                record['identity'] = process_identity(process.pid)
                pending = args.state_dir / 'service.json.tmp'
                pending.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
                pending.replace(args.state_dir / 'service.json')
                output(args, 'running', record)
                return 0
            time.sleep(0.1)
        raise RuntimeError(f'Service did not become ready; inspect {log_path}')
    except BaseException:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        raise


def main():
    args = configuration()
    # The stable directory and advisory lock also serialize commands from different skill versions.
    args.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (args.state_dir / 'service.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        record = read_record(args)
        if args.command == 'stop':
            return stop(args, record)
        if not args.directory.is_dir():
            raise RuntimeError('The preview document directory must already exist')
        if record:
            check_configuration(args, record)
            if not healthy(args):
                raise RuntimeError('Managed service is running but its rendering check failed')
            output(args, 'running', record)
            return 0
        if occupied(args):
            if not healthy(args):
                raise RuntimeError('Port is occupied by an incompatible service or a different document root')
            output(args, 'reused')
            return 0
        if args.command == 'status':
            output(args, 'stopped')
            return 1
        return start(args)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'Preview error: {error}', file=sys.stderr)
        sys.exit(1)
