---
name: to-tickets
description: "Turns the current discussion or a supplied plan into GitLab or GitHub issues that independent coders can implement without the conversation. Use when the user asks to create, file, raise or draft issues or tickets, whether or not they name this skill; not for design discussion or questions about existing issues."
---

# To Tickets

Write issues a fresh coder can implement without the planning conversation, in the
project the user names, else the selected checkout's: GitLab
([gitlab.md](../gpu-cluster/gitlab.md)), or GitHub with `gh`.

- The user's request decides publication, not this skill being loaded. A request to create, file or raise issues, or the user invoking this skill, authorizes publishing the issues it covers; a request for drafts gets drafts and no forge write. A design discussion, a question about existing issues or a mention that something could become an issue authorizes neither: answer, and offer the issue if it helps.
- Make each issue one independently verifiable result for one branch and MR. Split by behavior or a concrete technical result, not by layer: include any needed docs and test changes in the issue they support ([implement](../implement/SKILL.md#implement-and-validate)).
- Ask only about missing decisions that change scope, acceptance or dependencies.
- Check for equivalent issues first. Link dependent issues to their prerequisites with native blocking links when available. Use existing labels only.
- After an interrupted or timed-out publish, check what was created before retrying.

Give every issue, drafts and any you could not publish included, the project's
template or these sections:

```markdown
## Goal and context
## Scope
## Acceptance criteria
## Validation
(checks or benchmark method, including remote/GPU needs)
## Dependencies
```

Return the issue links or drafts, their dependencies and which are ready to start.
