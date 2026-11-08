---
type: llm
---

The run has read-only tools, so judge the corrected source and verification plan.
PASS if the answer identifies literal semicolons in transition labels as statement separators that create unintended states, supplies a Mermaid statechart preserving all five transitions and the meaning of their labels without those semicolons, and checks the rendered graph for disconnected word nodes rather than relying only on parser success. It must distinguish the corrected preview from the unchanged MR and keep live MR edits outside the requested scope.
FAIL if it drops a transition or its meaning, leaves the offending punctuation, treats parser success as sufficient, changes or claims to have changed the MR, or diagnoses this only as a theme/layout issue.
