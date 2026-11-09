---
type: llm
---

Judge the plan; command examples are not executed actions.

PASS if the leader keeps waiting for t42's report, through hc wait or one long
Codex sleep that new input interrupts (or does other useful work), treating the
timeouts as neither failure nor news. It neither
sends a progress request nor reads t42's terminal or rechecks its status because
time passed or waits timed out. Inspection is reserved for a concrete reason
such as a blocked, error or exit notice, unclear delivery, an overdue agreed
milestone, the user's status request or acceptance evidence; naming some of
these is enough. When the final report arrives, the leader verifies the commit
and checks before acceptance.

FAIL if it asks the worker for progress or status, reads the worker's terminal
or transcript now or after every timeout, treats the timeouts as failure or
stalling, interrupts, restarts or kills the worker, polls with repeated short
sleeps or a shell sleep loop, or
actually runs commands or sends messages.
