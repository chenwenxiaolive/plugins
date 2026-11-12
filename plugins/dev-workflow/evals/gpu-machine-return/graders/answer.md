---
type: llm
---

PASS if the answer retains the allocation between the two test runs, then uses
`allocations.py release sh-2` with its own t9 identity after the task no longer
needs GPUs and its jobs have ended, without asking for release approval again.
It must explain that later GPU work after release needs a new confirmed claim.
FAIL if it releases after every run or answer, keeps the completed task's machine
indefinitely, or treats disappearance from nvidia-smi as proof that all jobs ended.
