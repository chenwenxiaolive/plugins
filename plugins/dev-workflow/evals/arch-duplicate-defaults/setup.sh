#!/usr/bin/env bash
set -euo pipefail
mkdir -p app tests
cat > app/config.py <<'EOF'
import json

DEFAULTS = {"timeout": 30, "retries": 3, "cache_dir": "/volume/cache"}


def load(path):
    with open(path) as f:
        return {**DEFAULTS, **json.load(f)}
EOF
cat > app/loader.py <<'EOF'
import json

DEFAULT_SETTINGS = {"timeout": 60, "retries": 3, "cache_dir": "/volume/cache"}


def read_settings(path):
    with open(path) as f:
        return {**DEFAULT_SETTINGS, **json.load(f)}
EOF
cat > app/server.py <<'EOF'
from app.config import load
from app.loader import read_settings


def start(cfg_path, worker_cfg_path):
    cfg = load(cfg_path)
    worker = read_settings(worker_cfg_path)
    return cfg["timeout"], worker["timeout"]
EOF
touch app/__init__.py
