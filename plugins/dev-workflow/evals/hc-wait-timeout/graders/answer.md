---
type: llm
---

PASS if it waits for the program with `hc wait bench-1` rather than sleep or a polling loop, treats a timeout as only the end of that wait, not a failure, and waits again, and checks its exit status and output using `hc read`. Native agent messaging does not apply to this plain program.
FAIL if it polls with sleep, or calls a timeout a failure.
