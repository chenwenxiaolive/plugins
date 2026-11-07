---
type: llm
---

PASS if it uses codex queue --thread with the verified native UUID for task text and the same route back to the leader's UUID for reports, keeping native IDs separate from t42. It retains --no-daemon for Herdr process ownership and does not add --resume for the already live external worker. Queue exit zero proves only queuing; notLoaded and an immediate wait on the other app-server do not prove that this worker exited or completed. It waits for the actual native report and verifies commit/check evidence, using hc get/wait for the owning terminal's lifecycle or hc read for diagnostics when needed.
FAIL if it substitutes t42 for the UUID, uses hc send as the ordinary route between the Codex sessions, resumes a second copy because of notLoaded, removes --no-daemon to enable messaging, treats exit zero as completion, or claims the other server's wait result establishes worker liveness.
