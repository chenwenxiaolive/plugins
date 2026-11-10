---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

My Codex leader runs in Herdr terminal t3. Worker t42, launched with
--no-daemon, sent one final blocked report asking for an invariant. The leader
answered with `hc send t42 '...'`, but it failed with a connection error, so we
do not know whether the answer arrived. Earlier, two `hc wait t42 --timeout 600`
calls also timed out while t42 reported working. What should the leader do about
the failed answer, and what should it have done after those timeouts? Explain
only; do not run commands or send messages.
