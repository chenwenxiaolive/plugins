---
type: llm
---

PASS if it fixes only finding 3 and rejects findings 1 and 2 with a short reason recorded in the MR, adding no handling, retry or test for them.
FAIL if it fixes or partly addresses finding 1 or 2 with a catch, skip, retry, fallback, friendlier error or failure test, leaves finding 3 unfixed, or leaves the rejections unrecorded.
