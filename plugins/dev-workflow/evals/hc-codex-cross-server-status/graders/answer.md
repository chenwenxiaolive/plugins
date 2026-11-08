---
type: llm
---

PASS if it says the desktop app-server's notLoaded, interrupted and immediate-wait results describe saved history on a server that does not own the thread, not the worker's state; the owning terminal t42 is live and working, so the worker is neither interrupted nor finished by that evidence. It rejects send_message_to_thread (and --resume or codex resume) while t42 is live because that would load a second live writer, keeps codex queue as the task route with hc get/wait on t42 for the owner's lifecycle, and allows another server to take the thread only after t42 has been ended.
FAIL if it treats notLoaded or interrupted as proof the worker stopped, calls send_message_to_thread or resumes the thread while t42 is live, restarts or kills the working worker on that evidence, or uses hc send as the task route.
