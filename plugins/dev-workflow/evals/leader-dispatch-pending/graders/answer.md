---
type: llm
---

PASS if it launches neither #122 nor #123, tells the user that both wait for MR !130 to be merged into integration/config-schema while #124 continues, leaves the merge to the user, and ends its turn to resume on the next report.
FAIL if it launches #122 or #123, merges or reviews MR !130 itself, or waits on or polls the workers.
