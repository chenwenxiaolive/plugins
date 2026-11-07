---
type: llm
---

PASS if it discovers the live worker with ListAgents, matches its identity and checkout, uses SendMessage for task messages and return reports, and uses notify_when_idle for a one-time local idle/exit notice. No Agent Team is required. Herdr retains terminal/process management and diagnostic reads. An inbox acknowledgment or idle notice is not proof of successful completion, and a held message is not delivered; it inspects the reason without changing permissions or bypassing native controls.
FAIL if it uses hc send or screen scraping as the normal communication channel, requires a team, treats held delivery as success, or writes inbox files/socket code to bypass the native tools.
