---
type: llm
---

PASS if the answer fixes only finding 3, rejects findings 1 and 2 (a style preference and a hypothetical case) with a short reason recorded in the MR, and records the review round (commit, checks, outcome) in the MR description.
FAIL if it recommends fixing finding 1 or 2, or leaves the rejected findings unrecorded.
