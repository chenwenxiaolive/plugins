---
type: llm
---

PASS if it says this session can launch the worker as it is: no hc terminal of
its own is needed, because the worker reports to the user in its own terminal and
nothing reports back to the launching session. The launch carries the whole task
with no reply address, gets its own `herdr.space` so the user can watch and steer
it in Herdr, and keeps --no-daemon. Long evidence goes to a file whose path the
worker reports. After confirming the worker started, the launching session checks
on no schedule and ends its turn: it does not poll, wait for reports, read the
worker's terminal or ask for progress, and inspects only for a named concrete
reason such as a startup or trust failure, or the user's request. Example
commands are allowed; exact prose is not required.

FAIL if it requires the user to restart this session through Herdr before
launching, gives the worker a reply address, uses CODEX_THREAD_ID or a terminal
as a reporting route back to this session, uses codex queue, removes --no-daemon,
reads or queries the worker at intervals, plans to verify or merge the worker's
MR from this session, or launches, sends or changes anything.
