---
tags: [to-tickets]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/to-tickets as a draft only, do not publish: Rename the private report helper `_fmt_row` to `_format_row` and update its two callers. Keep its signature and behavior unchanged. Existing public-API tests exercise both callers, including empty and populated reports. No user or developer documentation mentions this helper. Draft the issue with acceptance criteria and validation.
