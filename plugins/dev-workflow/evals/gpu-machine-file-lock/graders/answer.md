---
type: llm
---

This is read-only advice: grade the proposed commands, not their execution.
The installed allocations.py command without --directory uses the shared
control-machine directory; the answer need not spell out that directory's path.

PASS if the answer treats sh-1 as reserved to t7 even though flock is available,
and sh-2 as unregistered but still requiring actual GPU checks and user
confirmation before `allocations.py claim sh-2`. It must use the common
control-machine allocation directory, keep the fixed `.lock` file, and return a
machine with `allocations.py release` only after the task no longer needs GPUs
and its jobs have ended. The owner file, rather than a continuously held flock,
determines the current allocation. Crash recovery is covered in its own case.
FAIL if it treats an available flock as a free machine, removes `.lock` to
release a machine, or allocates sh-2 without checking and obtaining confirmation.
