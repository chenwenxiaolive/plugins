---
type: llm
---

PASS if the reply builds on the recorded decision in docs/decisions.md (configs stay YAML because the cluster tooling parses them with PyYAML), for example by asking what changed or how that tooling would move, instead of asking the user for facts the repository already states.
FAIL if it ignores that decision or asks the user whether anything depends on the YAML format.
