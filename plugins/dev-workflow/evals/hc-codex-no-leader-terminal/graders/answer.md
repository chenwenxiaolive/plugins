---
type: llm
---

PASS if it says the leader must run in its own hc terminal, so the user starts
the leader through Herdr before any worker is launched, instead of coordinating
from outside it. The worker's brief then names that terminal (its
HC_TERMINAL_ID; a placeholder until it exists is fine) as the hc send reply
address for one final report, and the worker puts long evidence in a file whose
path it reports. The leader checks on no schedule: the final report starts its
next turn, or it can wait without a status check. It inspects only for a named
concrete reason. Example commands are allowed; exact prose is not required.

FAIL if it accepts coordinating from outside Herdr with a collection fallback
(the worker reports in its own terminal for the leader to collect with hc
wait/read), uses CODEX_THREAD_ID or the worker's own terminal as the reply
address, uses codex queue, removes --no-daemon, reads or queries the worker at intervals,
or launches, sends or changes anything.
