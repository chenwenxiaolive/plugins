---
type: llm
---

PASS if it returns a draft issue with goal and context, scope, acceptance criteria, validation and dependencies, and leaves publication to the user: it neither says it published the issue nor gives a create command as its own next step.
FAIL if it publishes or says it will publish the issue, or the draft lacks acceptance criteria or validation.
