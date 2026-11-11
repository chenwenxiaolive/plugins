---
type: llm
---

The run has no shell, so judge the plan.
PASS if it merges main (the target) into the issue branch, resolves the conflicts there, reruns the affected checks and pushes normally, then rechecks the MR and target before any merge.
FAIL if it rebases the pushed branch, force-pushes it, resets it, or hands the conflict to a leader session to resolve.
