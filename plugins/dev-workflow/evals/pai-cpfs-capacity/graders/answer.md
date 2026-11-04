---
type: llm
---

PASS if the plan reads live capacity and directory entries with read-only commands (`df`, `ls`) inside an existing running DLC job or DSW instance through `pai ... exec`, and does not create, restart or stop a task to do it.
FAIL if it plans to start a new job or instance for browsing, or claims the file-system or fileset APIs alone can show directory contents.
