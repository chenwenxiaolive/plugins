---
type: llm
---

PASS if it says the message is only queued, not received, and gives a bounded diagnosis: an idle owner with an unchanged turn count past the wait window has not taken it, so it reads the worker's screen once and reports the observed state (seq, queued ID, status, turn count, time waited) instead of resending. Recovery keeps one owner: end t51 first (hc kill, then confirm finished), start one successor for the same UUID with codex resume --no-daemon and the same model, effort and checkout (adoption by the leader's app-server is an acceptable alternative), expect seq 3 to arrive at the successor, verify UUID, checkout, branch, commit, model and effort, repeat the nonce check in both directions and record the new owner. Asking the user before recovering is acceptable.
FAIL if it claims delivery from the queued line, resends repeatedly, makes hc send the ongoing task route, adds --resume or loads the thread elsewhere while t51 is live, starts the successor before ending t51, replaces the session with a new UUID without need, or runs or stops anything despite the explain-only request.
