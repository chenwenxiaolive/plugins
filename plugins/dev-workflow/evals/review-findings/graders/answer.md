---
type: llm
---

PASS if the answer fixes only finding 3 and rejects findings 1, 2 and 4 (a style preference, a hypothetical case and redundant checks/tests for an excluded internal state) with a short reason recorded in the MR. It preserves validation at the config loader's boundary.
FAIL if it recommends fixing finding 1, 2 or 4 as part of the review, removes boundary validation, or leaves the rejected findings unrecorded.
