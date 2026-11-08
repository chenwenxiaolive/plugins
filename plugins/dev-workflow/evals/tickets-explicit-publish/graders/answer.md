---
type: llm
---

PASS if it treats the invocation as a request to publish one issue in the plugins repository on GitHub: it checks for an equivalent existing issue first (by searching, or by stating that search as the step before creating), then publishes the issue or, since it cannot write from here, gives the issue and the command it would run, without asking again whether to publish; and the issue covers goal and context, scope, acceptance criteria, validation and dependencies.
FAIL if it skips the duplicate check, stops at a draft and asks whether to publish, leaves out one of those sections, or splits this one change into several issues.
