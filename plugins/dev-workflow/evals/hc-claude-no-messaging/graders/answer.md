---
type: llm
---

PASS if it keeps this session out of the worker's loop: native cross-session
messaging, idle subscriptions and an Agent Team are not how this workflow runs,
and no team is required for anything. The invariant reaches the worker from the
user, typed in the worker's terminal in its Herdr space (or, if the user asks for
it to be sent, with `hc send <worker-terminal>` as plain text, no `--wait`). The
worker reports its result in that same terminal, where the user reads it, so this
session does not wait for it, subscribe to its idle state or collect and verify
its MR. Noting that an idle notice or a self-reported result is a claim rather
than proof of completion is fine.

FAIL if it sets up SendMessage or ListAgents as the ongoing route to the worker,
requires or recommends notify_when_idle or an Agent Team for this, has this
session wait for or collect the worker's result, treats an idle notice as
completion, reads the worker's terminal on a schedule, or writes inbox files or
socket code to reach the worker.
