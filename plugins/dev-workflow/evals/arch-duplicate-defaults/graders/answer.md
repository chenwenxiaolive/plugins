---
type: llm
---

PASS if the report identifies that app/config.py and app/loader.py each define their own defaults (with different timeouts, 30 and 60) as duplicate sources of truth, citing the files, proposes consolidating them, and says how to validate the change.
FAIL if it misses the duplication or proposes a new framework or layer without a concrete benefit.
