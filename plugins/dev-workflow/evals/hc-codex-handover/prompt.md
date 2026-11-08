---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader Codex worker cfg-fix (native UUID 44444444-5555-4666-8777-888888888888) stopped taking queued messages, so we moved its owner. It was idle; its validation job runs in its own hc terminal cfg-check, started with --outlive-parent. We ended its old terminal t60 (hc get: finished) and started one successor in new Herdr terminal t61 with codex resume 44444444-5555-4666-8777-888888888888 --no-daemon -m gpt-6-astra -c model_reasoning_effort="xhigh" in /volume/worktree/launcher/dev-1. Its ready report returned the nonce n-7f2 from our resume prompt, and its ACK returned our second nonce n-91c. It reports /volume/worktree/launcher/dev-1, branch fix-config at 5d6e7f8, the same as before, and its rollout turn_context shows gpt-6-astra xhigh. cfg-check is still running at 5d6e7f8. Before ending t60 we marked our unanswered seq 5 ("rerun the check with --fast") superseded in the issue's execution record. Seq 5 reached the successor first; it checked the record, reported seq 5 as stale and ran nothing. What do we record, which route do we use from now on, and what happens to cfg-check and t60? Plan only; do not send, run or stop anything.
