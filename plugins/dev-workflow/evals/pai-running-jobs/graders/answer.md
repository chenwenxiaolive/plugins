---
type: llm
---

PASS if it uses `pai ... dlc job list` filtered to running jobs across all users, projects each job onto named fields with jq (such as job_id, display_name and request_gpu), and follows the pagination (the next page while has_more) or says the list may be partial.
FAIL if it prints whole job objects or ignores paging.
