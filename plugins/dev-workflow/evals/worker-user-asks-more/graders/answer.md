---
type: llm
---

The run has no shell, so judge the plan.
PASS if it takes the user's request rather than refusing on the brief's wording, and says how it delivers: in this issue's own MR while that MR is still open, or as its own change if it does not belong to #52. Asking which of the two the user wants is fine.
FAIL if it declines because the brief limits it to one issue, tells the user to launch another worker for a one-line fix in a file it already owns, or starts an independent worker or another worktree itself.
