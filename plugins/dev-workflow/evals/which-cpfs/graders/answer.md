---
type: llm
---

PASS if the answer treats zg's `/volume` and the CPFS that PAI jobs mount at `/cpfs01` as two different file systems: it asks which one is meant or plans each separately.
FAIL if it treats them as one, for example by reading zg's `/volume` to report on PAI's CPFS or taking PAI's file-system figures as zg's usage, or if it plans for only one of them without noting the other exists.
