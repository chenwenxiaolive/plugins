---
type: llm
---

PASS if the deployment goes to a Herdr worker whose `--cwd` is a directory where no other independent instance runs (such as a free worktree slot, not the leader's checkout /volume/workspace/mini-vllm), with the remote paths it needs named in its brief, and the diagnosis goes to a native subagent or the leader itself rather than to a Herdr worker. A diagnosis subagent stays in the leader's checkout.
FAIL if a Herdr worker's `--cwd` is the leader's checkout or another independent instance's directory, or the diagnosis gets a Herdr worker of its own.
