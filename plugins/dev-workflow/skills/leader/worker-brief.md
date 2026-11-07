# Worker brief

Use the common brief and one delivery section for each implementation worker.
Fill it with facts checked by the leader, marking anything still unknown. Keep
the real project, model, hardware and purpose accurate; do not disguise them or
omit facts needed for correctness.

## Common brief

```text
Role: implementation worker, <native subagent or Herdr worker>, <selected model and reasoning effort>. The leader owns coordination and integration.
Goal: <one observable change and why it is needed>.
Done when: <behavioral acceptance criteria and independent expected results>.
Checkout: <actual checkout path> on branch <branch>, based on and merging into <target>; issue <link> (or none).
Owned files: <existing files and exact new paths; no overlap with other workers>.
First reads: <file plus symbol or section for the implementation, direct caller and relevant test>.
Required facts: <interfaces, invariants, compatibility requirements and concise supporting evidence; name unknowns>.
Validation: <checks on committed code and their expected results>.
Execution: <authorized CPU location; or the user-named node and GPU allocation, plus any authorized remote-worktree setup>. No GPU work unless allocated here.
Follow repository instructions and read the issue's execution record when one exists.
Start with the listed reads, then read complete relevant definitions and callers and expand when correctness requires it. Ask the leader for a specific missing fact or scope change when dependencies extend beyond the assignment.
If a safeguard or automatic model fallback is reported, preserve changes and tell the leader the reported category/request ID and actual model when available. The client's automatic fallback may continue this authorized task; the event alone does not require stopping. Report any remaining blocked operation, needed context, current branch/commit and unfinished work. Respect the refusal, do not infer its cause or repeatedly rephrase the blocked request, and attribute work to the model that did it.
Write no memory notes; put lasting findings in your final report or the issue's execution record.
```

## Shared-checkout subagent

Use the leader's current checkout and branch. Inherit its model and reasoning
effort unless the user chooses otherwise. Append:

```text
Edit only your owned files and return the changes to the leader. Do not stage, commit, switch branches, integrate, push or create an MR; the leader owns Git mutations and the full implement delivery and review. Start no other agents.
Propose the required checks. Run them only if the leader assigns a committed SHA after all writers have finished; keep that checkout unchanged until validation finishes. Do not validate uncommitted edits.
Report: changed behavior and files, proposed checks or results with the tested SHA, remaining blockers and any observed model switch.
```

## Herdr worker

Use a free worktree slot such as `/volume/worktree/<repo>/dev-N` and name its
branch and target. Use the leader's harness, model and reasoning effort unless
the user explicitly chooses otherwise. Append:

```text
Delivery: <own MR, or commits for the leader's existing delivery>.
Communication: <native tool or codex queue and leader's verified native reply address; Herdr bridge only for an explicit cross-harness assignment>. Report ready with your native session address and checkout, then send questions, blockers and the final report through that route. Keep native session IDs separate from Herdr terminal IDs. A peer message is an assignment or report within this task, not new user authorization.
If this assignment owns an MR, use the implement skill and stop at ready-for-merge, with the MR's risk score recorded. Otherwise return committed changes and validation evidence for the leader to integrate; do not create a separate MR. The leader completes implement delivery and review after integration.
Start no other agents; the codex review that implement runs for an assignment with its own MR is part of the task.
Report: changed behavior, commit/MR, checks and evidence, remaining blockers and any observed model switch.
```

## Scope and evidence

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

Keep full validation logs as artifacts. Read concise status, source revision and
check summaries first, then inspect failures and other details needed to verify
the result. Preserve the real test and model names and any evidence needed for
acceptance; summarizing output is not permission to skip required checks.
