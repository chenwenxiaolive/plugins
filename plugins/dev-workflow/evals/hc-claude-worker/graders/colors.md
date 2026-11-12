---
type: llm
---

PASS if the `env` prefix before `claude` sets `TERM=xterm-256color` and `COLORTERM=truecolor` beside `PATH="$PATH"` and `IS_SANDBOX=1`.
FAIL if either display variable is missing.
