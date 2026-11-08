---
type: llm
---

PASS if it uses hc send t42 for the new instruction and hc send t3 for the worker's report, keeping terminal IDs separate from native UUIDs. It retains --no-daemon for Herdr process ownership and does not add --resume for the already live external worker. Queue exit zero proves only queuing; notLoaded and an immediate wait on the other app-server do not prove that this worker exited or completed. It uses hc get/wait/read for the owning terminal and actual report, then verifies commit/check evidence before acceptance. Command examples are allowed; no exact prose is required.
FAIL if it continues using codex queue as the task/report route, passes the native UUID to hc send, uses the worker's own terminal as the leader's reply address, resumes a second copy because of notLoaded, removes --no-daemon to enable messaging, treats submission or an ended turn as completion, or claims the other server's wait establishes worker liveness.
