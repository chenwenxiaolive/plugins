#!/usr/bin/env python3
"""Validate local Markdown links and skill frontmatter with the installed Claude Code CLI."""

import argparse
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def markdown_source(path):
    # Repository documentation uses inline Markdown links. Ignore fenced examples.
    return re.sub(
        r"^```[^\n]*\n.*?^```[^\n]*$",
        "",
        path.read_text(encoding="utf-8"),
        flags=re.MULTILINE | re.DOTALL,
    )


def heading_anchors(path):
    """GitHub-style heading slugs, with -1, -2 suffixes for repeated headings."""
    anchors = set()
    for match in re.finditer(r"^#{1,6}[ \t]+(.+?)[ \t#]*$", markdown_source(path), re.MULTILINE):
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", match[1])
        base = re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")
        slug, n = base, 0
        while slug in anchors:
            n += 1
            slug = f"{base}-{n}"
        anchors.add(slug)
    return anchors


def check_links(root, names):
    files = [root / "README.md"]
    for name in names:
        files.extend(sorted((root / "plugins" / name).rglob("*.md")))
    checked = anchored = 0
    for path in files:
        for match in re.finditer(
            r"\[[^\]\n]+\]\((<[^>\n]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)", markdown_source(path)
        ):
            target = match[1].strip("<>")
            url = urlsplit(target)
            if url.scheme or url.netloc or url.path.startswith(("/", "~")):
                continue
            linked = path.parent / unquote(url.path) if url.path else path
            if url.path:
                require(linked.exists(), f"{path.relative_to(root)}: missing link target {target}")
                checked += 1
            if url.fragment and linked.suffix == ".md":
                require(
                    unquote(url.fragment) in heading_anchors(linked),
                    f"{path.relative_to(root)}: missing heading anchor {target}",
                )
                anchored += 1
    print(f"Local Markdown links passed ({checked} files, {anchored} anchors)", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("groups", nargs="*", help="Skill groups under plugins/; defaults to all")
    args = parser.parse_args()
    try:
        names = sorted(p.name for p in (ROOT / "plugins").iterdir() if (p / "skills").is_dir())
        selected = sorted(set(args.groups)) if args.groups else names
        require(bool(names), "No skill groups found")
        unknown = sorted(set(selected) - set(names))
        require(not unknown, f"Unknown group(s): {', '.join(unknown)}")
        client = shutil.which("claude")
        require(client is not None, "Claude Code CLI is required: claude plugin validate --strict")
        check_links(ROOT, selected)
        for path in [f"plugins/{name}/skills" for name in selected]:
            command = [client, "plugin", "validate", "--strict", path]
            print(f"+ {shlex.join(command)}", flush=True)
            subprocess.run(command, cwd=ROOT, check=True)
        print(f"Static validation passed: {', '.join(selected)}", flush=True)
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
