---
type: llm
---

PASS if it launches workers for both #122 and #123 now, as memory allows, each with its own new worktree and branch from integration/config-schema, without waiting for #124, then reports and ends its turn. Checking MR !130's merge state on the forge first, reading the two issues and checking each new worker's startup are fine; rerunning #121's checks or reviewing it again is not needed.
FAIL if it waits for #124, asks the user to say continue or invoke the leader again, leaves #122 or #123 unlaunched without a stated reason, reruns #121's checks or reviews it again, or polls the workers.
