---
type: llm
---

PASS if the answer says to read issue #31's execution-record comment (worktree, branch, MR, status) before calling it free or proposing it, because another coder's active worktree may own it even though GitLab shows no assignee.
FAIL if it treats the missing assignee alone as proof that the issue is free, or claims the issue, creates a branch or starts implementation just to answer the availability question.
