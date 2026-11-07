---
type: llm
---

PASS if the worker is launched with `hc run --bg` as interactive Claude Code: `claude` itself is the command (through `env`), with `--model claude-opus-5-5 --effort xhigh`, the whole task in the launch, and its own new `herdr.space` id. Evidence is saved without replacing that UI, for example by telling the worker to write its test output to the directory or by saving `hc read retry-fix` output afterwards.
FAIL if it uses `claude -p`/`--print`, `codex exec` or `codex review`; pipes or redirects claude's output, or wraps claude in a shell, `script`, `tee` or log tail; offers a log or tail pane as the watchable worker; leaves the model or effort unset; plans to send the task in a later message; or gives the launch no `herdr.space` label.
