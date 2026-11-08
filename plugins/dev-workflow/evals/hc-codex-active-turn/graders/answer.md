---
type: llm
---

PASS if the worker sends its report with plain hc send t3 while the leader is
working, retaining --no-daemon. It explains that Enter steers the current turn,
so the leader can process the report at a model/tool boundary without ending the
turn. It reads the actual result and verifies task evidence before acceptance.
Command examples are allowed; exact wording is not required.

FAIL if it uses codex queue for the reply, waits for the leader to become idle
before sending, adds --wait to the worker's report send, changes to a shared
daemon as the fix, promises instantaneous processing during a blocking tool, or
treats submission or idle status as proof of completion.
