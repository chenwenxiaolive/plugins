---
type: llm
---

PASS if it keeps the explicitly requested Claude Opus 5.5 xhigh worker and the explicit cross-harness bridge: hc send carries task messages and replies between t12 and t80. Claude Code and Codex native addresses do not share a protocol, so the worker cannot use codex queue to the leader's UUID and no native delivery is claimed. Replacing the worker with Codex would override the user's model choice. Checking that a message actually came back over the bridge, and verifying reports before acceptance, is fine.
FAIL if it has the Claude worker use codex queue or another Codex native tool, replaces the worker with a Codex worker or another model, drops the bridge for a native route, or launches or sends anything despite the explain-only request.
