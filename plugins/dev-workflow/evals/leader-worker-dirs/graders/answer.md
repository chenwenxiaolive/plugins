---
type: llm
---

PASS if the deployment goes to a herdr worker whose `--cwd` is a directory where no other agent runs (such as a free worktree slot, not the leader's checkout /volume/workspace/mini-vllm), with the remote paths it needs named in its brief, and the diagnosis goes to a subagent (the Agent tool) or the leader itself rather than to a herdr worker.
FAIL if a worker's `--cwd` is the leader's checkout or another agent's directory, or the diagnosis gets a herdr worker of its own.
