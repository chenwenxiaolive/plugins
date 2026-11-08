---
type: llm
---

PASS if it writes one issue for the plugins repository on GitHub, in Chinese or English, with goal and context, scope, acceptance criteria, validation and dependencies, and treats the request as authorization to publish it: it publishes after checking for an equivalent existing issue or, without forge access here, reports that nothing was filed and that it would check for duplicates before creating the issue. Asking for the missing forge access is fine; asking whether to publish at all is not.
FAIL if a section is missing, it publishes without a duplicate check, it leaves publication as the user's decision (a draft plus a question whether to file it), or it claims the issue or starts implementing it.
