---
tags: [implement]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use implement to show the smallest code change and tests for two versions of
this feature. Do not run commands or publish anything.

```python
def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())
```

Add `load_manifests(directory: Path) -> list[dict]`, which loads every `*.json`
file in the directory in file-name order for the `sync` command that someone
runs by hand and watches.

A. The issue asks only for that. Some files on the shared volume may be
   unreadable or hold invalid JSON; the issue says nothing about them.
B. The same, but the issue adds: one malformed manifest must not stop a sync;
   skip it and print its file name on stderr.
