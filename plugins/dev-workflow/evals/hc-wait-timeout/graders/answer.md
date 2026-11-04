---
type: llm
---

PASS if it waits with `hc wait bench-1` (not sleep or a polling loop), treats a timeout as a check-in rather than a failure, and reads the worker's actual answer with `hc read` instead of trusting its one-line report.
FAIL if it polls with sleep, or calls a timeout a failure.
