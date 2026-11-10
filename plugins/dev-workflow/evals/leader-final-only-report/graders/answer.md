---
type: llm
---

PASS if the sequence is one launch containing the complete task, then one final
report from the worker. There is no ready, progress, milestone, idle or
acknowledgement message. The leader does other work or ends its turn while the
worker runs. A blocked report or one late correctness fact is the only extra
message, after which the worker continues and still sends the final report.

FAIL if the plan adds a readiness handshake, periodic checks, notify_when_idle,
acknowledgements or a request for progress, or treats status changes as
completion.
