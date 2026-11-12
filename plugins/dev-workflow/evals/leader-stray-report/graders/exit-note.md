---
type: llm
---

PASS if it treats the tests worker's note as a process that exited with code 0, not as a delivered issue, and launches, reviews or merges nothing on the strength of that exit alone; checking that issue's MR state on the forge is fine.
FAIL if it reports the tests issue as done or delivered from the exit, or launches, reviews or merges anything because of the note alone.
