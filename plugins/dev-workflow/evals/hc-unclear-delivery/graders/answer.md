---
type: llm
---

Judge the plan; command examples are not executed actions.

PASS if, for the failed send, it checks t42 with hc read (hc get is fine too)
because delivery is unclear, and resends the invariant through plain hc send
only if it did not arrive. For the earlier timeouts, the leader should simply
have waited again, with hc wait or one long Codex sleep that new input
interrupts, or done other work, without reading t42 or asking for progress.

FAIL if it resends without checking first, uses --force or codex queue, treats
the timeouts as failure or as a reason to read t42 or ask for progress, removes
--no-daemon, restarts or kills the worker, polls with repeated short sleeps or a
shell sleep loop, or actually runs
commands or sends messages.
