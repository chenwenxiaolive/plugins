# Delegation brief

Use this brief for each worker, filled with facts checked by the launching
session and marking anything still unknown. Keep the real project, model,
hardware and purpose accurate; do not disguise them or omit facts needed for
correctness.

## Worker brief

```text
Role: independent Herdr worker, <selected model and reasoning effort>. You own this issue end to end and report to the user in this terminal, which they watch in Herdr. There is no coordinating session to report to or ask.
Goal: <one observable change and why it is needed>.
Done when: <behavioral acceptance criteria and independent expected results>.
Checkout: <worktree path for this issue>, already created on branch <branch>, based on and merging into <target>; issue <link> (or none).
Owned files: <existing files and exact new paths; no overlap with other workers>.
First reads: <file plus symbol or section for the implementation, direct caller and relevant test>.
Required facts: <interfaces, invariants, compatibility requirements and concise supporting evidence; name unknowns>.
Validation: <checks on committed code and their expected results>.
Execution: <authorized CPU location; or the user-named node and GPU allocation, plus any authorized remote-worktree setup>. No GPU work unless allocated here.
Delivery: use the implement skill for this issue alone: branch, validation, MR, review, and the merge its risk score allows. Report the MR link, commit SHA, check evidence and risk score when you are done; if the score leaves the merge to the user, say so instead of merging. For a page change, report visual acceptance apart from the functional checks: screenshot it as the preview skill describes, or give the user its preview link and say that visual acceptance is pending.
Follow repository instructions and read the issue's execution record when one exists.
Start with the listed reads, then read complete relevant definitions and callers and expand when correctness requires it. Decide open questions from the issue, this brief and existing authorization. When something still blocks you, keep the unblocked work moving and ask the user here, naming the decision, access or fact you need; they steer this terminal through Herdr.
If a safeguard or automatic model fallback is reported, preserve your changes and tell the user the reported category/request ID and actual model when available. The client's automatic fallback may continue this authorized task; the event alone does not require stopping. Report any remaining blocked operation, needed context, current branch/commit and unfinished work. Respect the refusal, do not infer its cause or repeatedly rephrase the blocked request, and attribute work to the model that did it.
Subagents: you may delegate scoped work to native subagents in this checkout, each with disjoint files from your assignment and its edits and evidence returned to you, making no Git mutations, no further agents and no memory notes. Wait for every local writer to finish before you commit, switch branches or integrate, and validate only a committed SHA in an unchanged checkout.
Do not start other independent workers, assign a subagent to another directory or worktree, take another working directory, or pick up another issue on your own when this one is done. The user's instructions in this terminal come first.
Write no memory notes; put lasting findings in your final report or the issue's execution record.
```

## Native subagents inside a worker's checkout

A worker may delegate scoped work to native subagents in its own working
directory and checkout. Each gets disjoint files within the worker's assignment,
the worker's checkout and branch, and the worker as parent. Append to such an
assignment:

```text
Stay in your parent's working directory/checkout; do not take another working directory or worktree, or enable native worktree isolation. Edit only your owned files and return the changes to the parent. Do not stage, commit, switch branches, integrate, push or create an MR; the parent owns Git mutations, delivery and review. Start no other agents and write no memory notes.
Propose the required checks. Run them only if the parent assigns a committed SHA after all local writers have finished; keep that checkout unchanged until validation finishes. Do not validate uncommitted edits.
Report: changed behavior and files, proposed checks or results with the tested SHA, remaining blockers and any observed model switch.
```

Work that needs another directory goes back to the user, who decides whether it
becomes its own worker.

## Scope and evidence

Replace placeholders before launch. Allocate a complete change: for a checkpoint
layout fix, include the serialization and loading contract, tensor dimensions,
sharding rules and compatibility tests that determine correctness. Point to the
relevant definitions and direct callers; include attention, replay or training
code when a dependency actually requires it. A small prompt is not a reason to
omit a necessary layout invariant or test.

Summarize verified facts with their file/symbol sources. Avoid attaching a whole
architecture document, historical benchmark archive or prior refusal conversation
just because it is available. If broad investigation is still needed, do it
before assigning the bounded implementation.

Keep full validation logs as artifacts, and have the worker report their paths
rather than their contents. Preserve the real test and model names and any
evidence needed for acceptance; summarizing output is not permission to skip
required checks.
