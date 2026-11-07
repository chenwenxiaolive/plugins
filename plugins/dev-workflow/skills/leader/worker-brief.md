# Worker brief

Use this for each implementation worker. Fill it with facts checked by the
leader, marking anything still unknown. Keep the real project, model, hardware
and purpose accurate; do not disguise them or omit facts needed for correctness.

```text
Role: implementation worker, Claude Opus 5.5, xhigh. The GPT-6-Astra leader owns coordination and integration.
Goal: <one observable change and why it is needed>.
Done when: <behavioral acceptance criteria and independent expected results>.
Checkout: /volume/worktree/<repo>/dev-N on branch <branch>, based on and merging into <target>; issue <link> (or none).
Owned files: <existing files and exact new paths; no overlap with other workers>.
First reads: <file plus symbol or section for the implementation, direct caller and relevant test>.
Required facts: <interfaces, invariants, compatibility requirements and concise supporting evidence; name unknowns>.
Validation: <checks on committed code and their expected results>.
Execution: <authorized CPU location; or the user-named node and GPU allocation, plus any authorized remote-worktree setup>. No GPU work unless allocated here.
Use the implement skill and stop at ready-for-merge, with the MR's risk score recorded. Follow repository instructions and read the issue's execution record.
Start with the listed reads, then read complete relevant definitions and callers and expand when correctness requires it. Ask the leader for a specific missing fact or scope change when dependencies extend beyond the assignment.
If a refusal or model fallback is reported, stop further task work, preserve changes and report the blocked operation, needed context, current branch/commit and unfinished work. Include the reported category and request ID when available; do not infer a cause or retry under a different model.
Start no other agents; the codex review that implement runs is part of the task.
Write no memory notes; put lasting findings in your final report or the issue's execution record.
Report: changed behavior, commit/MR, checks and evidence, remaining blockers and any observed model switch.
```

Replace placeholders before launch. Allocate a complete change: for a checkpoint
layout fix, include the serialization and loading contract, tensor dimensions,
sharding rules and compatibility tests that determine correctness. Point to the
relevant definitions and direct callers; include attention, replay or training
code when a dependency actually requires it. A small prompt is not a reason to
omit a necessary layout invariant or test.

The leader can summarize verified facts with their file/symbol sources. Avoid
attaching a whole architecture document, historical benchmark archive or prior
refusal conversation just because it is available. If broad investigation is
still needed, the leader does it before assigning the bounded implementation.
