---
type: llm
---

PASS if the brief tells the worker to report in its own terminal, put long
evidence in a file and report its path. The leader uses hc send t42 for
follow-ups and hc wait/read to collect the worker's questions/results, checking
actual content and evidence rather than accepting an ended turn as completion.
It requires no new leader terminal and retains --no-daemon. Example commands
are allowed; exact prose is not required.

FAIL if the worker sends its report to t42 as though that were the leader,
passes CODEX_THREAD_ID to hc send, falls back to codex queue, uses hc wait
--output to await the agent report, or requires moving the leader into Herdr.
