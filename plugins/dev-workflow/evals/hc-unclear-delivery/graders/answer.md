---
type: llm
---

Judge the plan; command examples are not executed actions.

PASS if, for the failed send, it inspects t42 with hc read (hc get is fine too),
giving unclear delivery as the reason, and resends the invariant through hc send,
without --force, only if it did not arrive. The earlier timeouts
needed no terminal read or progress prompt: the leader just waits again with hc
wait or does other work. Afterwards it returns to waiting for t42's report
rather than repeating unchanged checks.

FAIL if it resends blindly without reading first, uses --force or codex queue,
treats the timeouts as failure or as a reason to read t42 or ask for progress,
removes --no-daemon, restarts the worker, polls with sleep, or actually runs
commands or sends messages.
