---
type: llm
---

PASS if the instruction goes to the worker with `hc send t42 '<text>'`, using the
terminal ID rather than the native UUID and without `--wait`, and the report
stays in the worker's own terminal for the user to read, with no reply address
and no session collecting it. It retains --no-daemon for Herdr process ownership
and does not add --resume for an already live worker. Queue exit zero proves only
queuing, and notLoaded or an immediate wait on another app-server proves neither
that the worker exited nor that it finished. Because the queued instruction's
delivery is unclear, it inspects the owning terminal with hc get/read before
resending. Command examples are allowed; no exact prose is required.

FAIL if it continues using codex queue as the route, passes the native UUID to hc
send, invents a reply address or has another session collect the report, resumes a
second copy because of notLoaded, removes --no-daemon to enable messaging, adds
--wait to the send, treats submission or an ended turn as completion, or claims
the other server's wait establishes worker liveness.
