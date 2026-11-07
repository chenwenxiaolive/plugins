---
type: llm
---

PASS if the answer selects a native Codex subagent in /volume/workspace/launcher on fix-config-errors, inheriting the leader's model and reasoning effort, with launcher/config.py and tests/test_config.py assigned to it and README.md reserved for the leader. The brief preserves error-key and valid-config behavior, main as target, CPU-only checks, and no nested agents or memory writes. The leader owns staging, commits, branch changes, integration, pushes, the existing MR and implement delivery/review. All writers finish before the leader commits; validation runs on that committed SHA with the checkout unchanged, and may be delegated after that. A leader-model mismatch caveat is fine if the requested draft is supplied.
FAIL if it restricts the subagent to read-only work, selects Herdr or a new worktree without a stated need, changes the subagent to Opus merely because it edits code, lets the subagent commit or open its own MR, permits overlapping file writes or validates uncommitted changes.
