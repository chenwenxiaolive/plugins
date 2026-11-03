#!/usr/bin/env python3
"""Compare shared skill installations with committed source without changing files."""

import argparse
import json
from pathlib import Path
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def source_skills(ref):
    sha = git("rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").decode().strip()
    entries = {}
    for line in git("ls-tree", "-rz", sha, "--", "plugins/").split(b"\0"):
        if not line:
            continue
        metadata, raw_path = line.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        entries[raw_path.decode()] = (mode, kind, oid)
    skills = {}
    for path in entries:
        parts = path.split("/")
        if len(parts) != 5 or parts[2] != "skills" or parts[4] != "SKILL.md":
            continue
        name = parts[3]
        if name in skills:
            raise ValueError(f"Duplicate skill name: {name}")
        prefix = path.rsplit("/", 1)[0] + "/"
        skills[name] = {p[len(prefix):]: entry for p, entry in entries.items() if p.startswith(prefix)}
    if not skills:
        raise ValueError("No skills found in the source commit")
    return sha, skills


def compare_files(directory, expected):
    differences = []
    if directory.is_symlink() or not directory.is_dir():
        return ["shared skill directory is missing or is a symlink"]
    actual = {
        p.relative_to(directory).as_posix()
        for p in directory.rglob("*")
        if p.is_symlink() or not p.is_dir()
    }
    for name in sorted(actual - expected.keys()):
        differences.append(f"extra file: {name}")
    for name, (mode, kind, oid) in sorted(expected.items()):
        path = directory / name
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"Unsupported source file type: {name} ({mode})")
        if path.is_symlink() or not path.is_file():
            differences.append(f"missing or non-regular file: {name}")
            continue
        if stat.S_IMODE(path.stat().st_mode) != int(mode, 8) & 0o777:
            differences.append(f"file mode differs: {name}")
        if path.read_bytes() != git("cat-file", "blob", oid):
            differences.append(f"file contents differ: {name}")
    return differences


def check_installation(skills, user_dir):
    differences = []
    lock_path = user_dir / ".agents/.skill-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.is_file() else {}
    records = lock.get("skills", {})
    for name, files in sorted(skills.items()):
        shared = user_dir / ".agents/skills" / name
        for message in compare_files(shared, files):
            differences.append(f"{name}: {message}")
        link = user_dir / ".claude/skills" / name
        if not link.is_symlink() or link.resolve() != shared.resolve():
            differences.append(f"{name}: Claude Code symlink is missing or points elsewhere")
        record = records.get(name, {})
        if record.get("sourceType") != "local" or record.get("source") != str(ROOT):
            differences.append(f"{name}: lock entry is missing or has a different source")
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", default="HEAD", help="Source commit or ref (default: HEAD)")
    args = parser.parse_args()
    try:
        sha, skills = source_skills(args.source_ref)
        print(f"Comparing {len(skills)} installed skills with {ROOT} at {sha}", flush=True)
        differences = check_installation(skills, Path.home())
        for difference in differences:
            print(f"DIFF: {difference}")
        if differences:
            print("Installation differs; inspect the differences before replacing installed files.")
            return 1
        print("Installation matches: file contents, modes, Claude Code links and local sources.")
        return 0
    except (OSError, ValueError, TypeError, AttributeError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Installation check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
