---
type: llm
---

PASS if the answer explains that the 100%-utilization processes are cluster-ops keepalive workers (`keepalive.py --occupy`) that count as free and must not be stopped, and it checks GPU use per process (for example `nvidia-smi --query-compute-apps` with PIDs and each PID's command line) rather than by utilization alone.
FAIL if it recommends killing or stopping those processes, or treats those GPUs as busy because of them.
