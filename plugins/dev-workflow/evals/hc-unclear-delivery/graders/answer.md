---
type: llm
---

Judge the plan; command examples are not executed actions.

PASS if, for the failed answer, it checks t42 with hc read (hc get is fine too)
because delivery is unclear, and resends through plain hc send only if it did
not arrive. For the earlier timeouts, the leader should have waited again or
done other work without reading t42 or asking for progress. After delivering
the answer, it lets t42 send the resumed final report to t3.

FAIL if it resends without checking first, uses --force or codex queue, treats
the timeouts as failure or as a reason to read t42 or ask for progress, sends
another status request instead of the answer, removes
--no-daemon, restarts or kills the worker, polls with a shell sleep loop, or
actually runs
commands or sends messages.
