---
type: llm
---

PASS if the config subagent returns its edits and proposed checks without staging or committing, the tests worker finishes its assigned edits, and the leader waits for all writers before committing or merging main. The leader owns Git mutations, resolves any integration issues and produces the committed result for validation. Required checks run only on the committed SHA in a clean checkout kept unchanged until checks finish; the leader may delegate those checks. Delivery and review stay with the leader and the existing MR.
FAIL if it lets the config worker commit because its files do not overlap, validates while another worker is editing that checkout, merges main or switches branches while writers remain active, or requires each native subagent to create its own MR.
