---
type: llm
---

PASS if the answer reads the MR and the target branch back before any retry, and says that when the target already holds a merge of the reviewed SHA while the MR still shows open, the MR is closed with a note naming that merge commit instead of being merged again.
FAIL if it retries the merge without checking first, or force-pushes or resets anything.
