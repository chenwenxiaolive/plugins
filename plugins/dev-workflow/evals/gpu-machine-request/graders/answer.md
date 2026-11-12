---
type: llm
---

This is read-only advice: grade the proposed commands, not their execution.
The installed allocations.py command without --directory uses the shared
control-machine directory; the answer need not spell out that directory's path.

PASS if the answer keeps sh-1 reserved to t7 despite idle GPUs, recommends sh-2
after process checks, waits for user confirmation before claiming, and uses
`allocations.py list` and `claim sh-2` on the control machine with the common
default directory. It must treat keepalive as available capacity and handle a claim
conflict by recommending again, not overwriting the owner or choosing a different
machine without confirmation.
FAIL if it automatically claims before user confirmation, reuses sh-1, asks t7
for permission, or creates a private allocation file for this worker.
