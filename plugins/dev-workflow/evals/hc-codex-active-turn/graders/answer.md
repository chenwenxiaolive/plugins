---
type: llm
---

PASS if it explains that a codex queue message waits for the owner's current turn to end and does not steer the active turn, so the working status with an unchanged turn means a deferral, not loss or receipt. It does not resend; it waits for that turn to end (for example with hc wait t42) and then expects the ACK, diagnosing only if none arrives after that. Future long checks run as their own hc terminals (started with --outlive-parent so they survive an owner change) while the worker ends its turn, so queued messages can arrive between turns.
FAIL if it resends or repeats the message, treats the queued line as receipt, switches the task route to hc send, adds --resume, uses send_message_to_thread or another server to load the live worker's thread, or kills or restarts the working worker to deliver the message.
