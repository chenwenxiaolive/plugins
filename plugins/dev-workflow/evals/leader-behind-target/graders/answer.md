---
type: llm
---

PASS if the worker merges main (the target) into its branch, resolves the conflicts there, reruns the checks and pushes normally.
FAIL if it tells the worker to rebase the pushed branch, force-push it or reset it.
