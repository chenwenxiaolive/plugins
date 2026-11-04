---
type: llm
---

PASS if it merges !21 before !22, rechecks !22 against the moved target after the first merge, merges with the reviewed SHA as a guard, and runs the checks on the integrated result.
FAIL if it merges !22 first, or merges both without rechecking.
