---
name: to-tickets
description: "Turn the current discussion or a supplied plan into actionable GitLab issues for independent coders in reusable worktrees."
disable-model-invocation: true
---

# To Tickets

Write issues a fresh coder can implement without the planning conversation, in the
selected checkout's GitLab project ([gitlab.md](../gpu-cluster/gitlab.md)).
Running this skill authorizes publishing them, unless the user asked for drafts.

- Make each issue one independently verifiable result for one branch and MR. Split by behavior or a concrete technical result, not by layer. Give performance work its workload, baseline, metric and threshold, leaving unknown targets open.
- Ask only about missing decisions that change scope, acceptance or dependencies.
- Check for equivalent issues first. Create prerequisites first and link them from dependent issues, using native blocking links when available. Use existing labels only.
- Issues get no worktree assignment; the user assigns coders.
- After an interrupted or timed-out publish, check what was created before retrying.

Follow the project's template, or:

```markdown
## Goal and context
## Scope
## Acceptance criteria
## Validation
(checks or benchmark method, including remote/GPU needs)
## Dependencies
```

Return the issue links, their dependencies and which are ready to start.
