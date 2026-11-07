# Issue ownership and execution record

An implemented issue carries one editable comment that says who works on it:

```markdown
<!-- coder-execution-record -->
### Execution record

| Field | Value |
|---|---|
| Worktree | <absolute checkout path, or Released (last used: <path>)> |
| Branch | <development branch> |
| MR | <MR URL, or Not opened> |
| Status | active / blocked / needs-human / ready-for-merge / merged / paused, with context |
| Updated | <UTC timestamp> |
```

- Another active worktree owns the issue until it is released or the user reassigns it.
- Create or edit it with `glab api` (or `gh`) when you claim the task, open the MR, get blocked, reach `ready-for-merge` or `merged`, or release the worktree. Keep one record per issue and never overwrite another coder's.
