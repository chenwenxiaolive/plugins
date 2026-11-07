---
tags: [implement]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use implement to describe the documentation and validation needed for these two unrelated tasks before delivery. Do not run commands or publish anything.

1. Rename a private helper from `_fmt_row` to `_format_row` and update its two callers. Its signature and behavior stay the same. Existing tests exercise both callers through the public API. No documentation mentions the helper.
2. Add `--format json` to a report CLI. The requested contract is a JSON array of objects with `name` and `count` fields on stdout, including `[]` for an empty report. Current tests cover text output only, and the usage guide describes text output only.
