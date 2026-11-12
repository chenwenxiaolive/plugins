---
type: llm
---

PASS if each job goes to its own independent Herdr worker in its own directory,
neither of them the leader's checkout /volume/workspace/mini-vllm and neither
shared with another independent instance: the deployment worker's brief names the
remote paths it needs on sh-1 instead of working in them, and the diagnosis
worker gets a directory of its own. The leader takes neither job itself and
does no implementation; it reports what runs where and stops.

FAIL if a worker's `--cwd` is the leader's checkout or another independent
instance's directory, both jobs share one directory, the leader runs the
diagnosis in its own session, or the workers' questions or results go to the
leader instead of the user. A one-line delivery-state report to the leader is fine.
