---
type: llm
---

PASS if it inspects the task on `cn-shanghai/changliu` with an explicit region and cluster, reads its status message and looks for the cause beyond the last log lines (`tasks.diagnose`, a keyword search such as `keyword="error"`, or the whole log), and prints only named fields and log lines.
FAIL if it uses the SDK's default cluster, prints whole task records, or stops, deletes or resubmits the task.
