---
type: llm
---

PASS if the launch uses hc run --bg with the requested cwd, a name and its own herdr.space label, and the check's stdout/stderr reach both the terminal and the specified log. The command's failure must propagate through any pipeline, for example with bash pipefail and `2>&1 | tee ...`, or explicit handling of PIPESTATUS. No actual execution is allowed.
FAIL if all output goes only to a file, the log is missing stderr, the command runs outside hc, or tee masks the check's failure.
