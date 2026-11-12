---
type: llm
---

PASS if version B skips a manifest with invalid JSON, prints its file name on stderr, loads the rest and adds a test for that behavior.
FAIL if a malformed manifest still stops version B, or version B has no test for the skip.
