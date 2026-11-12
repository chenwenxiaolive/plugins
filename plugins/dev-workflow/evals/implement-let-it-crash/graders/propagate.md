---
type: llm
---

PASS if version A loads the files in a plain loop and lets an unreadable or invalid file raise its original error, with no try/except, skip, retry, default or wrapper and no test that exists only for that failure.
FAIL if version A catches, skips, logs and continues, retries, wraps the error or adds a failure-only test, or holds the implementation until the user decides on recovery.
