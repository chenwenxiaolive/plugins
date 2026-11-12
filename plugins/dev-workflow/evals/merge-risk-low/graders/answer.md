---
type: llm
---

The run has no shell, so judge the plan.
PASS if it rates the risk low, records the rating and the dimensions behind it in the MR description, and plans to merge the MR itself with the reviewed SHA as a guard, without waiting for the user to ask, then to set the execution record to merged and report the merge.
FAIL if it waits for the user, merges without the SHA guard, scores the risk on a numeric scale, or skips the execution record.
