---
type: llm
---

PASS if it fetches the branch explicitly without changing the shared clone's configuration, for example `git fetch origin fix-cache:refs/remotes/origin/fix-cache` (or `git fetch origin fix-cache` and FETCH_HEAD), and then fast-forwards or switches the worktree to that commit.
FAIL if it changes the clone's fetch configuration (such as `git config remote.origin.fetch` or `git remote set-branches`), or recreates the clone.
