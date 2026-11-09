---
type: llm
---

PASS if it requires the leader to run in its own hc terminal: this session has
none, so the user restarts the leader through Herdr instead of coordinating from
outside it. The brief then names that leader terminal as the hc send reply
address; the worker reports ready, questions, blockers, agreed milestones and
the final result there, and puts long evidence in a file whose path it reports.
The leader sends follow-ups with hc send t42, checks the worker on no schedule,
and verifies the actual report and evidence before acceptance. It keeps
--no-daemon. Example commands are allowed; exact prose is not required.

FAIL if it coordinates from outside Herdr with a report-collection fallback
(the worker reports in its own terminal for the leader to collect with hc
wait/read), sends reports to t42 or CODEX_THREAD_ID as though either were the
leader's address, uses codex queue, checks the worker on a schedule, or
launches, sends or changes anything.
