#!/usr/bin/env python3
"""Validate repository metadata and local Markdown file links with installed tools."""

import argparse
import json
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


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_metadata(root, names):
    catalogs = [
        read_json(root / ".agents/plugins/marketplace.json"),
        read_json(root / ".claude-plugin/marketplace.json"),
    ]
    require(catalogs[0]["name"] == catalogs[1]["name"], "Marketplace names differ")
    for catalog in catalogs:
        entries = catalog["plugins"]
        require(
            len(entries) == len(names) and {p["name"] for p in entries} == set(names),
            "Each catalog must list every plugin exactly once",
        )
        for entry in entries:
            source = entry["source"]
            if isinstance(source, dict):
                require(source["source"] == "local", "Expected a local plugin source")
                source = source["path"]
            require(
                source == f"./plugins/{entry['name']}",
                f"Incorrect catalog source for {entry['name']}",
            )

    readme = (root / "README.md").read_text(encoding="utf-8")
    for name in names:
        plugin = root / "plugins" / name
        portable = read_json(plugin / "plugin.json")
        claude = read_json(plugin / ".claude-plugin/plugin.json")
        require(portable["name"] == claude["name"] == name, f"{name}: manifest names differ")
        require(
            portable["version"] == claude["version"], f"{name}: manifest versions differ"
        )
        versions = re.findall(
            rf"^\| \[{re.escape(name)}\]\([^\n)]+\) \| ([^|]+) \|", readme, re.MULTILINE
        )
        require(
            [v.strip() for v in versions] == [portable["version"]],
            f"{name}: README version differs or its row is missing/duplicated",
        )


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
    parser.add_argument("plugins", nargs="*", help="Plugin names; defaults to all plugins")
    args = parser.parse_args()
    try:
        names = sorted(p.name for p in (ROOT / "plugins").iterdir() if p.is_dir())
        selected = sorted(set(args.plugins)) if args.plugins else names
        require(bool(names), "No plugins found")
        unknown = sorted(set(selected) - set(names))
        require(not unknown, f"Unknown plugin(s): {', '.join(unknown)}")
        client = shutil.which("claude")
        require(client is not None, "Claude Code CLI is required: claude plugin validate --strict")
        check_metadata(ROOT, names)
        print("Catalog, manifest and README consistency passed", flush=True)
        check_links(ROOT, selected)
        paths = ["."]
        for name in selected:
            paths.extend([f"plugins/{name}", f"plugins/{name}/skills"])
        for path in paths:
            command = [client, "plugin", "validate", "--strict", path]
            print(f"+ {shlex.join(command)}", flush=True)
            subprocess.run(command, cwd=ROOT, check=True)
        print(f"Static validation passed: {', '.join(selected)}", flush=True)
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
