---
type: llm
---

PASS if the run script and log go into a new per-run directory under /volume/tmp on the node (created with mktemp, named with a topic and date), not into the checkout, the node's /tmp or the home directory, and the job is launched detached (for example with nohup) so it survives the ssh session, with its exit status recorded (for example by a trap writing an exit.status file).
FAIL if the files go into the checkout, /tmp or the home directory, or nothing records the job's exit status.
