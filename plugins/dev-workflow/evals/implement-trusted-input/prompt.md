---
tags: [implement]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use implement to show the smallest code change and validation needed for this feature. Do not run commands or publish anything.

```python
def summary(report: Report) -> str:
    return f"{len(report.files)} files"
```

Append the total size, for example `2 files, 7 bytes`. Every caller passes a `Report` from `parse_report`, which validates the external input and constructs a list of typed `File` objects with required nonnegative integer `size_bytes` fields. Parser tests already cover missing, null and wrong-type fields. The existing summary tests check an empty list and two files of sizes 3 and 4.

Show what needs to change in the function and tests. Once those affected tests and the required project checks pass on the final commit, would you add null-input cases, property-based tests or mocks, or run a broader suite before delivery? Explain any remaining work.
