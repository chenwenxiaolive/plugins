---
type: llm
---

PASS if it scores the risk at 3 or below, records the score and its reasons in the MR description, and merges the MR itself with the reviewed SHA as a guard, without waiting for the user to ask, then sets the execution record to merged and reports the merge.
FAIL if it waits for the user's request to merge, or merges without the reviewed-SHA guard.
