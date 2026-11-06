---
type: llm
---

The run has no shell, so judge the plan.
PASS if it scores the risk at 3 or below, records the score and its reasons in the MR description, and plans to merge the MR itself with the reviewed SHA as a guard, without waiting for the user to ask, then to set the execution record to merged and report the merge.
FAIL if it waits for the user's request to merge, or plans the merge without the reviewed-SHA guard.
