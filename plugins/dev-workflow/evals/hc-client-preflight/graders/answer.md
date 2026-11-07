---
type: llm
---

PASS if it checks hc and the selected Claude Code client, treats missing Codex as irrelevant to launching this worker, and gives the normal interactive hc launch with PATH, a unique Herdr space and the requested task. The worker uses Claude Opus 5.5 at xhigh under the existing default. Checking Codex later when review actually needs it is acceptable.
FAIL if it requires installing or authenticating Codex before launching the Claude Code worker, skips checking the required client, or replaces the interactive worker with a print-mode command.
