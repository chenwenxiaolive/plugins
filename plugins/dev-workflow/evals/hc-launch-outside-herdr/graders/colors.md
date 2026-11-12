---
type: llm
---

PASS if the launch command sets `TERM=xterm-256color` and `COLORTERM=truecolor` in the `env` prefix before `codex`, beside `PATH="$PATH"`.
FAIL if the worker is left with this session's `TERM=dumb`, either variable is missing, or the command copies the whole environment.
