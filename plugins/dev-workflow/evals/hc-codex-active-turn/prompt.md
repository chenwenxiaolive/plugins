---
tags: [herdr-core, leader]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Codex leader (native UUID 0a0a0a0a-1111-4222-8333-444444444444) sent a follow-up to its Codex worker sink-fix twelve minutes ago with codex queue, which printed "Queued message 01a1c0de-0000-7000-8000-000000000001 for thread 11111111-2222-4333-8444-555555555555." The worker was launched through hc with --no-daemon in Herdr terminal t42, and its route passed the nonce check at launch. hc get t42 reports live, status working, turn 6, the same turn as at the send; the worker is running a 40-minute validation in the foreground of that turn. No ACK yet. Should we resend, switch to hc send, add --resume, or have the leader's thread tools message the worker? How should workers run long checks in future? Explain only; do not send anything or run commands.
