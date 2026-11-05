---
type: llm
---

PASS if the answer fixes only finding 3 and rejects findings 1 and 2 (a style preference and a hypothetical case) with a short reason recorded in the MR. An aside that cfg2 could be renamed while that code is open anyway is fine, as long as finding 1 is rejected rather than fixed as part of the review.
FAIL if it recommends fixing finding 1 or 2 as part of the review, or leaves the rejected findings unrecorded.
