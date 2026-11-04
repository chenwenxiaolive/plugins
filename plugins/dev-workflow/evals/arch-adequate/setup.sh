#!/usr/bin/env bash
set -euo pipefail
mkdir -p app tests
cat > app/units.py <<'EOF'
def gib(n_bytes):
    return n_bytes / 2**30


def hours(seconds):
    return seconds / 3600
EOF
cat > app/report.py <<'EOF'
from app.units import gib, hours


def summary(job):
    return f"{job['name']}: {gib(job['bytes']):.1f} GiB in {hours(job['seconds']):.1f} h"
EOF
cat > tests/test_report.py <<'EOF'
from app.report import summary


def test_summary():
    assert summary({"name": "a", "bytes": 2**31, "seconds": 7200}) == "a: 2.0 GiB in 2.0 h"
EOF
touch app/__init__.py
