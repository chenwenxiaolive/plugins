---
type: llm
---

PASS if the MR description itself contains a Mermaid state diagram of the job lifecycle in plain words that marks what changed (the requeue after a node failure, at most twice, and cancelling a queued job) apart from the unchanged transitions, and also gives the issue link and the validation at 4f2c9e1.
FAIL if the behavior change appears only as prose or bullets, the chart is kept out of the MR description (only in chat or on a separate page), or it contradicts the described behavior.
