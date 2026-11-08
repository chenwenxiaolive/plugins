---
type: llm
---

PASS if all of these hold:
- It writes one issue for the plugins repository on GitHub with goal and context, scope, acceptance criteria, validation and dependencies.
- It publishes the issue after checking for an equivalent existing one or, lacking forge access here, says nothing was filed and that with access it would check for an existing issue and then create it. Asking for that access, or giving the user a command to file it themselves, is fine.
- It does not ask whether the user wants the issue published, and it does not claim the issue or start implementing it.
FAIL otherwise.
