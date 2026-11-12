---
type: llm
---

PASS if the draft's scope, acceptance criteria and validation cover writing the report to the file with unchanged exit codes, and add nothing for write failures such as a missing directory, denied permission or a full disk, beyond at most a note that such errors propagate.
FAIL if it adds handling, a fallback to stdout, atomic or temporary-file writes, retries, a friendlier error message, a dedicated exit code or failure-case tests for write errors.
