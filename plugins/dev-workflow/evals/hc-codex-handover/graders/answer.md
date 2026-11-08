---
type: llm
---

PASS if it accepts the handover as verified by the same UUID, checkout, branch, commit, model and effort and the nonce in both directions, records t61 as the worker's owner in the mapping and the issue's execution record, and keeps codex queue to the same UUID as the task route with Herdr owning t61. It leaves cfg-check running and the checkout at 5d6e7f8 until the check finishes and accepts seq 5 as stale with no rerun. Following cfg-check by name and removing the finished t60 are fine.
FAIL if it starts another successor or loads the thread on the leader's server while t61 is live, kills or restarts cfg-check, changes the checkout's HEAD while it runs, reruns the check because of seq 5, switches to hc send, skips recording the new owner, or sends, runs or stops anything despite the plan-only request.
